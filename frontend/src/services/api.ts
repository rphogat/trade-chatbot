import type { ChatMessage, ChatResponse, ChatSession, Trade } from "../types";

const API_BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const chatApi = {
  getSessions: () => request<ChatSession[]>("/chat/sessions"),

  createSession: (title?: string) =>
    request<ChatSession>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify(title ? { title } : {}),
    }),

  getSession: (sessionId: string) =>
    request<ChatSession>(`/chat/sessions/${sessionId}`),

  deleteSession: (sessionId: string) =>
    request<void>(`/chat/sessions/${sessionId}`, { method: "DELETE" }),

  getMessages: (sessionId: string) =>
    request<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`),

  sendMessage: (sessionId: string, content: string) =>
    request<ChatResponse>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
};

export const tradeApi = {
  getTrades: (params?: Record<string, string>) => {
    const query = params ? "?" + new URLSearchParams(params).toString() : "";
    return request<Trade[]>(`/trades/${query}`);
  },

  getTrade: (tradeId: string) => request<Trade>(`/trades/${tradeId}`),
};
