from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True)
    is_correct = Column(Boolean, nullable=False)
    feedback = Column(Text, nullable=True)

    submitted_answer_id = Column(Integer, ForeignKey("submitted_answers.id"), nullable=False, unique=True, index=True)
    submitted_answer = relationship("SubmittedAnswer", back_populates="evaluation_result")

    def set_submitted_answer(self, submitted_answer):
        submitted_answer.evaluation_result = self
        self.submitted_answer = submitted_answer