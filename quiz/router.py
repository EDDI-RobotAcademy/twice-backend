from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from quiz.schemas import (
    QuizStartRequest,
    QuizStartResponse,
    QuizCompleteRequest,
    QuizCompleteResponse,
    QuizAbandonRequest,
    QuizAbandonResponse,
    QuizHistoryItem,
    QuizHistoryResponse,
)
from quiz.service import (
    start_attempt,
    complete_attempt,
    abandon_attempt,
    get_finish_history,
    format_datetime,
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/start", response_model=QuizStartResponse)
async def post_quiz_start(body: QuizStartRequest, db: AsyncSession = Depends(get_db)):
    attempt = await start_attempt(
        db, body.userId, body.quizId, body.difficultyLevel
    )
    return QuizStartResponse(
        attemptId=attempt.id,
        status="START",
        startedAt=format_datetime(attempt.started_at),
    )


@router.post("/complete", response_model=QuizCompleteResponse)
async def post_quiz_complete(body: QuizCompleteRequest, db: AsyncSession = Depends(get_db)):
    attempt = await complete_attempt(db, body.userId, body.attemptId, body.score)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return QuizCompleteResponse(
        attemptId=attempt.id,
        status="FINISH",
        score=attempt.score,
        startedAt=format_datetime(attempt.started_at),
        finishedAt=format_datetime(attempt.finished_at),
    )


@router.post("/abandon", response_model=QuizAbandonResponse)
async def post_quiz_abandon(body: QuizAbandonRequest, db: AsyncSession = Depends(get_db)):
    attempt, error = await abandon_attempt(db, body.userId, body.attemptId)
    if attempt is None and error is None:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if error == "already_finished":
        raise HTTPException(status_code=400, detail="Attempt already FINISH or ABANDONED")
    return QuizAbandonResponse(
        attemptId=attempt.id,
        status="ABANDONED",
        startedAt=format_datetime(attempt.started_at),
        finishedAt=format_datetime(attempt.finished_at),
    )


@router.get("/history", response_model=QuizHistoryResponse)
async def get_quiz_history(userId: str, db: AsyncSession = Depends(get_db)):
    attempts = await get_finish_history(db, userId)
    items = [
        QuizHistoryItem(
            quizId=a.quiz_id,
            difficultyLevel=a.difficulty_level,
            score=a.score,
            startedAt=format_datetime(a.started_at),
            finishedAt=format_datetime(a.finished_at) if a.finished_at else "",
        )
        for a in attempts
    ]
    return QuizHistoryResponse(attempts=items)
