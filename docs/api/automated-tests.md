# Automatisierte API-Tests

## Framework

- **pytest** als Test-Runner
- **FastAPI TestClient** (basiert auf httpx) fuer synchrone HTTP-Aufrufe gegen die FastAPI-App
- **SQLite In-Memory** als Test-Datenbank (kein laufender PostgreSQL-Server noetig)

## Tests ausfuehren

```bash
cd backend && uv run pytest tests/api/ -v
```

Alle Tests koennen auch zusammen mit den restlichen Tests ausgefuehrt werden:

```bash
cd backend && uv run pytest -v
```

## Backend-Konfiguration fuer Tests

| Aspekt | Konfiguration |
|--------|---------------|
| Datenbank | SQLite In-Memory (`sqlite:///:memory:`) mit `StaticPool`, damit alle Verbindungen dieselbe Instanz sehen |
| Tabellen | Werden per `autouse`-Fixture vor jedem Test erstellt und danach wieder geloescht – jeder Test startet mit leerer DB |
| AI-Provider | `StubAIProvider` (in `app/ai_stubs.py`) – gibt deterministische Antworten ohne Netzwerkzugriff |
| Dependency Override | `get_db` wird durch die Test-Session ersetzt, sodass der App-Code unverändert bleibt |

## Testgruppen

### Happy-Path Tests

| Testklasse | Beschreibung |
|------------|-------------|
| `TestHealthEndpoint` | GET /health gibt 200 mit `"status": "ok"` und nicht-leerem `service`-Feld zurueck |
| `TestCreateSession` | POST /sessions gibt 201 mit ganzzahliger `id` und nicht-leerem `created_at` zurueck |
| `TestListSessions` | GET /sessions gibt 200 zurueck und die Liste enthaelt die zuvor erstellte Session |
| `TestSendMessage` | POST /sessions/{id}/messages gibt 201 mit nicht-leerem Antwort-Body (id, content, role) zurueck |
| `TestGetMessages` | GET /sessions/{id}/messages gibt 200 zurueck und die gesendete Nachricht ist in der Liste enthalten |
| `TestGenerateQuiz` | POST /sessions/{id}/quiz gibt 201 mit `quiz_request_id`, `topic` und mindestens einem Quiz-Item zurueck |
| `TestSubmitAnswer` | POST /sessions/{id}/quiz/{qid}/answer gibt 201 mit `submitted_answer_id` und nicht-leerem `feedback` zurueck |

### Negative / Edge-Case Tests

| Testklasse | Beschreibung |
|------------|-------------|
| `TestSessionNotFound` | Zugriffe auf nicht existierende Session-ID (GET messages, POST message, POST quiz, DELETE) geben 404 zurueck |
| `TestEmptyMessageContent` | Leerer String oder nur Whitespace als Nachrichteninhalt gibt 422 zurueck |
| `TestMessageTooLong` | Nachricht mit mehr als 5000 Zeichen gibt 422 zurueck |
| `TestQuestionNotFound` | Antwort fuer nicht existierende Frage-ID gibt 404 zurueck |
| `TestEmptyQuizTopic` | Leeres oder nur aus Whitespace bestehendes Quiz-Thema gibt 422 zurueck |
| `TestEmptyMessagesBeforeAnySent` | GET messages vor dem Senden gibt 200 mit leerer Liste zurueck |
| `TestDeleteSession` | DELETE gibt 204 zurueck; nachfolgende Nachricht an geloeschte Session gibt 404 |
| `TestEmptyAnswer` | Leere Antwort bei Quiz-Bewertung gibt 422 zurueck |
