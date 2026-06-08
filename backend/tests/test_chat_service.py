import pytest
from unittest.mock import MagicMock, Mock
from sqlalchemy.exc import IntegrityError
from app.ai_provider import ChatService, AIProviderError, QuizResult

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class DummySession:
    """Simulates a SQLAlchemy session in a lightweight way."""
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

class DummyUserSession:
    """Mocks the domain session (UserSession)"""

    def __init__(self):
        self.messages = []
        self.quiz_request = []

    def add_message(self, msg):
        self.messages.append(msg)

    def add_quiz_request(self, qr):
        self.quiz_request.append(qr)

# ------------------------------------------------------------------
# Test: handle_question (message flow)
# ------------------------------------------------------------------

def test_handle_question_success():
    db = DummySession()
    ai = Mock()

    ai.ask.return_value = "AI Response"

    service = ChatService(db, ai)
    session = DummyUserSession()

    result = service.handle_question(session, "Hello")

    assert result == "AI Response"
    assert len(session.messages) == 2 # user + bot
    assert db.committed is True
    ai.ask_assert_called_once_with("Hello")

# ------------------------------------------------------------------
# Test: empty message validation
# ------------------------------------------------------------------

def test_handle_question_empty_message():
    db = DummySession()
    ai = Mock()

    service = ChatService(db, ai)
    session = DummyUserSession()

    with pytest.raises(ValueError):
        service.handle_question(session, "")

# ------------------------------------------------------------------
# Test: retry logic works
# ------------------------------------------------------------------

def test_handle_question_retry_success():
    db = DummySession()
    ai = Mock()

    ai.ask.side_effect = [AIProviderError("fail"), "Recovered"]

    service = ChatService(db, ai)
    session = DummyUserSession()

    result = service.handle_question(session, "Hi")

    assert result == "Recovered"
    assert ai.ask.call_count == 2

# ------------------------------------------------------------------
# Test: AI fails twice (no recovery)
# ------------------------------------------------------------------

def test_handle_question_ai_failure():
    db = DummySession()
    ai = Mock()

    ai.ask.side_effect = AIProviderError("fail")

    service = ChatService(db, ai)
    session = DummyUserSession()

    with pytest.raises(AIProviderError):
        service.handle_question(session, "Hi")

# ------------------------------------------------------------------
# Test: quiz generation success
# ------------------------------------------------------------------

def test_handle_quiz_success():
    db = DummySession()
    ai = Mock()

    ai.generate_quiz.return_value = QuizResult(items=[])

    service = ChatService(db, ai)
    session = DummyUserSession()

    result = service.handle_quiz_request(session, "Generate a quiz about Python")

    assert isinstance(result, QuizResult)
    assert len(session.quiz_request) == 1
    assert db.committed is True
    ai.generate_quiz.assert_called_once_with("Python")

# ------------------------------------------------------------------
# Test: empty quiz topic
# ------------------------------------------------------------------

def test_handle_quiz_empty_topic():
    db = DummySession()
    ai = Mock()

    service = ChatService(db, ai)
    session = DummyUserSession()

    with pytest.raises(ValueError):
        service.handle_quiz_request(session, "Generate a quiz about ")

# ------------------------------------------------------------------
# Test: start session
# ------------------------------------------------------------------

def test_start_session():
    db = DummySession()
    ai = Mock()

    service = ChatService(db, ai)
    session = DummyUserSession()

    result = service.start_session(session)

    assert result is session
    assert db.committed is True
    assert session in db.added

# ------------------------------------------------------------------
# Test: evaluate answer success
# ------------------------------------------------------------------

def test_evaluate_answer_success():
    db = DummySession()
    ai = Mock()

    ai.ask.return_value = "Correct explanation"

    service = ChatService(db, ai)

    result = service.evaluate_answer(
        question="What is Python?",
        answer="A programming language"
    )

    assert result == "Correct explanation"
    ai.ask.assert_called_once()

# ------------------------------------------------------------------
# Test: evaluate answer AI failure
# ------------------------------------------------------------------

def test_evaluate_answer_failure():
    db = DummySession()
    ai = Mock()

    ai.ask.side_effect = AIProviderError()

    service = ChatService(db, ai)

    result = service.evaluate_answer(
        question="Q",
        answer="A"
    )

    assert result == service.UNAVAILABLE_MSG
