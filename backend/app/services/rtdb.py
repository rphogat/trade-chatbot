from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket

from app.models.trade import PricingInfo, Trade, TradeStatus, TradeType, TradeUpdate


class TradeRTDB:
    """In-memory Real-Time Database for trade data with WebSocket broadcast."""

    def __init__(self) -> None:
        self._trades: dict[str, Trade] = {}
        self._subscribers: list[WebSocket] = []
        self._lock = asyncio.Lock()

    def _seed_sample_data(self) -> None:
        sample_trades = [
            Trade(
                trade_id="TRD-001",
                trade_status=TradeStatus.EXECUTED,
                executing_trader="John Smith",
                security_traded="AAPL",
                type_of_trade=TradeType.BUY,
                source_system="Bloomberg Terminal",
                pricing_info=PricingInfo(
                    price=178.50, quantity=1000, currency="USD",
                    total_value=178500.0, commission=49.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-002",
                trade_status=TradeStatus.PENDING,
                executing_trader="Sarah Johnson",
                security_traded="GOOGL",
                type_of_trade=TradeType.SELL,
                source_system="Reuters Eikon",
                pricing_info=PricingInfo(
                    price=141.20, quantity=500, currency="USD",
                    total_value=70600.0, commission=34.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-003",
                trade_status=TradeStatus.PARTIALLY_FILLED,
                executing_trader="Mike Chen",
                security_traded="MSFT",
                type_of_trade=TradeType.BUY,
                source_system="FIX Engine",
                pricing_info=PricingInfo(
                    price=415.75, quantity=2000, currency="USD",
                    total_value=831500.0, commission=89.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-004",
                trade_status=TradeStatus.SETTLED,
                executing_trader="Emily Davis",
                security_traded="TSLA",
                type_of_trade=TradeType.SHORT_SELL,
                source_system="Internal OMS",
                pricing_info=PricingInfo(
                    price=245.30, quantity=300, currency="USD",
                    total_value=73590.0, commission=24.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-005",
                trade_status=TradeStatus.EXECUTED,
                executing_trader="John Smith",
                security_traded="AMZN",
                type_of_trade=TradeType.BUY,
                source_system="Bloomberg Terminal",
                pricing_info=PricingInfo(
                    price=186.90, quantity=750, currency="USD",
                    total_value=140175.0, commission=44.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-006",
                trade_status=TradeStatus.CANCELLED,
                executing_trader="Sarah Johnson",
                security_traded="NVDA",
                type_of_trade=TradeType.OPTION_CALL,
                source_system="Reuters Eikon",
                pricing_info=PricingInfo(
                    price=875.00, quantity=100, currency="USD",
                    total_value=87500.0, commission=19.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-007",
                trade_status=TradeStatus.PENDING,
                executing_trader="Alex Wong",
                security_traded="JPM",
                type_of_trade=TradeType.SWAP,
                source_system="FIX Engine",
                pricing_info=PricingInfo(
                    price=198.40, quantity=1500, currency="USD",
                    total_value=297600.0, commission=74.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            Trade(
                trade_id="TRD-008",
                trade_status=TradeStatus.FAILED,
                executing_trader="Mike Chen",
                security_traded="META",
                type_of_trade=TradeType.BUY_TO_COVER,
                source_system="Internal OMS",
                pricing_info=PricingInfo(
                    price=505.20, quantity=400, currency="USD",
                    total_value=202080.0, commission=39.99,
                ),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        for trade in sample_trades:
            self._trades[trade.trade_id] = trade

    async def get_all_trades(self) -> list[Trade]:
        async with self._lock:
            return list(self._trades.values())

    async def get_trade(self, trade_id: str) -> Optional[Trade]:
        async with self._lock:
            return self._trades.get(trade_id)

    async def add_trade(self, trade: Trade) -> Trade:
        async with self._lock:
            self._trades[trade.trade_id] = trade
        await self._broadcast({"event": "trade_added", "trade": trade.model_dump()})
        return trade

    async def update_trade(self, trade_id: str, update: TradeUpdate) -> Optional[Trade]:
        async with self._lock:
            existing = self._trades.get(trade_id)
            if not existing:
                return None
            update_data = update.model_dump(exclude_none=True)
            updated = existing.model_copy(update=update_data)
            updated = updated.model_copy(
                update={"timestamp": datetime.now(timezone.utc).isoformat()}
            )
            self._trades[trade_id] = updated
        await self._broadcast({"event": "trade_updated", "trade": updated.model_dump()})
        return updated

    async def delete_trade(self, trade_id: str) -> bool:
        async with self._lock:
            if trade_id not in self._trades:
                return False
            del self._trades[trade_id]
        await self._broadcast({"event": "trade_deleted", "trade_id": trade_id})
        return True

    async def query_trades(
        self,
        status: Optional[TradeStatus] = None,
        trader: Optional[str] = None,
        security: Optional[str] = None,
        trade_type: Optional[TradeType] = None,
        source_system: Optional[str] = None,
    ) -> list[Trade]:
        async with self._lock:
            results = list(self._trades.values())

        if status:
            results = [t for t in results if t.trade_status == status]
        if trader:
            results = [t for t in results if trader.lower() in t.executing_trader.lower()]
        if security:
            results = [t for t in results if security.upper() in t.security_traded.upper()]
        if trade_type:
            results = [t for t in results if t.type_of_trade == trade_type]
        if source_system:
            results = [t for t in results if source_system.lower() in t.source_system.lower()]

        return results

    def get_trade_summary(self) -> str:
        trades = list(self._trades.values())
        if not trades:
            return "No trades in the system."

        lines = [f"RTDB contains {len(trades)} trades:\n"]
        for t in trades:
            lines.append(
                f"- {t.trade_id}: {t.security_traded} | {t.type_of_trade.value} | "
                f"Status: {t.trade_status.value} | Trader: {t.executing_trader} | "
                f"Price: {t.pricing_info.currency} {t.pricing_info.price} x "
                f"{t.pricing_info.quantity} = {t.pricing_info.total_value} | "
                f"Source: {t.source_system}"
            )
        return "\n".join(lines)

    async def subscribe(self, ws: WebSocket) -> None:
        self._subscribers.append(ws)

    async def unsubscribe(self, ws: WebSocket) -> None:
        if ws in self._subscribers:
            self._subscribers.remove(ws)

    async def _broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self._subscribers:
            try:
                await ws.send_text(json.dumps(message, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._subscribers.remove(ws)


trade_rtdb = TradeRTDB()
