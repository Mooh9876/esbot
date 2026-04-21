"""
Step definitions for feature quiz_generation

Shared Given and When steps (AI provider setup, student login, chat interface,
and the generic 'sends the message' router) are registered by
ask_question_steps.py, which behave loads from the same steps/ directory.

This file only defines Then steps that are specific to quiz generation.
"""

from behave import then


# ---------------------------------------------------------------------------
# Then steps – quiz-specific assertions
# ---------------------------------------------------------------------------

@then('the student receives a quiz with at least {min_count:d} question')
def step_receives_quiz_with_min_questions(context, min_count):
    """Assert the quiz result contains at least the required number of items."""
    assert context.quiz_result is not None, (
        f"Expected a quiz result but got an error: {context.last_error}"
    )
    assert len(context.quiz_result.items) >= min_count, (
        f"Expected at least {min_count} question(s) but got {len(context.quiz_result.items)}"
    )


@then('the first question reads "{expected_question}"')
def step_first_question_text(context, expected_question):
    """Assert the first quiz item text matches the stub's deterministic output."""
    assert context.quiz_result is not None, "No quiz result available"
    first = context.quiz_result.items[0].question
    assert first == expected_question, (
        f"Expected first question '{expected_question}' but got '{first}'"
    )


@then('the quiz appears in the conversation history')
def step_quiz_in_history(context):
    """Assert that a QuizRequest was persisted and linked to the current session."""
    context.db_session.refresh(context.session)
    assert len(context.session.quiz_requests) > 0, (
        "No quiz requests were stored in the session"
    )
