import pytest
from sqlalchemy.exc import IntegrityError

from app.models.evaluation_result import EvaluationResult
from app.models.submitted_answer import SubmittedAnswer
from app.models.quiz_item import QuizItem
from app.models.quiz_request import QuizRequest
from app.models.user_session import UserSession


def _create_submitted_answer(db_session):
    """Erstellt die notwendige Eltern-Hierarchie und gibt eine persistierte SubmittedAnswer zurück."""
    session = UserSession()
    qr = QuizRequest(topic="Python", difficulty="easy")
    session.add_quiz_request(qr)
    item = QuizItem(question="Frage?", correct_answer="Antwort")
    qr.add_quiz_item(item)
    answer = SubmittedAnswer(answer="Meine Antwort")
    item.add_submitted_answer(answer)
    db_session.add(session)
    db_session.flush()
    return answer


class TestEvaluationResultCreation:
    """Prüft, ob ein EvaluationResult-Objekt korrekt erstellt werden kann."""

    def test_create_with_valid_data(self):
        ev = EvaluationResult(is_correct=True, feedback="Richtig!")
        assert ev.is_correct is True
        assert ev.feedback == "Richtig!"
        assert ev.id is None

    def test_create_with_false_result(self):
        ev = EvaluationResult(is_correct=False, feedback="Leider falsch.")
        assert ev.is_correct is False

    def test_feedback_can_be_none(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev = EvaluationResult(is_correct=True, feedback=None)
        answer.set_evaluation(ev)
        db_session.add(ev)
        db_session.flush()
        assert ev.feedback is None
        assert ev.id is not None

    def test_id_assigned_after_flush(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev = EvaluationResult(is_correct=True, feedback="Korrekt")
        answer.set_evaluation(ev)
        db_session.add(ev)
        db_session.flush()
        assert ev.id is not None
        assert isinstance(ev.id, int)


class TestEvaluationResultValidation:
    """Prüft, dass fehlende Pflichtfelder beim Flush einen Fehler auslösen."""

    def test_null_is_correct_raises(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev = EvaluationResult(is_correct=None, feedback="text")
        answer.set_evaluation(ev)
        db_session.add(ev)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_submitted_answer_id_raises(self, db_session):
        ev = EvaluationResult(is_correct=True, feedback="Richtig")
        db_session.add(ev)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestEvaluationResultRelationship:
    """Prüft die bidirektionale 1:1-Beziehung zu SubmittedAnswer."""

    def test_submitted_answer_backref(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev = EvaluationResult(is_correct=True, feedback="Richtig")
        answer.set_evaluation(ev)
        db_session.add(ev)
        db_session.flush()

        assert ev.submitted_answer is answer
        assert ev.submitted_answer_id == answer.id

    def test_evaluation_appears_on_answer(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev = EvaluationResult(is_correct=True, feedback="Richtig")
        answer.set_evaluation(ev)
        db_session.add(ev)
        db_session.flush()

        assert answer.evaluation_result is ev

    def test_one_to_one_unique_constraint(self, db_session):
        answer = _create_submitted_answer(db_session)
        ev1 = EvaluationResult(is_correct=True, feedback="Erste Bewertung")
        answer.set_evaluation(ev1)
        db_session.add(ev1)
        db_session.flush()

        ev2 = EvaluationResult(
            is_correct=False,
            feedback="Zweite Bewertung",
            submitted_answer_id=answer.id,
        )
        db_session.add(ev2)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestEvaluationResultHelpers:
    """Prüft die Helper-Methode set_submitted_answer."""

    def test_set_submitted_answer_links_both_sides(self):
        answer = SubmittedAnswer(answer="Meine Antwort")
        ev = EvaluationResult(is_correct=True, feedback="Richtig")
        ev.set_submitted_answer(answer)
        assert ev.submitted_answer is answer
        assert answer.evaluation_result is ev
