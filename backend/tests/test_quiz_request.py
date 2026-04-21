import pytest
from sqlalchemy.exc import IntegrityError

from app.models.quiz_request import QuizRequest
from app.models.quiz_item import QuizItem
from app.models.user_session import UserSession


class TestQuizRequestCreation:
    """Prüft, ob ein QuizRequest-Objekt korrekt erstellt werden kann."""

    def test_create_with_valid_data(self):
        qr = QuizRequest(topic="Python Basics", difficulty="easy")
        assert qr.topic == "Python Basics"
        assert qr.difficulty == "easy"
        assert qr.id is None

    def test_created_at_default(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="SQL", difficulty="hard")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()
        assert qr.created_at is not None

    def test_id_assigned_after_flush(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="SQL", difficulty="medium")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()
        assert qr.id is not None
        assert isinstance(qr.id, int)

    def test_quiz_items_initially_empty(self):
        qr = QuizRequest(topic="Python", difficulty="easy")
        assert qr.quiz_items == []


class TestQuizRequestValidation:
    """Prüft, dass fehlende Pflichtfelder beim Flush einen Fehler auslösen."""

    def test_null_topic_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic=None, difficulty="easy")
        session.add_quiz_request(qr)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_difficulty_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty=None)
        session.add_quiz_request(qr)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_session_id_raises(self, db_session):
        qr = QuizRequest(topic="Python", difficulty="easy")
        db_session.add(qr)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestQuizRequestRelationship:
    """Prüft die bidirektionalen Beziehungen von QuizRequest."""

    def test_session_backref(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()

        assert qr.session is session
        assert qr.session_id == session.id

    def test_quiz_request_appears_in_session(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()

        assert qr in session.quiz_requests

    def test_add_quiz_item_bidirectional(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Was ist eine Liste?", correct_answer="Ein Datentyp")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        assert item in qr.quiz_items
        assert item.quiz_request is qr

    def test_cascade_delete_removes_quiz_items(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        item_id = item.id
        db_session.delete(qr)
        db_session.flush()

        assert db_session.get(QuizItem, item_id) is None


class TestQuizRequestHelpers:
    """Prüft die Helper-Methode add_quiz_item."""

    def test_add_quiz_item_appends_to_list(self):
        qr = QuizRequest(topic="Python", difficulty="easy")
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        assert item in qr.quiz_items

    def test_add_quiz_item_sets_request_reference(self):
        qr = QuizRequest(topic="Python", difficulty="easy")
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        assert item.quiz_request is qr
