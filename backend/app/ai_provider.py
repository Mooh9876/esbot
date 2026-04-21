"""
AI provider interface and the ChatService use-case handler.

The interface defines the contract that any AI backend must fulfill.
The ChatService delegates all AI-dependent work to an injected provider.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Data transfer objects shared between layers
# ---------------------------------------------------------------------------

@dataclass
class QuizItem:
    """A single question produced by the AI provider."""
    question: str
    correct_answer: str


@dataclass
class QuizResult:
    """Result returned by the AI provider for a quiz generation request."""
    items: List[QuizItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Abstract AI provider interface
# ---------------------------------------------------------------------------

class AIProvider(ABC):
    """
    Contract for any AI backend
    Implementations must be stateless and side-effect-free beyond returning data.
    """

    @abstractmethod
    def ask(self, question: str) -> str:
        """
        Generate a textual explanation for a course question.

        Returns the explanation as a plain string.
        Raises AIProviderError on unrecoverable failures.
        """

    @abstractmethod
    def generate_quiz(self, topic: str) -> QuizResult:
        """
        Generate quiz items for the given topic.

        Returns a QuizResult containing at least one QuizItem.
        Raises ValueError when the topic is empty or blank.
        Raises AIProviderError on unrecoverable failures.
        """


# ---------------------------------------------------------------------------
# Domain exception
# ---------------------------------------------------------------------------

class AIProviderError(RuntimeError):
    """Raised when the AI backend is unavailable or returns an error."""


# ---------------------------------------------------------------------------
# Application service (use-case handler)
# ---------------------------------------------------------------------------

class ChatService:
    """
    Coordinates user interaction with the AI provider and the database.
    """

    UNAVAILABLE_MSG = "AI service is currently unavailable. Please try again later."
    EMPTY_MSG_ERROR = "Message must not be empty"
    EMPTY_TOPIC_ERROR = "Quiz topic must not be empty"

    def __init__(self, db_session, ai_provider: AIProvider):
        self._db = db_session
        self._ai = ai_provider

    # ------------------------------------------------------------------
    # Ask a course question
    # ------------------------------------------------------------------

    def handle_question(self, session, message_text: str) -> str:
        """
        Validate the message, call the AI provider (with one automatic retry
        on a transient failure), persist both messages, and return the bot reply.

        Raises ValueError when message_text is empty.
        Raises AIProviderError when the AI backend is unavailable after the retry.
        """
        from app.models.message import Message

        if not message_text or not message_text.strip():
            raise ValueError(self.EMPTY_MSG_ERROR)

        # One automatic retry to handle transient AI service failures
        try:
            reply_text = self._ai.ask(message_text)
        except AIProviderError:
            reply_text = self._ai.ask(message_text)

        # Persist the user message and the bot reply
        user_msg = Message(content=message_text, role="user")
        bot_msg = Message(content=reply_text, role="bot")
        session.add_message(user_msg)
        session.add_message(bot_msg)
        self._db.add(session)
        self._db.commit()

        return reply_text

    # ------------------------------------------------------------------
    # Generate a quiz for a topic
    # ------------------------------------------------------------------

    def handle_quiz_request(self, session, prompt: str) -> QuizResult:
        """
        Parse the topic from the prompt, call the AI provider to generate
        quiz items, persist a QuizRequest entity, and return the result.

        Raises ValueError when the topic is blank.
        Raises AIProviderError when the AI backend is unavailable.
        """
        from app.models.quiz_request import QuizRequest as QuizRequestModel

        # Extract the topic from prompts of the form "Generate a quiz about X"
        topic = self._extract_topic(prompt)

        if not topic:
            raise ValueError(self.EMPTY_TOPIC_ERROR)

        try:
            result = self._ai.generate_quiz(topic)
        except AIProviderError:
            raise

        # Persist the quiz request linked to the current session
        qr = QuizRequestModel(topic=topic, difficulty="standard")
        session.add_quiz_request(qr)
        self._db.add(session)
        self._db.commit()

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_topic(prompt: str) -> str:
        """
        Strip the "Generate a quiz about " prefix and return the remainder.
        Returns an empty string when no topic follows the prefix.
        """
        prefix = "Generate a quiz about "
        if prompt.startswith(prefix):
            return prompt[len(prefix):].strip()
        return prompt.strip()
