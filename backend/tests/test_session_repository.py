import pytest

from app.repositories.session_repository import SessionRepository
from app.models.user_session import UserSession
from app.models.message import Message
from app.models.quiz_request import QuizRequest

# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------

def create_session_with_data():
    session = UserSession()
    return session

# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestSessionRepository:
    def test_create_session(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)

        db_session.flush()

        assert session.id is not None

    def test_get_by_id(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)
        db_session.flush()

        found = repo.get_by_id(session.id)

        assert found is session 

    def test_get_all_sessions(self, db_session):
        repo = SessionRepository(db_session)

        s1 = UserSession()
        s2 = UserSession()

        repo.create_session(s1)
        repo.create_session(s2)

        db_session.flush()

        all_sessions = repo.get_all_sessions()

        assert len(all_sessions) >= 2

    def test_add_message(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)

        msg = Message(content="Hello", role="user")
        repo.add_message(session, msg)

        db_session.flush()
        db_session.expire_all()

        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"

    def test_get_messages(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)

        repo.add_message(session, Message(content="A", role="user"))
        repo.add_message(session, Message(content="B", role="bot"))

        db_session.flush()
        db_session.expire_all()

        messages = repo.get_messages(session)

        assert len(messages) == 2

    def test_update_session(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)

        updated = repo.update_session(session)

        assert updated is session

    def test_delete_session(self, db_session):
        repo = SessionRepository(db_session)

        session = UserSession()
        repo.create_session(session)
        db_session.flush()

        session_id = session.id

        repo.delete_session(session)
        db_session.flush()

        assert db_session.get(UserSession, session_id) is None

    def test_cascade_delete_messages(self, db_session):
        repo = SessionRepository(db_session)
        
        session = UserSession()
        repo.create_session(session)

        msg = Message(content="test", role="user")
        repo.add_message(session, msg)

        db_session.flush()

        msg_id = msg.id

        repo.delete_session(session)
        db_session.flush()

        assert db_session.get(Message, msg_id) is None