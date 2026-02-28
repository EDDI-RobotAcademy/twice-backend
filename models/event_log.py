from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)  # SERVICE_VISIT
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    account = relationship("Account", back_populates="event_logs")
