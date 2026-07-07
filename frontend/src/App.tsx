import { useEffect, useRef, useState } from "react";
import ReasoningLog from "./ReasoningLog";
import SwarmCanvas from "./SwarmCanvas";
import type { SimSnapshot } from "./types";

const API_BASE = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

export default function App() {
  const [snapshot, setSnapshot] = useState<SimSnapshot | null>(null);
  const [mission, setMission] = useState("Recon the north perimeter and hold a reserve near the LZ.");
  const [status, setStatus] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onmessage = (event) => setSnapshot(JSON.parse(event.data));
    ws.onopen = () => ws.send("hello");
    return () => ws.close();
  }, []);

  async function startMission() {
    setStatus("Planning mission...");
    const res = await fetch(`${API_BASE}/mission`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mission_text: mission }),
    });
    setStatus(res.ok ? "Mission planned." : "Mission planning failed.");
  }

  async function injectAgentLoss() {
    if (!snapshot) return;
    const alive = snapshot.agents.filter((a) => a.alive);
    if (alive.length === 0) return;
    const target = alive[Math.floor(Math.random() * alive.length)];
    setStatus(`Injecting loss of ${target.id}...`);
    const res = await fetch(`${API_BASE}/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind: "agent_lost", agent_id: target.id }),
    });
    setStatus(res.ok ? `Replanned after losing ${target.id}.` : "Replan failed.");
  }

  return (
    <div style={{ display: "flex", gap: 24, padding: 24, background: "#0b1220", minHeight: "100vh", color: "#cdd6e4" }}>
      <div>
        <h2 style={{ marginTop: 0 }}>Hivemind Demo</h2>
        <textarea
          value={mission}
          onChange={(e) => setMission(e.target.value)}
          rows={3}
          style={{ width: 500, marginBottom: 8 }}
        />
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <button onClick={startMission}>Start Mission</button>
          <button onClick={injectAgentLoss}>Inject: Lose Random Agent</button>
        </div>
        <p style={{ color: "#8fa3bf" }}>{status}</p>
        <SwarmCanvas snapshot={snapshot} />
      </div>
      <div style={{ width: 420 }}>
        <h3 style={{ marginTop: 0 }}>Commander Reasoning Log</h3>
        <ReasoningLog entries={snapshot?.reasoning_log ?? []} />
      </div>
    </div>
  );
}
