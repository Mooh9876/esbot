"""
Stub / mock implementations of AIProvider for use in BDD acceptance tests.

All stubs are deterministic they return hard-coded values that exactly
match the expected output strings declared in the .feature files.
No live model or network call is ever made during test execution.
"""

from app.ai_provider import AIProvider, AIProviderError, QuizItem, QuizResult


class StubAIProvider(AIProvider):
    """
    Default stub: always succeeds and returns the responses that the
    .feature files expect.
    """

    # Canned response for the "ask a question" feature
    ASK_RESPONSE = (
        "Unit tests verify individual components in isolation"
    )

    # Canned response for the AI-failure happy-path (retry succeeds)
    POLYMORPHISM_RESPONSE = (
        "Polymorphism allows objects of different types to be treated uniformly"
    )

    def ask(self, question: str) -> str:
        """Return a deterministic explanation regardless of the actual question."""
        if "polymorphism" in question.lower():
            return self.POLYMORPHISM_RESPONSE
        return self.ASK_RESPONSE

    def generate_quiz(self, topic: str) -> QuizResult:
        """Return a deterministic quiz item regardless of the actual topic."""
        return QuizResult(
            items=[
                QuizItem(
                    question="What does TDD stand for?",
                    correct_answer="Test-Driven Development",
                )
            ]
        )


class FailingAIProvider(AIProvider):
    """
    Stub that always raises AIProviderError.
    Used for the 'AI service is completely unavailable' error scenario.
    """

    def ask(self, question: str) -> str:
        raise AIProviderError("AI service is currently unavailable. Please try again later.")

    def generate_quiz(self, topic: str) -> QuizResult:
        raise AIProviderError("AI service is currently unavailable. Please try again later.")


class RetryAIProvider(AIProvider):
    """
    Stub that fails on the first call and succeeds on subsequent calls.
    Simulates a transient AI service outage that resolves after one retry.
    """

    def __init__(self):
        self._call_count = 0

    def ask(self, question: str) -> str:
        self._call_count += 1
        if self._call_count == 1:
            # Simulate a transient failure on the first attempt
            raise AIProviderError("Transient failure – retrying")
        # Second attempt returns the expected deterministic response
        return StubAIProvider.POLYMORPHISM_RESPONSE

    def generate_quiz(self, topic: str) -> QuizResult:
        self._call_count += 1
        if self._call_count == 1:
            raise AIProviderError("Transient failure – retrying")
        return StubAIProvider().generate_quiz(topic)
