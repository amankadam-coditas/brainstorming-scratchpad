import { useEffect, useRef } from "react";
import type { SimSnapshot } from "./types";

const ZONE_COLOR: Record<string, string> = {
  no_fly: "rgba(220, 60, 60, 0.25)",
  comms_denied: "rgba(220, 170, 40, 0.2)",
};

export default function SwarmCanvas({ snapshot }: { snapshot: SimSnapshot | null }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !snapshot) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { world, agents } = snapshot;
    const scaleX = canvas.width / world.width;
    const scaleY = canvas.height / world.height;

    ctx.fillStyle = "#0b1220";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (const zone of world.zones) {
      ctx.fillStyle = ZONE_COLOR[zone.kind] ?? "rgba(150,150,150,0.2)";
      ctx.fillRect(zone.x * scaleX, zone.y * scaleY, zone.width * scaleX, zone.height * scaleY);
    }

    ctx.fillStyle = "#3a3f4b";
    for (const obs of world.obstacles) {
      ctx.beginPath();
      ctx.arc(obs.x * scaleX, obs.y * scaleY, obs.radius * scaleX, 0, Math.PI * 2);
      ctx.fill();
    }

    for (const agent of agents) {
      const x = agent.x * scaleX;
      const y = agent.y * scaleY;

      if (agent.waypoints.length > 0) {
        ctx.strokeStyle = "rgba(90, 200, 255, 0.4)";
        ctx.beginPath();
        ctx.moveTo(x, y);
        for (const [wx, wy] of agent.waypoints) {
          ctx.lineTo(wx * scaleX, wy * scaleY);
        }
        ctx.stroke();
      }

      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(agent.heading);
      ctx.fillStyle = agent.alive ? "#5ac8ff" : "#555";
      ctx.beginPath();
      ctx.moveTo(8, 0);
      ctx.lineTo(-6, 5);
      ctx.lineTo(-6, -5);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      ctx.fillStyle = "#8fa3bf";
      ctx.font = "10px monospace";
      ctx.fillText(agent.id, x + 8, y - 8);
    }
  }, [snapshot]);

  return <canvas ref={canvasRef} width={800} height={800} style={{ border: "1px solid #2a3040" }} />;
}
