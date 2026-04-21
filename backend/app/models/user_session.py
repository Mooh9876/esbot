from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    quiz_requests = relationship("QuizRequest", back_populates="session", cascade="all, delete-orphan")

    def add_message(self, message):
        message.session = self
        self.messages.append(message)

    def add_quiz_request(self, quiz_request):
        quiz_request.session = self
        self.quiz_requests.append(quiz_request)