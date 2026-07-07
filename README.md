# Hivemind Demo

A small demo swarm-autonomy system inspired by Shield AI's Hivemind, scoped for simulation
rather than real hardware. GenAI is deliberately kept out of the flight-critical loop — it sits
one layer up, as a mission "Commander" that decomposes natural-language orders into spatial
tasks and replans when the world changes.

## Architecture

- **Sim core** (`backend/hivemind/sim`) — 2D world with obstacles and comms-denied/no-fly zones,
  tick-based drone kinematics.
- **Classical control** (`backend/hivemind/control`) — deterministic waypoint navigation and
  local collision avoidance. No LLM calls, runs every tick.
- **Task allocation** (`backend/hivemind/allocation`) — greedy auction assigning Commander tasks
  to agents by travel cost. Keeps the LLM out of per-tick assignment decisions.
- **Commander** (`backend/hivemind/commander`) — LLM-backed mission planner using the OpenAI SDK's
  chat-completions/tool-calling interface (provider-agnostic: works with OpenAI, Azure OpenAI, or
  any OpenAI-compatible endpoint via `OPENAI_BASE_URL`/`OPENAI_API_KEY`). Takes a mission string,
  returns a structured task graph via tool call, and replans on injected events (agent lost, new
  obstacle, comms-denied zone discovered).
- **Server** (`backend/hivemind/server.py`) — FastAPI REST endpoints (`/mission`, `/event`) plus
  a WebSocket (`/ws`) streaming live sim state and the Commander's reasoning log.
- **Dashboard** (`frontend/`) — React + canvas swarm visualization, live reasoning log panel.

## Running it

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
# Optional: point at any OpenAI-compatible provider/proxy instead of api.openai.com
export OPENAI_BASE_URL=https://your-provider.example.com/v1
# Optional: model name for that provider (defaults to gpt-4o-mini)
export LLM_MODEL=gpt-4o-mini
python -m hivemind.main
```

Server runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at `http://localhost:5173`.

## Demo flow

1. Open the dashboard, edit the mission text if you like, click **Start Mission**.
2. Watch the Commander's reasoning log and the swarm converging on assigned targets.
3. Click **Inject: Lose Random Agent** to simulate an agent going dark — the Commander
   replans and the log shows the updated task graph.

## Notes / next steps

- v1 uses a hand-rolled 2D sim for speed; swapping in ROS2/Gazebo would add real physics and
  3D fidelity at the cost of setup complexity.
- The allocator is a simple greedy auction; a real system would want capability-aware bidding
  (payload, remaining fuel, sensor type) rather than pure distance.
- No authentication/production hardening — this is a demo, not a deployable system.
