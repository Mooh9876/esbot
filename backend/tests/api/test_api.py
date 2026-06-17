import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# ---------------------------------------------------------------------------
# SQLite In-Memory Datenbank fuer isolierte API-Tests
# ---------------------------------------------------------------------------

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

_SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=_engine)
    session = _SessionLocal()

    def _override():
        yield session

    app.dependency_overrides[get_db] = _override
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=_engine)


# ===================================================================
# Happy-Path Tests
# ===================================================================


class TestHealthEndpoint:
    """GET /health gibt 200 mit erwartetem Status-Feld zurueck."""

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert isinstance(data["service"], str)
        assert len(data["service"]) > 0


class TestCreateSession:
    """POST /sessions mit gueltigen Daten gibt 201 und eine session_id."""

    def test_create_returns_201(self, client):
        resp = client.post("/sessions")
        assert resp.status_code == 201

    def test_create_returns_id(self, client):
        data = client.post("/sessions").json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_returns_created_at(self, client):
        data = client.post("/sessions").json()
        assert "created_at" in data
        assert isinstance(data["created_at"], str)
        assert len(data["created_at"]) > 0


class TestListSessions:
    """GET /sessions gibt 200 und enthaelt die erstellte Session."""

    def test_list_contains_new_session(self, client):
        created = client.post("/sessions").json()
        resp = client.get("/sessions")
        assert resp.status_code == 200

        sessions = resp.json()
        assert isinstance(sessions, list)
        ids = [s["id"] for s in sessions]
        assert created["id"] in ids


class TestSendMessage:
    """POST /sessions/{id}/messages gibt 201 und nicht-leeren Body."""

    def test_send_message_returns_201(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": "Was ist Python?"},
        )
        assert resp.status_code == 201

    def test_send_message_body(self, client):
        session_id = client.post("/sessions").json()["id"]
        data = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": "Was ist Python?"},
        ).json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0
        assert data["role"] in ("user", "bot")


class TestGetMessages:
    """GET /sessions/{id}/messages gibt 200 und enthaelt die Nachricht."""

    def test_message_history(self, client):
        session_id = client.post("/sessions").json()["id"]
        client.post(
            f"/sessions/{session_id}/messages",
            json={"content": "Hallo"},
        )
        resp = client.get(f"/sessions/{session_id}/messages")
        assert resp.status_code == 200

        messages = resp.json()
        assert isinstance(messages, list)
        assert len(messages) >= 1
        assert any(m["content"] == "Hallo" for m in messages)


class TestGenerateQuiz:
    """POST /sessions/{id}/quiz gibt 201 mit mindestens einer Frage."""

    def test_quiz_returns_201(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": "python"},
        )
        assert resp.status_code == 201

    def test_quiz_body(self, client):
        session_id = client.post("/sessions").json()["id"]
        data = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": "python"},
        ).json()
        assert "quiz_request_id" in data
        assert isinstance(data["quiz_request_id"], int)
        assert data["topic"] == "python"
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

        item = data["items"][0]
        assert "id" in item
        assert isinstance(item["question"], str)
        assert len(item["question"]) > 0
        assert isinstance(item["correct_answer"], str)
        assert len(item["correct_answer"]) > 0


class TestSubmitAnswer:
    """POST /sessions/{id}/quiz/{qid}/answer gibt 201 bei korrekter Antwort."""

    def _create_quiz(self, client):
        session_id = client.post("/sessions").json()["id"]
        quiz = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": "testing"},
        ).json()
        question_id = quiz["items"][0]["id"]
        correct_answer = quiz["items"][0]["correct_answer"]
        return session_id, question_id, correct_answer

    def test_submit_returns_201(self, client):
        session_id, question_id, correct_answer = self._create_quiz(client)
        resp = client.post(
            f"/sessions/{session_id}/quiz/{question_id}/answer",
            json={"answer": correct_answer},
        )
        assert resp.status_code == 201

    def test_submit_body(self, client):
        session_id, question_id, correct_answer = self._create_quiz(client)
        data = client.post(
            f"/sessions/{session_id}/quiz/{question_id}/answer",
            json={"answer": correct_answer},
        ).json()
        assert "submitted_answer_id" in data
        assert isinstance(data["submitted_answer_id"], int)
        assert "feedback" in data
        assert isinstance(data["feedback"], str)
        assert len(data["feedback"]) > 0


# ===================================================================
# Negative / Edge-Case Tests
# ===================================================================


class TestSessionNotFound:
    """Zugriff auf nicht existierende Session gibt 404."""

    def test_get_messages_404(self, client):
        resp = client.get("/sessions/999999/messages")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_send_message_404(self, client):
        resp = client.post(
            "/sessions/999999/messages",
            json={"content": "Hallo"},
        )
        assert resp.status_code == 404

    def test_generate_quiz_404(self, client):
        resp = client.post(
            "/sessions/999999/quiz",
            json={"topic": "python"},
        )
        assert resp.status_code == 404

    def test_delete_session_404(self, client):
        resp = client.delete("/sessions/999999")
        assert resp.status_code == 404


class TestEmptyMessageContent:
    """Leerer Nachrichteninhalt gibt 422."""

    def test_empty_string(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": ""},
        )
        assert resp.status_code == 422

    def test_whitespace_only(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": "   "},
        )
        assert resp.status_code == 422


class TestMessageTooLong:
    """Nachricht ueber 5000 Zeichen gibt 422."""

    def test_too_long_content(self, client):
        session_id = client.post("/sessions").json()["id"]
        long_text = "A" * 5001
        resp = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": long_text},
        )
        assert resp.status_code == 422


class TestQuestionNotFound:
    """Antwort fuer nicht existierende Frage gibt 404."""

    def test_invalid_question_id(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/quiz/999999/answer",
            json={"answer": "Test"},
        )
        assert resp.status_code == 404
        assert "detail" in resp.json()


class TestEmptyQuizTopic:
    """Leeres Quiz-Thema gibt 422."""

    def test_empty_topic(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": ""},
        )
        assert resp.status_code == 422

    def test_whitespace_topic(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": "   "},
        )
        assert resp.status_code == 422


class TestEmptyMessagesBeforeAnySent:
    """GET messages vor dem Senden einer Nachricht gibt 200 mit leerer Liste."""

    def test_empty_list(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.get(f"/sessions/{session_id}/messages")
        assert resp.status_code == 200
        assert resp.json() == []


class TestDeleteSession:
    """DELETE /sessions/{id} gibt 204 und nachfolgende Zugriffe geben 404."""

    def test_delete_returns_204(self, client):
        session_id = client.post("/sessions").json()["id"]
        resp = client.delete(f"/sessions/{session_id}")
        assert resp.status_code == 204

    def test_message_after_delete_returns_404(self, client):
        session_id = client.post("/sessions").json()["id"]
        client.delete(f"/sessions/{session_id}")
        resp = client.post(
            f"/sessions/{session_id}/messages",
            json={"content": "Hallo"},
        )
        assert resp.status_code == 404


class TestEmptyAnswer:
    """Leere Antwort bei Quiz-Bewertung gibt 422."""

    def test_empty_answer(self, client):
        session_id = client.post("/sessions").json()["id"]
        quiz = client.post(
            f"/sessions/{session_id}/quiz",
            json={"topic": "testing"},
        ).json()
        question_id = quiz["items"][0]["id"]
        resp = client.post(
            f"/sessions/{session_id}/quiz/{question_id}/answer",
            json={"answer": ""},
        )
        assert resp.status_code == 422
