from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SubmittedAnswer(Base):
    __tablename__ = "submitted_answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)

    quiz_item_id = Column(Integer, ForeignKey("quiz_items.id"), nullable=False)
    quiz_item = relationship("QuizItem", back_populates="submitted_answers")

    evaluation_result = relationship(
        "EvaluationResult",
        back_populates="submitted_answer",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def set_evaluation(self, evaluation):
        evaluation.submitted_answer = self
        self.evaluation_result = evaluation