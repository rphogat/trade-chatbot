from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db
from app.routers import chat, trades
from app.services.rtdb import trade_rtdb


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    trade_rtdb._seed_sample_data()
    yield


app = FastAPI(
    title="Trade ChatBot API",
    description="Multi-session ChatBot with Real-Time Trade Database",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trades.router)
app.include_router(chat.router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "trade-chatbot"}
