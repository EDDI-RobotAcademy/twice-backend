from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AggregationSnapshot(Base):
    __tablename__ = "aggregation_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    metric_type: Mapped[str] = mapped_column(String(32), nullable=False)  # PARTICIPATION | RETENTION_4W
    period_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    anchor_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    numerator: Mapped[int] = mapped_column(Integer, nullable=False)
    denominator: Mapped[int] = mapped_column(Integer, nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
