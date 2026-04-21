"""
Step definitions for feature ask_question

Every Given / When / Then step declared in the feature file has exactly one
matching function here. Steps delegate all work to ChatService
"""

from behave import given, when, then

from app.models.user_session import UserSession
from app.ai_stubs import StubAIProvider
from app.ai_provider import ChatService


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given('the AI provider is a stub that returns deterministic responses')
def step_use_stub_ai_provider(context):
    """Attach a deterministic stub so no live AI is called during the test."""
    context.ai_provider = StubAIProvider()


@given('the student "{email}" is registered and logged in')
def step_student_logged_in(context, email):
    """
    Create a UserSession that represents the logged-in student.
    The email is accepted as a parameter to keep scenarios readable, but the
    current domain model identifies sessions by auto-generated integer IDs,
    so the email is not stored.
    """
    session = UserSession()
    context.db_session.add(session)
    context.db_session.commit()
    context.session = session


@given('the student is on the chat interface')
def step_student_on_chat_interface(context):
    """
    Verify that a session already exists in the context.
    This step acts as a pre-condition guard; the actual UI is not modelled here.
    """
    assert context.session is not None, "A logged-in session must exist before reaching the chat interface"


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when('the student sends the message "{message_text}"')
def step_student_sends_message(context, message_text):
    """
    Route the message to the correct use-case handler:
      - Quiz prompts  → ChatService.handle_quiz_request
      - All other messages → ChatService.handle_question

    Both paths capture errors so Then steps can assert on them.
    """
    service = ChatService(context.db_session, context.ai_provider)

    # Quiz prompts are identified by the prefix used in the .feature files
    if message_text.startswith("Generate a quiz about"):
        try:
            context.quiz_result = service.handle_quiz_request(context.session, message_text)
            context.last_error = None
        except ValueError as exc:
            context.last_error = str(exc)
            context.quiz_result = None
        except Exception as exc:
            context.last_error = str(exc)
            context.quiz_result = None
    else:
        try:
            context.last_reply = service.handle_question(context.session, message_text)
            context.last_error = None
        except ValueError as exc:
            context.last_error = str(exc)
            context.last_reply = None
        except Exception as exc:
            context.last_error = str(exc)
            context.last_reply = None


@when('the student sends an empty message')
def step_student_sends_empty_message(context):
    """Delegate an empty string to ChatService to trigger the validation error."""
    service = ChatService(context.db_session, context.ai_provider)
    try:
        context.last_reply = service.handle_question(context.session, "")
        context.last_error = None
    except ValueError as exc:
        context.last_error = str(exc)
        context.last_reply = None


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------

@then('the student receives an explanation containing "{expected_fragment}"')
def step_receives_explanation_containing(context, expected_fragment):
    """Assert the bot reply contains the expected deterministic fragment."""
    assert context.last_reply is not None, f"Expected a reply but got an error: {context.last_error}"
    assert expected_fragment in context.last_reply, (
        f"Expected fragment '{expected_fragment}' not found in reply: '{context.last_reply}'"
    )


@then('the message appears in the conversation history')
def step_message_in_history(context):
    """Assert that at least one message was persisted to the session."""
    context.db_session.refresh(context.session)
    assert len(context.session.messages) > 0, "No messages were stored in the session"


@then('the student sees the error "{expected_error}"')
def step_student_sees_error(context, expected_error):
    """Assert the service raised an error with the expected message text."""
    assert context.last_error is not None, "Expected an error but the service succeeded"
    assert expected_error in context.last_error, (
        f"Expected error '{expected_error}' but got: '{context.last_error}'"
    )


@then('no message appears in the conversation history')
def step_no_message_in_history(context):
    """Assert that nothing was persisted to the session."""
    context.db_session.refresh(context.session)
    assert len(context.session.messages) == 0, (
        f"Expected empty history but found {len(context.session.messages)} message(s)"
    )
