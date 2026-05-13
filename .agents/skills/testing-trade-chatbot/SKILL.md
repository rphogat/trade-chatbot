---
name: testing-trade-chatbot
description: Test the Trade ChatBot application end-to-end. Use when verifying chat UI, RTDB panel, session management, or trade query features.
---

# Testing Trade ChatBot

## Prerequisites

- Python 3.11+ with venv
- Node.js 18+
- No external API keys required for fallback mode testing

## Devin Secrets Needed

- `OPENAI_API_KEY` (optional) — only needed to test LLM-powered responses. Without it, the app uses keyword-based fallback responses for trade queries.

## Server Setup

### Backend (FastAPI on port 8000)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

Verify: `curl http://localhost:8000/api/health` should return `{"status":"healthy"}`

### Frontend (React/Vite on port 3000)

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies `/api` requests to `localhost:8000` via Vite config.

## Key Test Flows

### 1. Session Creation & Trade Query
- Click "+ New Chat" in sidebar
- Type a trade query like "Tell me about TRD-001"
- Verify response contains correct trade fields (Security, Type, Status, Trader, Price, etc.)
- Verify sidebar title updates to reflect the first message

### 2. Session Isolation
- Create two separate sessions with different queries
- Switch between them and verify each only shows its own messages
- No message leakage between sessions

### 3. RTDB Panel
- Click "Show Trade RTDB Panel" at bottom of sidebar
- Verify all 8 sample trades (TRD-001 to TRD-008) are displayed
- Check status badges are color-coded (green=EXECUTED, blue=PENDING, red=CANCELLED/FAILED, yellow=PARTIALLY_FILLED, teal=SETTLED)
- Panel auto-refreshes every 5 seconds

### 4. Session Deletion
- Hover over a session in sidebar to reveal the ✕ delete button
- Click ✕ and verify session is removed from sidebar

### 5. Trade Status Queries
- "Show pending trades" → should list TRD-002 and TRD-007
- "Show me all trades" → should list all 8 trades
- "Tell me about AAPL trades" → should show TRD-001

## Sample Trade Data

The RTDB is pre-loaded with 8 trades:
- TRD-001: AAPL, BUY, EXECUTED, John Smith
- TRD-002: GOOGL, SELL, PENDING, Sarah Johnson
- TRD-003: MSFT, BUY, PARTIALLY_FILLED, Mike Chen
- TRD-004: TSLA, SHORT_SELL, SETTLED, Emily Davis
- TRD-005: AMZN, BUY, EXECUTED, John Smith
- TRD-006: NVDA, OPTION_CALL, CANCELLED, Sarah Johnson
- TRD-007: JPM, SWAP, PENDING, Alex Wong
- TRD-008: META, BUY_TO_COVER, FAILED, Mike Chen

## Common Pitfalls

- **SQLite DateTime columns**: SQLAlchemy DateTime columns require native Python `datetime` objects, not ISO format strings. If you see "SQLite DateTime type only accepts Python datetime and date objects", check that `datetime.now()` results are not being `.isoformat()`-ed before passing to the ORM.
- **Database file locking**: If you delete `chat_history.db` while the server is running, restart the server to avoid "readonly database" errors.
- **pyproject.toml build-backend**: Must be `setuptools.build_meta`, not `setuptools.backends._legacy:_Backend`.
- **Browser focus**: When testing via browser UI, ensure Chrome is maximized and focused. Use `wmctrl` to manage window state on Linux.
