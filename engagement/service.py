import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.account import Account
from models.event_log import EventLog


SERVICE_VISIT = "SERVICE_VISIT"


async def ensure_account(session: AsyncSession, user_id: str) -> Account:
    result = await session.execute(select(Account).where(Account.id == user_id))
    account = result.scalar_one_or_none()
    if account is None:
        account = Account(id=user_id)
        session.add(account)
        await session.flush()
    return account


async def record_visit(session: AsyncSession, user_id: str) -> None:
    await ensure_account(session, user_id)
    log = EventLog(
        id=str(uuid.uuid4()),
        account_id=user_id,
        event_type=SERVICE_VISIT,
        occurred_at=datetime.utcnow(),
    )
    session.add(log)
