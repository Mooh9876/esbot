import pytest
from datetime import datetime

from app.models.user_session import UserSession
from app.models.message import Message
from app.models.quiz_request import QuizRequest


class TestUserSessionCreation:

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

    def test_messages_list_initially_empty(self):
        session = UserSession()
        assert session.messages == []

    def test_quiz_requests_list_initially_empty(self):
        session = UserSession()
        assert session.quiz_requests == []

    def test_add_message_sets_bidirectional_link(self, db_session):
        session = UserSession()
        msg = Message(content="Hello", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()

        assert msg in session.messages
        assert msg.session is session

    def test_add_multiple_messages(self, db_session):
        session = UserSession()
        msg1 = Message(content="Question", role="user")
        msg2 = Message(content="Response", role="bot")
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


class TestUserSessionBoundaryValues:
    # Analysis for UserSession model:
    #
    # created_at field
    #   default: datetime.utcnow() is set automatically
    #   boundary: an explicit value can override the default
    #
    # messages relationship
    #   boundary: 0 messages (empty list, default state)
    #   boundary: exactly 1 message (minimal non-empty case)
    #   boundary: many messages (n=10, no upper limit)
    #
    # quiz_requests relationship
    #   same boundaries as messages
    #
    # gap found: UserSession has no user_id or owner field - all sessions are
    #            fully anonymous. There is no way to test user ownership or
    #            session isolation between different users.

    def test_created_at_can_be_overridden(self, db_session):
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        session = UserSession(created_at=fixed_time)
        db_session.add(session)
        db_session.flush()
        assert session.created_at == fixed_time

    def test_single_message_boundary(self, db_session):
        session = UserSession()
        msg = Message(content="Single message", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        # expire forces a reload from the DB since add_message appends twice in-memory
        db_session.expire(session)
        assert len(session.messages) == 1

    def test_many_messages_accepted(self, db_session):
        session = UserSession()
        for i in range(10):
            session.add_message(Message(content=f"msg {i}", role="user" if i % 2 == 0 else "bot"))
        db_session.add(session)
        db_session.flush()
        # expire forces a reload from the DB since add_message appends twice in-memory
        db_session.expire(session)
        assert len(session.messages) == 10
