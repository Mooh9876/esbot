import pytest
from sqlalchemy.exc import IntegrityError

from app.models.message import Message
from app.models.user_session import UserSession


class TestMessageCreation:

    def test_create_with_valid_data(self):
        msg = Message(content="Hello World", role="user")
        assert msg.content == "Hello World"
        assert msg.role == "user"
        assert msg.id is None

    def test_role_can_be_bot(self):
        msg = Message(content="Response", role="bot")
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

    def test_set_session_links_to_session(self):
        session = UserSession()
        msg = Message(content="test", role="user")
        msg.set_session(session)
        assert msg.session is session


class TestMessageBoundaryValues:
    # Analysis for Message model fields:
    #
    # content field
    #   valid class:   any non-empty string (e.g. "Hello")
    #   invalid class: None -> IntegrityError (NOT NULL constraint)
    #   boundary:      empty string "" -> accepted by DB (not NULL), but semantically wrong
    #   boundary:      very long string -> no length limit on Text columns, so no upper bound
    #
    # role field
    #   valid classes: "user", "bot"
    #   invalid class: None -> IntegrityError
    #   boundary:      empty string "" -> accepted (not NULL)
    #   gap found:     role is a plain string column with no Enum constraint.
    #                  Values like "admin" are stored without error.
    #                  Validation needs to be done in the service layer.

    def test_empty_content_accepted_by_db(self, db_session):
        # empty string is not NULL, passes the NOT NULL check
        session = UserSession()
        msg = Message(content="", role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert msg.content == ""

    def test_empty_role_accepted_by_db(self, db_session):
        session = UserSession()
        msg = Message(content="test", role="")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert msg.role == ""

    def test_invalid_role_value_accepted_by_db(self, db_session):
        # no enum constraint on the column, so "admin" is saved without any error
        session = UserSession()
        msg = Message(content="test", role="admin")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert msg.role == "admin"

    def test_very_long_content_accepted(self, db_session):
        session = UserSession()
        long_content = "A" * 10_000
        msg = Message(content=long_content, role="user")
        session.add_message(msg)
        db_session.add(session)
        db_session.flush()
        assert len(msg.content) == 10_000
