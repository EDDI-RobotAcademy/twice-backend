from pydantic import BaseModel, Field
from typing import Optional


class QuizStartRequest(BaseModel):
    userId: str
    quizId: str
    difficultyLevel: str = Field(..., pattern="^(LOW|MID|HIGH)$")


class QuizStartResponse(BaseModel):
    attemptId: str
    status: str = "START"
    startedAt: str


class QuizCompleteRequest(BaseModel):
    userId: str
    attemptId: str
    score: int = Field(..., ge=0)


class QuizCompleteResponse(BaseModel):
    attemptId: str
    status: str = "FINISH"
    score: int
    startedAt: str
    finishedAt: str


class QuizAbandonRequest(BaseModel):
    userId: str
    attemptId: str


class QuizAbandonResponse(BaseModel):
    attemptId: str
    status: str = "ABANDONED"
    startedAt: str
    finishedAt: str


class QuizHistoryItem(BaseModel):
    quizId: str
    difficultyLevel: str
    score: int
    startedAt: str  # yyyy-mm-dd HH:MM:SS
    finishedAt: str


class QuizHistoryResponse(BaseModel):
    attempts: list[QuizHistoryItem]
