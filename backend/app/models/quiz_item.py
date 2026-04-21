from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class QuizItem(Base):
    __tablename__ = "quiz_items"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)

    quiz_request_id = Column(Integer, ForeignKey("quiz_requests.id"), nullable=False, index=True)
    quiz_request = relationship("QuizRequest", back_populates="quiz_items")

    submitted_answers = relationship("SubmittedAnswer", back_populates="quiz_item", cascade="all, delete-orphan")

    def add_submitted_answer(self, submitted_answer):
        submitted_answer.quiz_item = self
        self.submitted_answers.append(submitted_answer)