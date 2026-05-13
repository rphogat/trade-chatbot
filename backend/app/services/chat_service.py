from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from openai import AsyncOpenAI
from sqlalchemy import func, select

from app.db.database import ChatMessageDB, ChatSessionDB, async_session_factory
from app.models.chat import ChatMessage, ChatSession, MessageRole
from app.services.rtdb import trade_rtdb

SYSTEM_PROMPT = """You are a Trade Assistant ChatBot. You have access to a \
Real-Time Database (RTDB) containing live trade data. \
You help users query, analyze, and understand their trades.

You can help with:
- Looking up specific trades by ID, trader, security, status, or source system
- Analyzing trade patterns and portfolio positions
- Explaining trade statuses and types
- Providing summaries of trading activity
- Answering general questions about trading concepts

Current RTDB State:
{trade_data}

When answering questions about trades, always reference the actual data from the RTDB above. \
Be precise with numbers and trade details. If a user asks about a trade that doesn't exist, \
let them know and suggest what trades are available."""


class ChatService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        self._client: Optional[AsyncOpenAI] = None
        if api_key:
            self._client = AsyncOpenAI(api_key=api_key)

    async def create_session(self, title: Optional[str] = None) -> ChatSession:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        db_session = ChatSessionDB(
            id=session_id,
            title=title or "New Chat",
            created_at=now,
            updated_at=now,
        )

        async with async_session_factory() as db:
            db.add(db_session)
            await db.commit()

        return ChatSession(
            id=session_id,
            title=title or "New Chat",
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            message_count=0,
        )

    async def get_sessions(self) -> list[ChatSession]:
        async with async_session_factory() as db:
            result = await db.execute(
                select(ChatSessionDB).order_by(ChatSessionDB.updated_at.desc())
            )
            rows = result.scalars().all()

            sessions = []
            for row in rows:
                msg_count_result = await db.execute(
                    select(func.count())
                    .select_from(ChatMessageDB)
                    .where(ChatMessageDB.session_id == row.id)
                )
                msg_count = msg_count_result.scalar() or 0

                sessions.append(
                    ChatSession(
                        id=row.id,
                        title=row.title,
                        created_at=str(row.created_at),
                        updated_at=str(row.updated_at),
                        message_count=msg_count,
                    )
                )
            return sessions

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        async with async_session_factory() as db:
            result = await db.execute(
                select(ChatSessionDB).where(ChatSessionDB.id == session_id)
            )
            row = result.scalar_one_or_none()
            if not row:
                return None

            msg_count_result = await db.execute(
                select(func.count())
                .select_from(ChatMessageDB)
                .where(ChatMessageDB.session_id == session_id)
            )
            msg_count = msg_count_result.scalar() or 0

            return ChatSession(
                id=row.id,
                title=row.title,
                created_at=str(row.created_at),
                updated_at=str(row.updated_at),
                message_count=msg_count,
            )

    async def delete_session(self, session_id: str) -> bool:
        async with async_session_factory() as db:
            result = await db.execute(
                select(ChatSessionDB).where(ChatSessionDB.id == session_id)
            )
            row = result.scalar_one_or_none()
            if not row:
                return False

            await db.execute(
                ChatMessageDB.__table__.delete().where(
                    ChatMessageDB.session_id == session_id
                )
            )
            await db.delete(row)
            await db.commit()
            return True

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        async with async_session_factory() as db:
            result = await db.execute(
                select(ChatMessageDB)
                .where(ChatMessageDB.session_id == session_id)
                .order_by(ChatMessageDB.message_order.asc())
            )
            rows = result.scalars().all()
            return [
                ChatMessage(
                    id=row.id,
                    session_id=row.session_id,
                    role=MessageRole(row.role),
                    content=row.content,
                    timestamp=str(row.timestamp),
                )
                for row in rows
            ]

    async def send_message(self, session_id: str, content: str) -> ChatMessage:
        now = datetime.now(timezone.utc)

        async with async_session_factory() as db:
            count_result = await db.execute(
                select(func.count())
                .select_from(ChatMessageDB)
                .where(ChatMessageDB.session_id == session_id)
            )
            msg_count = count_result.scalar() or 0

            user_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=MessageRole.USER.value,
                content=content,
                timestamp=now,
                message_order=msg_count,
            )
            db.add(user_msg)
            await db.commit()

        history = await self.get_messages(session_id)
        assistant_content = await self._generate_response(history)

        async with async_session_factory() as db:
            assistant_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=MessageRole.ASSISTANT.value,
                content=assistant_content,
                timestamp=datetime.now(timezone.utc),
                message_order=msg_count + 1,
            )
            db.add(assistant_msg)

            session_result = await db.execute(
                select(ChatSessionDB).where(ChatSessionDB.id == session_id)
            )
            session_row = session_result.scalar_one_or_none()
            if session_row:
                if msg_count == 0:
                    session_row.title = content[:50] + ("..." if len(content) > 50 else "")
                session_row.updated_at = datetime.now(timezone.utc)

            await db.commit()

        return ChatMessage(
            id=assistant_msg.id,
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            timestamp=str(assistant_msg.timestamp),
        )

    async def _generate_response(self, history: list[ChatMessage]) -> str:
        trade_data = trade_rtdb.get_trade_summary()
        system_message = SYSTEM_PROMPT.format(trade_data=trade_data)

        if not self._client:
            return self._fallback_response(history, trade_data)

        try:
            messages = [{"role": "system", "content": system_message}]
            for msg in history:
                messages.append({"role": msg.role.value, "content": msg.content})

            response = await self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content or "I couldn't generate a response."
        except Exception as e:
            return f"LLM Error: {e}\n\n{self._fallback_response(history, trade_data)}"

    def _fallback_response(self, history: list[ChatMessage], trade_data: str) -> str:
        if not history:
            return "Hello! I'm your Trade Assistant. Ask me about trades in the RTDB."

        last_msg = history[-1].content.lower()

        if any(w in last_msg for w in ["all trades", "show trades", "list trades", "all trade"]):
            return f"Here's the current state of all trades:\n\n{trade_data}"

        if "trd-" in last_msg:
            trade_id = ""
            for word in last_msg.split():
                if "trd-" in word:
                    trade_id = word.upper().strip("?.,!")
                    break
            trades = list(trade_rtdb._trades.values())
            for t in trades:
                if t.trade_id == trade_id:
                    return (
                        f"**Trade {t.trade_id}**\n"
                        f"- Security: {t.security_traded}\n"
                        f"- Type: {t.type_of_trade.value}\n"
                        f"- Status: {t.trade_status.value}\n"
                        f"- Trader: {t.executing_trader}\n"
                        f"- Price: {t.pricing_info.currency} {t.pricing_info.price}\n"
                        f"- Quantity: {t.pricing_info.quantity}\n"
                        f"- Total: {t.pricing_info.currency} {t.pricing_info.total_value}\n"
                        f"- Commission: {t.pricing_info.currency} {t.pricing_info.commission}\n"
                        f"- Source: {t.source_system}\n"
                        f"- Timestamp: {t.timestamp}"
                    )
            ids = ', '.join(t.trade_id for t in trades)
            return f"Trade {trade_id} not found. Available trades: {ids}"

        for status in ["pending", "executed", "cancelled", "settled", "failed", "partially"]:
            if status in last_msg:
                trades = list(trade_rtdb._trades.values())
                matched = [
                    t for t in trades if status.upper() in t.trade_status.value
                ]
                if matched:
                    lines = [f"Trades with status containing '{status.upper()}':\n"]
                    for t in matched:
                        lines.append(
                            f"- {t.trade_id}: {t.security_traded} ({t.type_of_trade.value}) "
                            f"by {t.executing_trader}"
                        )
                    return "\n".join(lines)
                return f"No trades found with status '{status.upper()}'."

        for security in ["aapl", "googl", "msft", "tsla", "amzn", "nvda", "jpm", "meta"]:
            if security in last_msg:
                trades = list(trade_rtdb._trades.values())
                matched = [
                    t for t in trades if security.upper() in t.security_traded.upper()
                ]
                if matched:
                    t = matched[0]
                    return (
                        f"**{t.security_traded} Trade ({t.trade_id})**\n"
                        f"- Type: {t.type_of_trade.value}\n"
                        f"- Status: {t.trade_status.value}\n"
                        f"- Trader: {t.executing_trader}\n"
                        f"- Price: {t.pricing_info.currency} {t.pricing_info.price} x "
                        f"{t.pricing_info.quantity}\n"
                        f"- Total: {t.pricing_info.currency} {t.pricing_info.total_value}"
                    )

        if any(w in last_msg for w in ["help", "what can", "how to"]):
            return (
                "I can help you with:\n"
                "- **View all trades**: 'Show all trades'\n"
                "- **Lookup by ID**: 'Tell me about TRD-001'\n"
                "- **Filter by status**: 'Show pending trades'\n"
                "- **Filter by security**: 'What's the AAPL trade?'\n"
                "- **Trade summary**: 'Give me a summary'\n\n"
                f"Currently tracking {len(trade_rtdb._trades)} trades in the RTDB."
            )

        return (
            f"I'm your Trade Assistant with access to "
            f"{len(trade_rtdb._trades)} trades in the RTDB. "
            "Try asking about specific trades (e.g., 'Tell me about TRD-001'), "
            "trade statuses (e.g., 'Show pending trades'), "
            "or securities (e.g., 'What's the AAPL trade?'). "
            "Type 'help' for more options."
        )


chat_service = ChatService()
