from app.models.user_session import UserSession
from app.models.message import Message

class SessionRepository:
    """
    Repository layer for UserSession persistence operations
    """

    def __init__(self, db_session):
        self.db = db_session

    # --------------------------------------------------------------
    # Create
    # --------------------------------------------------------------

    def create_session(self, session: UserSession):
        self.db.add(session)
        self.db.commit()
        return session
    
    # --------------------------------------------------------------
    # Read
    # --------------------------------------------------------------

    def get_by_id(self, session_id: int):
        return self.db.get(UserSession, session_id)
    
    def get_all_sessions(self):
        return self.db.query(UserSession).all()
    
    # --------------------------------------------------------------
    # Messages
    # --------------------------------------------------------------

    def add_message(self, session: UserSession, message: Message):
        session.add_message(message)
        self.db.add(session)
        self.db.commit()

    def get_messages(self, session: UserSession):
        return session.messages
    
    # --------------------------------------------------------------
    # Update
    # --------------------------------------------------------------

    def update_session(self, session: UserSession):
        self.db.add(session)
        self.db.commit()
        return session
    
    # --------------------------------------------------------------
    # Delete
    # --------------------------------------------------------------

    def delete_session(self, session: UserSession):
        self.db.delete(session)
        self.db.commit()