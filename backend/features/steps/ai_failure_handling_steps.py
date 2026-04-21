"""
Step definitions for feature ai_failure_handling

Shared steps (student login, on-chat-interface guard, the generic
'sends the message' router, and the standard Then assertions) are already
registered by ask_question_steps.py.

This file only defines the Given steps that configure the AI provider
stubs specific to failure scenarios.
"""

from behave import given

from app.ai_stubs import FailingAIProvider, RetryAIProvider


# ---------------------------------------------------------------------------
# Given steps – feature-specific AI provider configurations
# ---------------------------------------------------------------------------

@given('the AI provider fails on the first call but succeeds on retry')
def step_use_retry_ai_provider(context):
    """
    Attach a stub that raises AIProviderError on the first call and returns
    a deterministic response on the second call.
    ChatService automatically performs one retry, so the scenario's
    happy-path Then steps will pass.
    """
    context.ai_provider = RetryAIProvider()


@given('the AI provider is unavailable')
def step_use_failing_ai_provider(context):
    """
    Attach a stub that always raises AIProviderError.
    ChatService will exhaust its single retry and propagate the error,
    allowing the 'student sees the error' Then step to assert on it.
    """
    context.ai_provider = FailingAIProvider()
