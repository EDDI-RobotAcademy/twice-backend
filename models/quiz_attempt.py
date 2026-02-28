from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    quiz_id: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(8), nullable=False)  # LOW | MID | HIGH
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # START | FINISH | ABANDONED
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    account = relationship("Account", back_populates="quiz_attempts")
