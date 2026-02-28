from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    event_logs = relationship("EventLog", back_populates="account")
    quiz_attempts = relationship("QuizAttempt", back_populates="account")
