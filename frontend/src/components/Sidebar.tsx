import type { ChatSession } from "../types";

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
  onToggleTradePanel: () => void;
  showTradePanel: boolean;
}

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onToggleTradePanel,
  showTradePanel,
}: SidebarProps) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <span className="logo">&#x1F4C8;</span>
        <h1>Trade ChatBot</h1>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <div className="sessions-list">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`session-item ${session.id === activeSessionId ? "active" : ""}`}
            onClick={() => onSelectSession(session.id)}
          >
            <span className="session-title">{session.title}</span>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
              title="Delete session"
            >
              &#x2715;
            </button>
          </div>
        ))}
        {sessions.length === 0 && (
          <div style={{ padding: "20px 12px", color: "var(--text-muted)", fontSize: "13px", textAlign: "center" }}>
            No chat sessions yet.<br />Click &quot;+ New Chat&quot; to start.
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <button className="trade-panel-toggle" onClick={onToggleTradePanel}>
          {showTradePanel ? "Hide" : "Show"} Trade RTDB Panel
        </button>
      </div>
    </div>
  );
}
