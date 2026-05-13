import { useCallback, useEffect, useState } from "react";
import ChatArea from "./components/ChatArea";
import Sidebar from "./components/Sidebar";
import TradePanel from "./components/TradePanel";
import { chatApi } from "./services/api";
import type { ChatMessage, ChatSession } from "./types";

export default function App() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showTradePanel, setShowTradePanel] = useState(false);

  const loadSessions = useCallback(async () => {
    try {
      const data = await chatApi.getSessions();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }, []);

  const loadMessages = useCallback(async (sessionId: string) => {
    try {
      const data = await chatApi.getMessages(sessionId);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (activeSessionId) {
      loadMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId, loadMessages]);

  const handleNewChat = async () => {
    try {
      const session = await chatApi.createSession();
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await chatApi.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        setActiveSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeSessionId) return;

    const userMsg: ChatMessage = {
      id: "temp-" + Date.now(),
      session_id: activeSessionId,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(activeSessionId, content);
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== userMsg.id),
        { ...userMsg, id: "user-" + Date.now() },
        response.message,
      ]);
      setSessions((prev) =>
        prev.map((s) => (s.id === response.session.id ? response.session : s))
      );
    } catch (err) {
      console.error("Failed to send message:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: "error-" + Date.now(),
          session_id: activeSessionId,
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onToggleTradePanel={() => setShowTradePanel((p) => !p)}
        showTradePanel={showTradePanel}
      />
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        sessionTitle={activeSession?.title || "New Chat"}
        hasActiveSession={!!activeSessionId}
        onNewChat={handleNewChat}
      />
      {showTradePanel && (
        <TradePanel onClose={() => setShowTradePanel(false)} />
      )}
    </div>
  );
}
