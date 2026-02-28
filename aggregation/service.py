import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from models.event_log import EventLog
from models.quiz_attempt import QuizAttempt
from models.aggregation_snapshot import AggregationSnapshot

SERVICE_VISIT = "SERVICE_VISIT"
PARTICIPATION = "PARTICIPATION"
RETENTION_4W = "RETENTION_4W"


def _date_to_datetime_start(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 0, 0, 0)


def _date_to_datetime_end(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 23, 59, 59, 999999)


async def compute_participation(
    session: AsyncSession,
    period_from: date,
    period_to: date,
) -> tuple[int, int, float]:
    """Returns (finished_users, target_users, rate)."""
    start_dt = _date_to_datetime_start(period_from)
    end_dt = _date_to_datetime_end(period_to)

    finished_subq = (
        select(distinct(QuizAttempt.account_id))
        .where(
            QuizAttempt.status == "FINISH",
            QuizAttempt.finished_at >= start_dt,
            QuizAttempt.finished_at <= end_dt,
        )
    )
    target_subq = (
        select(distinct(EventLog.account_id))
        .where(
            EventLog.event_type == SERVICE_VISIT,
            EventLog.occurred_at >= start_dt,
            EventLog.occurred_at <= end_dt,
        )
    )

    finished_result = await session.execute(
        select(func.count()).select_from(finished_subq.subquery())
    )
    target_result = await session.execute(
        select(func.count()).select_from(target_subq.subquery())
    )
    finished_users = finished_result.scalar() or 0
    target_users = target_result.scalar() or 0
    rate = (finished_users / target_users) if target_users else 0.0
    return finished_users, target_users, rate


async def save_participation_snapshot(
    session: AsyncSession,
    period_from: date,
    period_to: date,
    numerator: int,
    denominator: int,
    rate: float,
) -> AggregationSnapshot:
    snap = AggregationSnapshot(
        id=str(uuid.uuid4()),
        metric_type=PARTICIPATION,
        period_from=period_from,
        period_to=period_to,
        anchor_date=None,
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        created_at=datetime.utcnow(),
    )
    session.add(snap)
    await session.flush()
    return snap


def _four_weekly_buckets(anchor_date: date) -> list[tuple[date, date]]:
    """Four ISO weekly buckets ending at anchor_date (inclusive). Monday = week start.
    Returns [(start, end), ...] with end inclusive. Last bucket may be partial (Monday to anchor_date).
    """
    # Monday of the week containing anchor_date
    weekday = anchor_date.isoweekday()  # 1=Mon, 7=Sun
    week4_monday = anchor_date - timedelta(days=weekday - 1)
    bucket4 = (week4_monday, anchor_date)

    bucket3_end = week4_monday - timedelta(days=1)
    bucket3_start = bucket3_end - timedelta(days=6)
    bucket3 = (bucket3_start, bucket3_end)

    bucket2_end = bucket3_start - timedelta(days=1)
    bucket2_start = bucket2_end - timedelta(days=6)
    bucket2 = (bucket2_start, bucket2_end)

    bucket1_end = bucket2_start - timedelta(days=1)
    bucket1_start = bucket1_end - timedelta(days=6)
    bucket1 = (bucket1_start, bucket1_end)

    return [bucket1, bucket2, bucket3, bucket4]


async def compute_retention_4w(
    session: AsyncSession,
    anchor_date: date,
) -> tuple[int, int, float]:
    """Returns (retained_users, total_users, rate)."""
    buckets = _four_weekly_buckets(anchor_date)
    range_start = buckets[0][0]
    range_end = anchor_date

    start_dt = _date_to_datetime_start(range_start)
    end_dt = _date_to_datetime_end(range_end)

    # All users with >=1 SERVICE_VISIT in the full 4-week range
    total_subq = (
        select(distinct(EventLog.account_id))
        .where(
            EventLog.event_type == SERVICE_VISIT,
            EventLog.occurred_at >= start_dt,
            EventLog.occurred_at <= end_dt,
        )
    )
    total_result = await session.execute(
        select(func.count()).select_from(total_subq.subquery())
    )
    total_users = total_result.scalar() or 0

    if total_users == 0:
        return 0, 0, 0.0

    # Get all account_ids in the range
    accounts_result = await session.execute(total_subq)
    account_ids = [r[0] for r in accounts_result.all()]

    retained = 0
    for account_id in account_ids:
        in_all = True
        for (b_start, b_end) in buckets:
            b_start_dt = _date_to_datetime_start(b_start)
            b_end_dt = _date_to_datetime_end(b_end)
            r = await session.execute(
                select(EventLog.account_id).where(
                    EventLog.account_id == account_id,
                    EventLog.event_type == SERVICE_VISIT,
                    EventLog.occurred_at >= b_start_dt,
                    EventLog.occurred_at <= b_end_dt,
                ).limit(1)
            )
            if r.scalar() is None:
                in_all = False
                break
        if in_all:
            retained += 1

    rate = (retained / total_users) if total_users else 0.0
    return retained, total_users, rate


async def save_retention_snapshot(
    session: AsyncSession,
    anchor_date: date,
    numerator: int,
    denominator: int,
    rate: float,
) -> AggregationSnapshot:
    snap = AggregationSnapshot(
        id=str(uuid.uuid4()),
        metric_type=RETENTION_4W,
        period_from=None,
        period_to=None,
        anchor_date=anchor_date,
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        created_at=datetime.utcnow(),
    )
    session.add(snap)
    await session.flush()
    return snap


async def list_snapshots(
    session: AsyncSession,
    metric_type: str | None = None,
) -> list[AggregationSnapshot]:
    q = select(AggregationSnapshot).order_by(AggregationSnapshot.created_at.desc())
    if metric_type:
        q = q.where(AggregationSnapshot.metric_type == metric_type)
    result = await session.execute(q)
    return list(result.scalars().all())
