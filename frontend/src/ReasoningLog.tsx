import type { ReasoningLogEntry } from "./types";

export default function ReasoningLog({ entries }: { entries: ReasoningLogEntry[] }) {
  return (
    <div style={{ maxHeight: 800, overflowY: "auto", fontFamily: "monospace", fontSize: 13 }}>
      {entries.length === 0 && <p style={{ color: "#8fa3bf" }}>No Commander activity yet. Start a mission.</p>}
      {entries
        .slice()
        .reverse()
        .map((entry, i) => (
          <div key={i} style={{ marginBottom: 12, padding: 8, background: "#141b28", borderRadius: 6 }}>
            <div style={{ color: "#5ac8ff", marginBottom: 4 }}>{entry.trigger}</div>
            <div style={{ color: "#cdd6e4", marginBottom: 6 }}>{entry.reasoning}</div>
            <ul style={{ margin: 0, paddingLeft: 18, color: "#8fa3bf" }}>
              {entry.tasks.map((t) => (
                <li key={t.id}>
                  [{t.id}] {t.description} @ ({Math.round(t.x)}, {Math.round(t.y)}) prio {t.priority}
                </li>
              ))}
            </ul>
          </div>
        ))}
    </div>
  );
}
