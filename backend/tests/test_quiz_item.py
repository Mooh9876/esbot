import pytest
from sqlalchemy.exc import IntegrityError

from app.models.quiz_item import QuizItem
from app.models.quiz_request import QuizRequest
from app.models.submitted_answer import SubmittedAnswer
from app.models.user_session import UserSession


class TestQuizItemCreation:
    """Prüft, ob ein QuizItem-Objekt korrekt erstellt werden kann."""

    def test_create_with_valid_data(self):
        item = QuizItem(question="Was ist Python?", correct_answer="Eine Programmiersprache")
        assert item.question == "Was ist Python?"
        assert item.correct_answer == "Eine Programmiersprache"
        assert item.id is None

    def test_id_assigned_after_flush(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()
        assert item.id is not None
        assert isinstance(item.id, int)

    def test_submitted_answers_initially_empty(self):
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        assert item.submitted_answers == []


class TestQuizItemValidation:
    """Prüft, dass fehlende Pflichtfelder beim Flush einen Fehler auslösen."""

    def test_null_question_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question=None, correct_answer="Antwort")
        qr.add_quiz_item(item)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_correct_answer_raises(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer=None)
        qr.add_quiz_item(item)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_null_quiz_request_id_raises(self, db_session):
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        db_session.add(item)
        with pytest.raises(IntegrityError):
            db_session.flush()


class TestQuizItemRelationship:
    """Prüft die bidirektionalen Beziehungen von QuizItem."""

    def test_quiz_request_backref(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        assert item.quiz_request is qr
        assert item.quiz_request_id == qr.id

    def test_item_appears_in_quiz_request(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        db_session.add(session)
        db_session.flush()

        assert item in qr.quiz_items

    def test_add_submitted_answer_bidirectional(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        answer = SubmittedAnswer(answer="Meine Antwort")
        item.add_submitted_answer(answer)
        db_session.add(session)
        db_session.flush()

        assert answer in item.submitted_answers
        assert answer.quiz_item is item

    def test_cascade_delete_removes_submitted_answers(self, db_session):
        session = UserSession()
        qr = QuizRequest(topic="Python", difficulty="easy")
        session.add_quiz_request(qr)
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        qr.add_quiz_item(item)
        answer = SubmittedAnswer(answer="Meine Antwort")
        item.add_submitted_answer(answer)
        db_session.add(session)
        db_session.flush()

        answer_id = answer.id
        db_session.delete(item)
        db_session.flush()

        assert db_session.get(SubmittedAnswer, answer_id) is None


class TestQuizItemHelpers:
    """Prüft die Helper-Methode add_submitted_answer."""

    def test_add_submitted_answer_appends_to_list(self):
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        answer = SubmittedAnswer(answer="Meine Antwort")
        item.add_submitted_answer(answer)
        assert answer in item.submitted_answers

    def test_add_submitted_answer_sets_item_reference(self):
        item = QuizItem(question="Frage?", correct_answer="Antwort")
        answer = SubmittedAnswer(answer="Meine Antwort")
        item.add_submitted_answer(answer)
        assert answer.quiz_item is item
