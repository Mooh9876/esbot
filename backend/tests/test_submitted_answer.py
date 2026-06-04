import pytest
from sqlalchemy.exc import IntegrityError

from app.models.submitted_answer import SubmittedAnswer
from app.models.evaluation_result import EvaluationResult
from app.models.quiz_item import QuizItem
from app.models.quiz_request import QuizRequest
from app.models.user_session import UserSession


def _create_quiz_item(db_session):
    # helper: builds the full parent chain so we have a saved QuizItem to work with
    session = UserSession()
    qr = QuizRequest(topic="Python", difficulty="easy")
    session.add_quiz_request(qr)
    item = QuizItem(question="Question?", correct_answer="Answer")
    qr.add_quiz_item(item)
    db_session.add(session)
    db_session.flush()
    return item


class TestSubmittedAnswerCreation:

    def test_create_with_valid_data(self):
        answer = SubmittedAnswer(answer="My answer")
        assert answer.answer == "My answer"
        assert answer.id is None

    def test_id_assigned_after_flush(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        db_session.flush()
        assert answer.id is not None
        assert isinstance(answer.id, int)

    def test_evaluation_result_initially_none(self):
        answer = SubmittedAnswer(answer="My answer")
        assert answer.evaluation_result is None


class TestSubmittedAnswerValidation:

    def test_null_answer_raises(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer=None)
        item.add_submitted_answer(answer)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_quiz_item_id_raises(self, db_session):
        answer = SubmittedAnswer(answer="My answer")
        db_session.add(answer)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestSubmittedAnswerRelationship:

    def test_quiz_item_backref(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        db_session.flush()

        assert answer.quiz_item is item
        assert answer.quiz_item_id == item.id

    def test_answer_appears_in_quiz_item(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        db_session.flush()

        assert answer in item.submitted_answers

    def test_set_evaluation_bidirectional(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        evaluation = EvaluationResult(is_correct=True, feedback="Correct!")
        answer.set_evaluation(evaluation)
        db_session.add(evaluation)
        db_session.flush()

        assert answer.evaluation_result is evaluation
        assert evaluation.submitted_answer is answer

    def test_cascade_delete_removes_evaluation(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        evaluation = EvaluationResult(is_correct=False, feedback="Wrong")
        answer.set_evaluation(evaluation)
        db_session.add(evaluation)
        db_session.flush()

        eval_id = evaluation.id
        db_session.delete(answer)
        db_session.flush()

        assert db_session.get(EvaluationResult, eval_id) is None


class TestSubmittedAnswerHelpers:

    def test_set_evaluation_sets_result(self):
        answer = SubmittedAnswer(answer="My answer")
        evaluation = EvaluationResult(is_correct=True, feedback="Correct!")
        answer.set_evaluation(evaluation)
        assert answer.evaluation_result is evaluation

    def test_set_evaluation_sets_back_reference(self):
        answer = SubmittedAnswer(answer="My answer")
        evaluation = EvaluationResult(is_correct=True, feedback="Correct!")
        answer.set_evaluation(evaluation)
        assert evaluation.submitted_answer is answer


class TestSubmittedAnswerBoundaryValues:
    # Analysis for SubmittedAnswer model:
    #
    # answer field
    #   valid class:   any non-empty string (e.g. "A programming language")
    #   invalid class: None -> IntegrityError (NOT NULL)
    #   boundary:      empty string "" -> accepted by DB (not NULL)
    #   boundary:      very long string (5000 chars) -> no upper limit on String columns
    #
    # gap found: an empty answer string passes the DB constraint.
    #            semantically it makes no sense - this should be caught in the service layer.

    def test_empty_answer_accepted_by_db(self, db_session):
        item = _create_quiz_item(db_session)
        answer = SubmittedAnswer(answer="")
        item.add_submitted_answer(answer)
        db_session.flush()
        assert answer.answer == ""

    def test_very_long_answer_accepted(self, db_session):
        item = _create_quiz_item(db_session)
        long_answer = "B" * 5_000
        answer = SubmittedAnswer(answer=long_answer)
        item.add_submitted_answer(answer)
        db_session.flush()
        assert len(answer.answer) == 5_000
