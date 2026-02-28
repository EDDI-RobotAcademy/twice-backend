from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class ParticipationResponse(BaseModel):
    finishedUsers: int
    targetUsers: int
    participationRate: float
    snapshotId: str


class Retention4wResponse(BaseModel):
    retainedUsers: int
    totalUsers: int
    retentionRate: float
    snapshotId: str


class SnapshotItem(BaseModel):
    id: str
    metric_type: str
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    anchor_date: Optional[date] = None
    numerator: int
    denominator: int
    rate: float
    created_at: str


class SnapshotsResponse(BaseModel):
    snapshots: list[SnapshotItem]
