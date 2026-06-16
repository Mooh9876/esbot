# ESBot Backend API Reference

## 1. Base URL

The ESBot backend runs locally at:
- http://localhost:8000

---

## 2. Setup instructions

### Install dependencies
```bash
cd backend && uv sync --all-groups
```

### Start database
```bash
docker compose -f .devcontainer/docker-compose.yml up db -d
```
Important: Make sure Docker Desktop is running.

### Environment setup
Copy the provided environment template:
```bash
cp backend/.env.example backend/.env
```
The following configuration is available:
- `DATABASE_URL`: PostgreSQL connection string
- `APP_ENV`: application environment (development/test/production)

Important: Change values if necessary

### Run backend
```bash
cd backend && uv run uvicorn app.main:app --reload
```

### Run tests
```bash
cd backend && uv run pytest -v
```

### Verify
Open:
- http://localhost:8000/health
- http://localhost:8000/docs

---

## 3. General Notes

- All endpoints use JSON for request and response bodies
- Session IDs, message IDs, quiz IDs are integers
- No `/api/v1`prefix is used in this implementation
- `created_at`fields are returned as ISO 8601 strings (via `datetime.isoformat()`)
- Validation errors follow FastAPI's standard `422 Unprocessable Entity` format
- AI responses are generated via a pluggable `AIProvider` (stub in test mode)

---


## 4. Endpoints

## 4.1 System

### GET /health
#### Description
- Health check endpoint

#### Success Response
- Code: `200 OK`
```json
{
    "status": "ok",
    "service": "esbot-backend"
}
```

## 4.2 Sessions

### GET /sessions
#### Description 
- Returns all sessions

#### Success Response
- Code: `200 OK`
```json
[
  {
    "id": 0,
    "created_at": "2026-06-16T15:30:00Z"
  }
]
```

### POST /sessions
#### Description
- Creates a new session

#### Success Response
- `201 Created`
```json
{
  "id": 0,
  "created_at": "2026-06-16T15:30:00Z"
}
```

### DELETE /sessions/{session_id}
#### Description
- Deletes a session

#### Path Parameters
- `session_id`(integer, required)

#### Success Response
- `204 No Content`


## 4.3 Messages

### POST /sessions/{session_id}/messages
#### Description 
- Sends a message to a session and receives a bot reply

#### Path Parameters
- `session_id`(integer)

#### Request Body
```json
{
  "content": "What is Python?"
}
```
- max. 5000 chars
- not empty

#### Success Response
- `201 Created`
```json
{
  "id": 0,
  "content": "Python is a programming language, which...",
  "role": "user",
  "created_at": "2026-06-16T15:31:00Z"
}
```


### GET /sessions/{session_id}/messages
#### Description
- Returns all messages of a session

#### Path Parameters
- `session_id`(integer)

#### Success Response
- `200 OK`
```json
[
  {
    "id": 1,
    "content": "Hello",
    "role": "user",
    "created_at": "2026-06-16T15:31:00Z"
  }
]
```


## 4.4 Quiz

### POST /sessions/{session_id}/quiz
#### Description
- Generates a quiz for a session

#### Path Parameters
- `session_id`(integer)

#### Request Body
```json
{
  "topic": "python"
}
```

#### Response
- `201 Created`
```json
{
  "quiz_request_id": 0,
  "topic": "python",
  "items": [
    {
      "id": 0,
      "question": "What is Python?",
      "correct_answer": "A programming language."
    }
  ]
}
```


### POST /sessions/{session_id}/quiz/{question_id}/answer
#### Description
- Submits an answer for a quiz question and returns evaluation feedback

#### Path Parameters
- `session_id`(integer)
- `question_id`(integer)

#### Request Body
```json
{
  "answer": "Python is a programming language."
}
```
- max. 2000 chars
- not empty

#### Response
- `201 Created`
```json
{
  "submitted_answer_id": 0,
  "feedback": "Correct"
}
```
---

## 5. Error Handling

### 404 Not Found
Returned when a resource does not exist.
```json
{
  "detail": "Session nicht gefunden"
}
```
or
```json
{
    "detail": "Frage nicht gefunden"
}
```
or
```json
{
    "detail": "Frage gehoert nicht zu dieser Session"
}
```

### 422 Unprocessable Entity
Validation error (Pydantic).

Examples:
- empty content
- empty topic
- empty answer
- exceeded length limits

```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "Nachricht darf nicht leer sein",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
Returned when an unexpected error occurs on the server.
```json
{
    "detail": "Internal Server Error"
}
```

### 503 Service Unavailable
AI provider is unavailable.

```json
{
  "detail": "KI-Service ist derzeit nicht erreichbar"
}
```
---

## 6. Validation Rules

| Field | Rule |
|-------|------|
| message.content | required, 1-5000 chars |
| quiz.topic | required, 1-200 chars |
| answer.answer | required, 1-2000 chars |

---

## 7. Summary

The ESBot API provides:

- Session management
- Chat based messaging with AI responses
- Quiz generation per session
- Answer evaluation system
- Health check endpoint