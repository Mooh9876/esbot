from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class QuizRequest(Base):
    __tablename__ = "quiz_requests"

    id = Column(Integer, primary_key=True)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=False, index=True)
    session = relationship("UserSession", back_populates="quiz_requests")

    quiz_items = relationship("QuizItem", back_populates="quiz_request", cascade="all, delete-orphan")

    def add_quiz_item(self, quiz_item):
        quiz_item.quiz_request = self
        self.quiz_items.append(quiz_item)