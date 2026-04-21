"""
behave environment hooks: executed before and after every scenario.

Responsibilities:
  - Create an isolated in-memory SQLite database for each scenario.
  - Tear down all test data after each scenario so tests stay independent.
  - Attach shared objects (db_session, chat_service, etc.) to the context
    so step definitions can access them without duplicating setup code.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base


def before_scenario(context, scenario):
    """
    Set up a fresh in-memory SQLite database before every scenario.

    A new engine and session are created per scenario so each test
    starts with an empty schema and no residual data from prior tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import all models so SQLAlchemy knows their table definitions
    import app.models.user_session
    import app.models.message
    import app.models.quiz_request
    import app.models.quiz_item
    import app.models.submitted_answer
    import app.models.evaluation_result

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    context.db_session = SessionLocal()
    context.engine = engine

    # Placeholder attributes used by step definitions
    context.session = None       # the active UserSession domain object
    context.last_reply = None    # most recent bot reply text
    context.last_error = None    # most recent service-layer error message
    context.quiz_result = None   # most recent QuizResult returned by ChatService
    context.ai_provider = None   # set by "Given the AI provider is …" steps


def after_scenario(context, scenario):
    """
    Close the database session and drop all tables after every scenario.

    This guarantees that no test data leaks between scenarios.
    """
    if context.db_session:
        context.db_session.close()
    Base.metadata.drop_all(bind=context.engine)
