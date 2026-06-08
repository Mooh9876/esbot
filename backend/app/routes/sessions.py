from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_session import UserSession
from app.models.message import Message
from app.models.quiz_request import QuizRequest
from app.models.quiz_item import QuizItem as QuizItemModel
from app.models.submitted_answer import SubmittedAnswer
from app.models.evaluation_result import EvaluationResult
from app.ai_provider import AIProvider, AIProviderError, QuizResult
from app.ai_stubs import StubAIProvider

router = APIRouter(prefix="/sessions", tags=["sessions"])

MAX_MESSAGE_LENGTH = 5000
MAX_TOPIC_LENGTH = 200
MAX_ANSWER_LENGTH = 2000


def get_ai_provider() -> AIProvider:
    return StubAIProvider()


# ---------------------------------------------------------------------------
# Request- und Response-Schemas
# ---------------------------------------------------------------------------

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: str


class MessageRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Nachricht darf nicht leer sein")
        if len(stripped) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Nachricht darf maximal {MAX_MESSAGE_LENGTH} Zeichen lang sein"
            )
        return stripped


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    role: str
    created_at: str


class QuizGenerateRequest(BaseModel):
    topic: str

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Thema darf nicht leer sein")
        if len(stripped) > MAX_TOPIC_LENGTH:
            raise ValueError(
                f"Thema darf maximal {MAX_TOPIC_LENGTH} Zeichen lang sein"
            )
        return stripped


class QuizItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    correct_answer: str


class QuizResponse(BaseModel):
    quiz_request_id: int
    topic: str
    items: list[QuizItemResponse]


class AnswerRequest(BaseModel):
    answer: str

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Antwort darf nicht leer sein")
        if len(stripped) > MAX_ANSWER_LENGTH:
            raise ValueError(
                f"Antwort darf maximal {MAX_ANSWER_LENGTH} Zeichen lang sein"
            )
        return stripped


class AnswerResponse(BaseModel):
    submitted_answer_id: int
    feedback: str


# ---------------------------------------------------------------------------
# POST /sessions  –  Neue Session anlegen
# ---------------------------------------------------------------------------

@router.post("", response_model=SessionResponse, status_code=201)
def create_session(db: Session = Depends(get_db)):
    session = UserSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(
        id=session.id,
        created_at=session.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# GET /sessions  –  Alle Sessions auflisten
# ---------------------------------------------------------------------------

@router.get("", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(UserSession).order_by(UserSession.created_at.desc()).all()
    return [
        SessionResponse(id=s.id, created_at=s.created_at.isoformat())
        for s in sessions
    ]


# ---------------------------------------------------------------------------
# DELETE /sessions/{session_id}  –  Session loeschen
# ---------------------------------------------------------------------------

@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(UserSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    db.delete(session)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/messages  –  Nachricht senden
# ---------------------------------------------------------------------------

@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def send_message(
    session_id: int,
    body: MessageRequest,
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    session = db.get(UserSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    user_msg = Message(content=body.content, role="user")
    session.add_message(user_msg)
    db.add(session)
    db.flush()

    try:
        reply_text = ai.ask(body.content)
    except AIProviderError:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="KI-Service ist derzeit nicht erreichbar",
        )

    bot_msg = Message(content=reply_text, role="bot")
    session.add_message(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return MessageResponse(
        id=bot_msg.id,
        content=bot_msg.content,
        role=bot_msg.role,
        created_at=bot_msg.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}/messages  –  Nachrichtenverlauf abrufen
# ---------------------------------------------------------------------------

@router.get("/{session_id}/messages", response_model=list[MessageResponse])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    session = db.get(UserSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [
        MessageResponse(
            id=m.id,
            content=m.content,
            role=m.role,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/quiz  –  Quiz generieren
# ---------------------------------------------------------------------------

@router.post(
    "/{session_id}/quiz",
    response_model=QuizResponse,
    status_code=201,
)
def generate_quiz(
    session_id: int,
    body: QuizGenerateRequest,
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    session = db.get(UserSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    try:
        result: QuizResult = ai.generate_quiz(body.topic)
    except AIProviderError:
        raise HTTPException(
            status_code=503,
            detail="KI-Service ist derzeit nicht erreichbar",
        )

    quiz_request = QuizRequest(topic=body.topic, difficulty="standard")
    session.add_quiz_request(quiz_request)
    db.flush()

    for item in result.items:
        qi = QuizItemModel(question=item.question, correct_answer=item.correct_answer)
        quiz_request.add_quiz_item(qi)

    db.commit()
    db.refresh(quiz_request)

    return QuizResponse(
        quiz_request_id=quiz_request.id,
        topic=quiz_request.topic,
        items=[
            QuizItemResponse(
                id=qi.id,
                question=qi.question,
                correct_answer=qi.correct_answer,
            )
            for qi in quiz_request.quiz_items
        ],
    )


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/quiz/{question_id}/answer  –  Antwort bewerten
# ---------------------------------------------------------------------------

@router.post(
    "/{session_id}/quiz/{question_id}/answer",
    response_model=AnswerResponse,
    status_code=201,
)
def evaluate_answer(
    session_id: int,
    question_id: int,
    body: AnswerRequest,
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    session = db.get(UserSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    quiz_item = db.get(QuizItemModel, question_id)
    if quiz_item is None:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")

    if quiz_item.quiz_request.session_id != session.id:
        raise HTTPException(
            status_code=404,
            detail="Frage gehoert nicht zu dieser Session",
        )

    prompt = f"Question: {quiz_item.question}\nAnswer: {body.answer}"
    try:
        feedback = ai.ask(prompt)
    except AIProviderError:
        raise HTTPException(
            status_code=503,
            detail="KI-Service ist derzeit nicht erreichbar",
        )

    submitted = SubmittedAnswer(answer=body.answer)
    quiz_item.add_submitted_answer(submitted)
    db.flush()

    is_correct = body.answer.strip().lower() == quiz_item.correct_answer.strip().lower()
    evaluation = EvaluationResult(is_correct=is_correct, feedback=feedback)
    submitted.set_evaluation(evaluation)

    db.commit()
    db.refresh(submitted)

    return AnswerResponse(
        submitted_answer_id=submitted.id,
        feedback=feedback,
    )
