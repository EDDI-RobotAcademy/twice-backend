from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from aggregation.schemas import (
    ParticipationResponse,
    Retention4wResponse,
    SnapshotItem,
    SnapshotsResponse,
)
from aggregation.service import (
    compute_participation,
    save_participation_snapshot,
    compute_retention_4w,
    save_retention_snapshot,
    list_snapshots,
)
from quiz.service import format_datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/participation", response_model=ParticipationResponse)
async def get_participation(
    from_: date = Query(..., alias="from", description="Period start YYYY-MM-DD"),
    to: date = Query(..., description="Period end YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    finished_users, target_users, rate = await compute_participation(db, from_, to)
    snap = await save_participation_snapshot(
        db, from_, to, finished_users, target_users, rate
    )
    return ParticipationResponse(
        finishedUsers=finished_users,
        targetUsers=target_users,
        participationRate=rate,
        snapshotId=snap.id,
    )


@router.get("/retention/4w", response_model=Retention4wResponse)
async def get_retention_4w(
    anchorDate: date = Query(..., description="Anchor date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    retained_users, total_users, rate = await compute_retention_4w(db, anchorDate)
    snap = await save_retention_snapshot(
        db, anchorDate, retained_users, total_users, rate
    )
    return Retention4wResponse(
        retainedUsers=retained_users,
        totalUsers=total_users,
        retentionRate=rate,
        snapshotId=snap.id,
    )


@router.get("/snapshots", response_model=SnapshotsResponse)
async def get_snapshots(
    metricType: str | None = Query(None, description="Filter by PARTICIPATION or RETENTION_4W"),
    db: AsyncSession = Depends(get_db),
):
    snapshots = await list_snapshots(db, metricType)
    items = [
        SnapshotItem(
            id=s.id,
            metric_type=s.metric_type,
            period_from=s.period_from,
            period_to=s.period_to,
            anchor_date=s.anchor_date,
            numerator=s.numerator,
            denominator=s.denominator,
            rate=s.rate,
            created_at=format_datetime(s.created_at),
        )
        for s in snapshots
    ]
    return SnapshotsResponse(snapshots=items)
