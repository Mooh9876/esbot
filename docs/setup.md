# ESBot – Backend Setup

## Voraussetzungen

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) als Paketmanager
- Docker + Docker Compose (für PostgreSQL)

**uv installieren:**
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Lokaler Start

```bash
git clone <REPO_URL>
cd esbot/backend

# Abhängigkeiten installieren
uv sync --all-groups

# .env anlegen
cp .env.example .env
# DATABASE_URL und APP_ENV in .env anpassen

# PostgreSQL starten
docker compose -f ../.devcontainer/docker-compose.yml up db -d

# Server starten
uv run uvicorn app.main:app --reload
```

API läuft auf `http://localhost:8000`, Swagger-Doku unter `http://localhost:8000/docs`.

---

## DevContainer (VS Code)

1. Extension "Dev Containers" installieren
2. Repo in VS Code öffnen → `Cmd+Shift+P` → **Reopen in Container**
3. Im Terminal: `cd backend && uv sync --all-groups`

Die `DATABASE_URL` ist über `.devcontainer/docker-compose.yml` bereits gesetzt, kein `.env` nötig.

---

## Tests ausführen

Tests laufen ohne laufendes PostgreSQL – sie nutzen SQLite in-memory (konfiguriert in `tests/conftest.py`).

### Mit uv (empfohlen)

```bash
cd backend

# alle Tests
uv run pytest -v

# nur Smoke-Tests
uv run pytest tests/test_smoke.py -v

# mit Coverage
uv run pytest --cov=app --cov-report=term-missing
```

### Ohne uv (nur Python + pip)

Falls `uv` nicht installiert ist, können die Tests auch direkt mit `pip` und `pytest` ausgeführt werden:

```bash
cd backend

# Abhängigkeiten installieren
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic-settings alembic python-dotenv pytest pytest-cov httpx

# alle Tests
python -m pytest tests/ -v

# nur Unit-Tests für ein bestimmtes Entity
python -m pytest tests/test_message.py -v

# mit Coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

---

## Projektstruktur

```
backend/
├── app/
│   ├── config.py                 # Konfiguration via Umgebungsvariablen
│   ├── database.py               # SQLAlchemy Engine, Session, Base
│   ├── main.py                   # FastAPI App, /health Endpoint
│   └── models/
│       ├── user_session.py       # UserSession Entity
│       ├── message.py            # Message Entity
│       ├── quiz_request.py       # QuizRequest Entity
│       ├── quiz_item.py          # QuizItem Entity
│       ├── submitted_answer.py   # SubmittedAnswer Entity
│       └── evaluation_result.py  # EvaluationResult Entity
├── tests/
│   ├── conftest.py               # pytest-Fixtures (SQLite in-memory, TestClient)
│   ├── test_smoke.py             # Smoke-Tests
│   ├── test_user_session.py      # Unit-Tests UserSession
│   ├── test_message.py           # Unit-Tests Message
│   ├── test_quiz_request.py      # Unit-Tests QuizRequest
│   ├── test_quiz_item.py         # Unit-Tests QuizItem
│   ├── test_submitted_answer.py  # Unit-Tests SubmittedAnswer
│   └── test_evaluation_result.py # Unit-Tests EvaluationResult
├── .env.example
└── pyproject.toml
```

---

## Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL-URL | `postgresql://esbot_user:esbot_password@localhost:5432/esbot` |
| `APP_ENV` | `development` / `test` / `production` | `development` |

---

## Hinweise

- **SQLite im Test-Profil**: Kein Datenbankserver nötig, Tests laufen in jeder Umgebung.
- **Alembic** ist installiert, wird aber erst ab Aufgabe 4.2 (Domain-Entities) benötigt.
- **LangChain / AI**: Kein Domain-Entity, wird separat als Service-Interface integriert und gemockt.

