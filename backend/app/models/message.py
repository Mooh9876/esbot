from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # "user" oder "bot"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=False, index=True)
    session = relationship("UserSession", back_populates="messages")

    def set_session(self, session):
        self.session = session