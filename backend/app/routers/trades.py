from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.models.trade import Trade, TradeStatus, TradeType, TradeUpdate
from app.services.rtdb import trade_rtdb

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("/", response_model=list[Trade])
async def list_trades(
    status: Optional[TradeStatus] = None,
    trader: Optional[str] = None,
    security: Optional[str] = None,
    trade_type: Optional[TradeType] = None,
    source_system: Optional[str] = None,
) -> list[Trade]:
    return await trade_rtdb.query_trades(
        status=status,
        trader=trader,
        security=security,
        trade_type=trade_type,
        source_system=source_system,
    )


@router.get("/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str) -> Trade:
    trade = await trade_rtdb.get_trade(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@router.post("/", response_model=Trade, status_code=201)
async def create_trade(trade: Trade) -> Trade:
    existing = await trade_rtdb.get_trade(trade.trade_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Trade {trade.trade_id} already exists")
    return await trade_rtdb.add_trade(trade)


@router.patch("/{trade_id}", response_model=Trade)
async def update_trade(trade_id: str, update: TradeUpdate) -> Trade:
    trade = await trade_rtdb.update_trade(trade_id, update)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@router.delete("/{trade_id}", status_code=204)
async def delete_trade(trade_id: str) -> None:
    deleted = await trade_rtdb.delete_trade(trade_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")


@router.websocket("/ws")
async def trade_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    await trade_rtdb.subscribe(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await trade_rtdb.unsubscribe(websocket)
