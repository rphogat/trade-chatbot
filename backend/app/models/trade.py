from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradeStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


class TradeType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SHORT_SELL = "SHORT_SELL"
    BUY_TO_COVER = "BUY_TO_COVER"
    SWAP = "SWAP"
    OPTION_CALL = "OPTION_CALL"
    OPTION_PUT = "OPTION_PUT"


class PricingInfo(BaseModel):
    price: float = Field(..., description="Execution price per unit")
    quantity: int = Field(..., description="Number of units traded")
    currency: str = Field(default="USD", description="Trading currency")
    total_value: float = Field(default=0.0, description="Total trade value")
    commission: float = Field(default=0.0, description="Commission/fees")


class Trade(BaseModel):
    trade_id: str = Field(..., description="Unique trade identifier")
    trade_status: TradeStatus = Field(..., description="Current status of the trade")
    executing_trader: str = Field(..., description="Trader executing the trade")
    security_traded: str = Field(..., description="Security/instrument being traded")
    type_of_trade: TradeType = Field(..., description="Type of trade")
    source_system: str = Field(..., description="Originating system")
    pricing_info: PricingInfo = Field(..., description="Pricing details")
    timestamp: str = Field(..., description="Trade timestamp (ISO 8601)")


class TradeUpdate(BaseModel):
    trade_status: Optional[TradeStatus] = None
    executing_trader: Optional[str] = None
    security_traded: Optional[str] = None
    type_of_trade: Optional[TradeType] = None
    source_system: Optional[str] = None
    pricing_info: Optional[PricingInfo] = None
