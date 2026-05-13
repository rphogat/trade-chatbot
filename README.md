# Trade ChatBot

A multi-session AI ChatBot with Real-Time Database (RTDB) for trade data. Each chat session maintains its own conversation history and context, allowing users to query and analyze trade data through natural language.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React Frontend                         │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Sidebar  │  │  Chat Area   │  │  Trade RTDB Panel  │  │
│  │ Sessions │  │  Messages    │  │  Live Trade Cards   │  │
│  └──────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────┴───────────────────────────────────┐
│                   FastAPI Backend                         │
│  ┌─────────────────┐  ┌──────────────────────────────┐   │
│  │  Chat Service   │  │  Trade RTDB Service           │   │
│  │  - Sessions     │  │  - In-memory trade store      │   │
│  │  - Messages     │  │  - CRUD operations            │   │
│  │  - LLM (OpenAI) │  │  - WebSocket broadcast        │   │
│  └────────┬────────┘  └──────────────────────────────┘   │
│           │                                               │
│  ┌────────┴────────┐                                      │
│  │  SQLite DB      │                                      │
│  │  (Chat History) │                                      │
│  └─────────────────┘                                      │
└──────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Session Chat**: Create, switch, and delete independent chat sessions
- **Conversation Context**: Each session maintains full history for contextual responses
- **Real-Time Trade Database (RTDB)**: In-memory database with 8 sample trades
- **Trade Data Fields**: TradeID, TradeStatus, ExecutingTrader, SecurityTraded, TypeOfTrade, SourceSystem, PricingInfo
- **LLM-Powered Responses**: OpenAI GPT integration with trade data context
- **Fallback Mode**: Works without API key using keyword-based trade lookups
- **Live Trade Panel**: Side panel showing real-time trade data with auto-refresh
- **WebSocket Support**: Real-time trade update broadcasting
- **Dark Theme UI**: Modern dark-themed interface inspired by ChatGPT

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, react-markdown
- **Backend**: FastAPI, SQLAlchemy (async), OpenAI SDK
- **Database**: SQLite (chat history), In-memory dict (RTDB)
- **Real-time**: WebSocket (FastAPI native)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key (optional — works without it using fallback responses)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Optional: Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:3000` with API proxied to `http://localhost:8000`.

## API Endpoints

### Chat
- `GET /api/chat/sessions` — List all sessions
- `POST /api/chat/sessions` — Create new session
- `GET /api/chat/sessions/{id}` — Get session details
- `DELETE /api/chat/sessions/{id}` — Delete session
- `GET /api/chat/sessions/{id}/messages` — Get session messages
- `POST /api/chat/sessions/{id}/messages` — Send message & get AI response

### Trades (RTDB)
- `GET /api/trades/` — List trades (with optional filters)
- `GET /api/trades/{id}` — Get specific trade
- `POST /api/trades/` — Add new trade
- `PATCH /api/trades/{id}` — Update trade
- `DELETE /api/trades/{id}` — Delete trade
- `WS /api/trades/ws` — WebSocket for real-time updates

### Health
- `GET /api/health` — Health check

## Sample Trade Data

The RTDB is pre-loaded with 8 sample trades across securities (AAPL, GOOGL, MSFT, TSLA, AMZN, NVDA, JPM, META) with various statuses, trade types, and source systems.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM responses | _(empty — uses fallback)_ |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `DB_PATH` | SQLite database file path | `chat_history.db` |
