from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from engagement.schemas import VisitRequest, VisitResponse
from engagement.service import record_visit

router = APIRouter(prefix="/engagement", tags=["engagement"])


@router.post("/visit", response_model=VisitResponse)
async def post_visit(body: VisitRequest, db: AsyncSession = Depends(get_db)):
    await record_visit(db, body.userId)
    return VisitResponse(ok=True)
