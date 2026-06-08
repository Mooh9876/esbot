from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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
