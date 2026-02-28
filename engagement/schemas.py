from pydantic import BaseModel, Field


class VisitRequest(BaseModel):
    userId: str = Field(..., description="Account ID")


class VisitResponse(BaseModel):
    ok: bool = True
