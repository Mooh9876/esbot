import pytest
from sqlalchemy.exc import IntegrityError

from app.models.quiz_item import QuizItem
from app.models.quiz_request import QuizRequest
from app.models.submitted_answer import SubmittedAnswer
from app.models.user_session import UserSession


class TestQuizItemCreation:

    def test_create_with_valid_data(self):
        item = QuizItem(question="What is Python?", correct_answer="A programming language")
        assert item.question == "What is Python?"
        assert item.correct_answer == "A programming language"
        assert item.id is None

    def test_id_assigned_after_flush(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()
        assert item.id is not None
        assert isinstance(item.id, int)

    def test_submitted_answers_initially_empty(self):
        item = QuizItem(question="Question?", correct_answer="Answer")
        assert item.submitted_answers == []


class TestQuizItemValidation:

    def test_null_question_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question=None, correct_answer="Answer")
        qr.add_quiz_item(item)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_correct_answer_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer=None)
        qr.add_quiz_item(item)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_quiz_request_id_raises(self, db_session):
        item = QuizItem(question="Question?", correct_answer="Answer")
        db_session.add(item)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestQuizItemRelationship:

    def test_quiz_request_backref(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        assert item.quiz_request is qr
        assert item.quiz_request_id == qr.id

    def test_item_appears_in_quiz_request(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        assert item in qr.quiz_items

    def test_add_submitted_answer_bidirectional(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        db_session.add(session)
        db_session.flush()

        assert answer in item.submitted_answers
        assert answer.quiz_item is item

    def test_cascade_delete_removes_submitted_answers(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        db_session.add(session)
        db_session.flush()

        answer_id = answer.id
        db_session.delete(item)
        db_session.flush()

        assert db_session.get(SubmittedAnswer, answer_id) is None


class TestQuizItemHelpers:

    def test_add_submitted_answer_appends_to_list(self):
        item = QuizItem(question="Question?", correct_answer="Answer")
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        assert answer in item.submitted_answers

    def test_add_submitted_answer_sets_item_reference(self):
        item = QuizItem(question="Question?", correct_answer="Answer")
        answer = SubmittedAnswer(answer="My answer")
        item.add_submitted_answer(answer)
        assert answer.quiz_item is item


class TestQuizItemBoundaryValues:
    # Analysis for QuizItem model fields:
    #
    # question field
    #   valid class:   any non-empty string (e.g. "What is Python?")
    #   invalid class: None -> IntegrityError
    #   boundary:      empty string "" -> accepted by DB (not NULL)
    #
    # correct_answer field
    #   same structure as question
    #   valid class:   any non-empty string
    #   invalid class: None -> IntegrityError
    #   boundary:      empty string "" -> accepted by DB (not NULL)
    #
    # submitted_answers relationship
    #   boundary: 0 answers (default), 1 answer, many answers (n=3 tested)
    #
    # gap found: both fields have no minimum length or content check at DB level.
    #            An empty question or answer passes without any error.

    def test_empty_question_accepted_by_db(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="", correct_answer="Answer")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()
        assert item.question == ""

    def test_empty_correct_answer_accepted_by_db(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()
        assert item.correct_answer == ""

    def test_multiple_submitted_answers_for_one_item(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Question?", correct_answer="Answer")
        qr.add_quiz_item(item)
        for i in range(3):
            item.add_submitted_answer(SubmittedAnswer(answer=f"Answer {i}"))
        db_session.add(session)
        db_session.flush()
        # expire forces a reload from the DB since add_submitted_answer appends twice in-memory
        db_session.expire(item)
        assert len(item.submitted_answers) == 3
