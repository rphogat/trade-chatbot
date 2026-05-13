import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "../types";

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  isLoading: boolean;
  sessionTitle: string;
  hasActiveSession: boolean;
  onNewChat: () => void;
}

const SUGGESTIONS = [
  "Show me all trades",
  "What is the status of TRD-001?",
  "Show pending trades",
  "Tell me about AAPL trades",
];

export default function ChatArea({
  messages,
  onSendMessage,
  isLoading,
  sessionTitle,
  hasActiveSession,
  onNewChat,
}: ChatAreaProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "44px";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "44px";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  if (!hasActiveSession) {
    return (
      <div className="main-area">
        <div className="welcome-screen">
          <div className="welcome-icon">&#x1F4AC;</div>
          <h2>Trade ChatBot</h2>
          <p>
            Your AI-powered trade assistant with access to the Real-Time
            Database. Ask about trades, analyze positions, and get insights
            from live market data.
          </p>
          <div className="welcome-suggestions">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                className="suggestion-btn"
                onClick={() => {
                  onNewChat();
                  setTimeout(() => onSendMessage(s), 300);
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-area">
      <div className="chat-header">
        <h2>{sessionTitle}</h2>
        <span className="status-badge">RTDB Connected</span>
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={msg.id || idx} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === "user" ? "U" : "AI"}
            </div>
            <div className="message-content">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">AI</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask about trades... (e.g., 'Show all pending trades')"
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            &#x27A4;
          </button>
        </div>
      </div>
    </div>
  );
}
