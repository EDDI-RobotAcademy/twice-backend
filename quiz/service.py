import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.account import Account
from models.quiz_attempt import QuizAttempt

from engagement.service import ensure_account


async def start_attempt(
    session: AsyncSession,
    user_id: str,
    quiz_id: str,
    difficulty_level: str,
) -> QuizAttempt:
    await ensure_account(session, user_id)
    attempt_id = str(uuid.uuid4())
    now = datetime.utcnow()
    attempt = QuizAttempt(
        id=attempt_id,
        account_id=user_id,
        quiz_id=quiz_id,
        difficulty_level=difficulty_level,
        status="START",
        score=None,
        started_at=now,
        finished_at=None,
    )
    session.add(attempt)
    await session.flush()
    return attempt


async def complete_attempt(
    session: AsyncSession,
    user_id: str,
    attempt_id: str,
    score: int,
) -> QuizAttempt | None:
    result = await session.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.account_id == user_id,
        )
    )
    attempt = result.scalar_one_or_none()
    if attempt is None:
        return None
    now = datetime.utcnow()
    attempt.status = "FINISH"
    attempt.score = score
    attempt.finished_at = now
    await session.flush()
    return attempt


async def abandon_attempt(
    session: AsyncSession,
    user_id: str,
    attempt_id: str,
) -> tuple[QuizAttempt | None, str | None]:
    """Returns (attempt, error_code). error_code is 'already_finished' or None."""
    result = await session.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.account_id == user_id,
        )
    )
    attempt = result.scalar_one_or_none()
    if attempt is None:
        return None, None
    if attempt.status in ("FINISH", "ABANDONED"):
        return None, "already_finished"
    now = datetime.utcnow()
    attempt.status = "ABANDONED"
    attempt.finished_at = now
    await session.flush()
    return attempt, None


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def get_finish_history(session: AsyncSession, user_id: str) -> list[QuizAttempt]:
    result = await session.execute(
        select(QuizAttempt)
        .where(
            QuizAttempt.account_id == user_id,
            QuizAttempt.status == "FINISH",
        )
        .order_by(QuizAttempt.started_at.desc())
    )
    return list(result.scalars().all())
