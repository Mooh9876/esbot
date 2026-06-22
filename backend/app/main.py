from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.routes.sessions import router as sessions_router

# Alle Modelle müssen importiert sein, bevor create_all aufgerufen wird
import app.models.user_session  # noqa: F401
import app.models.message  # noqa: F401
import app.models.quiz_request  # noqa: F401
import app.models.quiz_item  # noqa: F401
import app.models.submitted_answer  # noqa: F401
import app.models.evaluation_result  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bei SQLite: Tabellen anlegen falls noch nicht vorhanden (idempotent)
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        print("[ESBot] SQLite tables created/verified")
    # beim Start kurz prüfen ob die DB erreichbar ist
    # im Test-Profil (SQLite) läuft das nicht durch, deshalb try/except
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[ESBot] DB connection ok")
    except Exception as e:
        print(f"[ESBot] DB not available: {e}")
    yield
    engine.dispose()


app = FastAPI(
    title="ESBot Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(sessions_router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "esbot-backend"}
