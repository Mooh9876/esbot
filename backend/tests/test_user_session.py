import pytest
from datetime import datetime

from app.models.user_session import UserSession
from app.models.message import Message
from app.models.quiz_request import QuizRequest


class TestUserSessionCreation:
    """Prüft, ob ein UserSession-Objekt korrekt erstellt werden kann."""

    def test_create_with_defaults(self):
        session = UserSession()
        assert session.id is None
        assert session.messages == []
        assert session.quiz_requests == []

    def test_created_at_default(self, db_session):
        session = UserSession()
        db_session.add(session)
        db_session.flush()
        assert session.created_at is not None
        assert isinstance(session.created_at, datetime)

    def test_id_assigned_after_flush(self, db_session):
        session = UserSession()
        db_session.add(session)
        db_session.flush()
        assert session.id is not None
        assert isinstance(session.id, int)


class TestUserSessionRelationships:
    """Prüft bidirektionale Beziehungen zu Message und QuizRequest."""

    def test_messages_list_initially_empty(self):
        session = UserSession()
        assert session.messages == []

    def test_quiz_requests_list_initially_empty(self):
        session = UserSession()
        assert session.quiz_requests == []

    def test_add_message_sets_bidirectional_link(self, db_session):
        session = UserSession()
        msg = Message(content="Hallo", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()

        assert msg in session.messages
        assert msg.session is session

    def test_add_multiple_messages(self, db_session):
        session = UserSession()
        msg1 = Message(content="Frage", role="user")
        msg2 = Message(content="Antwort", role="bot")
        msg1.session = session
        msg2.session = session
        db_session.add(session)
        db_session.flush()

        assert len(session.messages) == 2
        assert msg1 in session.messages
        assert msg2 in session.messages

    def test_add_quiz_request_sets_bidirectional_link(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()

        assert qr in session.quiz_requests
        assert qr.session is session

    def test_add_multiple_quiz_requests(self, db_session):
        session = UserSession()
        qr1 = QuizRequest(topic="Python", difficulty="easy")
        qr2 = QuizRequest(topic="SQL", difficulty="hard")
        qr1.session = session
        qr2.session = session
        db_session.add(session)
        db_session.flush()

        assert len(session.quiz_requests) == 2

    def test_cascade_delete_removes_messages(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()

        msg_id = msg.id
        db_session.delete(session)
        db_session.flush()

        assert db_session.get(Message, msg_id) is None

    def test_cascade_delete_removes_quiz_requests(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        db_session.add(session)
        db_session.flush()

        qr_id = qr.id
        db_session.delete(session)
        db_session.flush()

        assert db_session.get(QuizRequest, qr_id) is None


class TestUserSessionHelpers:
    """Prüft die Helper-Methoden add_message und add_quiz_request."""

    def test_add_message_appends_to_list(self):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        assert msg in session.messages

    def test_add_message_sets_session_reference(self):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        assert msg.session is session

    def test_add_quiz_request_appends_to_list(self):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        assert qr in session.quiz_requests

    def test_add_quiz_request_sets_session_reference(self):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        assert qr.session is session
