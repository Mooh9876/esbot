import pytest
from sqlalchemy.exc import IntegrityError

from app.models.message import Message
from app.models.user_session import UserSession


class TestMessageCreation:
    """Prüft, ob ein Message-Objekt korrekt erstellt werden kann."""

    def test_create_with_valid_data(self):
        msg = Message(content="Hallo Welt", role="user")
        assert msg.content == "Hallo Welt"
        assert msg.role == "user"
        assert msg.id is None

    def test_role_can_be_bot(self):
        msg = Message(content="Antwort", role="bot")
        assert msg.role == "bot"

    def test_created_at_default(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert msg.created_at is not None

    def test_id_assigned_after_flush(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert msg.id is not None
        assert isinstance(msg.id, int)


class TestMessageValidation:
    """Prüft, dass fehlende Pflichtfelder beim Flush einen Fehler auslösen."""

    def test_null_content_raises(self, db_session):
        session = UserSession()
        msg = Message(content=None, role="user")
        session.add_message(msg)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_role_raises(self, db_session):
        session = UserSession()
        msg = Message(content="test", role=None)
        session.add_message(msg)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_session_id_raises(self, db_session):
        msg = Message(content="test", role="user")
        db_session.add(msg)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestMessageRelationship:
    """Prüft die bidirektionale Beziehung zwischen Message und UserSession."""

    def test_session_backref(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()

        assert msg.session is session
        assert msg.session_id == session.id

    def test_message_appears_in_session_messages(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()

        assert msg in session.messages


class TestMessageHelpers:
    """Prüft die Helper-Methode set_session."""

    def test_set_session_links_to_session(self):
        session = UserSession()
        msg = Message(content="test", role="user")
        msg.set_session(session)
        assert msg.session is session
