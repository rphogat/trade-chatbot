export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  id: string | null;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string | null;
}

export interface ChatResponse {
  message: ChatMessage;
  session: ChatSession;
}

export interface Trade {
  trade_id: string;
  trade_status: string;
  executing_trader: string;
  security_traded: string;
  type_of_trade: string;
  source_system: string;
  pricing_info: PricingInfo;
  timestamp: string;
}

export interface PricingInfo {
  price: number;
  quantity: number;
  currency: string;
  total_value: number;
  commission: number;
}
