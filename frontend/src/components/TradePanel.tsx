import { useEffect, useState } from "react";
import { tradeApi } from "../services/api";
import type { Trade } from "../types";

interface TradePanelProps {
  onClose: () => void;
}

export default function TradePanel({ onClose }: TradePanelProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTrades = async () => {
    try {
      const data = await tradeApi.getTrades();
      setTrades(data);
    } catch (err) {
      console.error("Failed to fetch trades:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
    const interval = setInterval(fetchTrades, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="trade-panel">
      <div className="trade-panel-header">
        <h3>
          <span className="live-dot"></span>
          RTDB Live Trades
        </h3>
        <button className="close-panel-btn" onClick={onClose}>
          &#x2715;
        </button>
      </div>

      <div className="trade-list">
        {loading && (
          <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
            Loading trades...
          </div>
        )}
        {!loading && trades.length === 0 && (
          <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
            No trades in RTDB
          </div>
        )}
        {trades.map((trade) => (
          <div key={trade.trade_id} className="trade-card">
            <div className="trade-card-header">
              <span className="trade-id">{trade.trade_id}</span>
              <span className={`trade-status ${trade.trade_status}`}>
                {trade.trade_status.replace("_", " ")}
              </span>
            </div>
            <div className="trade-card-body">
              <span className="label">Security</span>
              <span className="value">{trade.security_traded}</span>
              <span className="label">Type</span>
              <span className="value">{trade.type_of_trade.replace("_", " ")}</span>
              <span className="label">Trader</span>
              <span className="value">{trade.executing_trader}</span>
              <span className="label">Price</span>
              <span className="value">
                {trade.pricing_info.currency} {trade.pricing_info.price.toFixed(2)}
              </span>
              <span className="label">Qty</span>
              <span className="value">{trade.pricing_info.quantity.toLocaleString()}</span>
              <span className="label">Total</span>
              <span className="value">
                {trade.pricing_info.currency} {trade.pricing_info.total_value.toLocaleString()}
              </span>
              <span className="label">Source</span>
              <span className="value">{trade.source_system}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
