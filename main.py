from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import init_db
from engagement.router import router as engagement_router
from quiz.router import router as quiz_router
from aggregation.router import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="OH Backend", lifespan=lifespan)

app.include_router(engagement_router)
app.include_router(quiz_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "OH Backend", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok"}
