"""FastAPI server: REST for mission/event injection, WebSocket for live sim + reasoning stream."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from hivemind.allocation.market import allocate
from hivemind.commander.commander import Commander
from hivemind.sim.agent import DroneAgent
from hivemind.sim.engine import TICK_DT, SimulationEngine

app = FastAPI(title="Hivemind Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SimulationEngine()
commander = Commander()
connected_sockets: set[WebSocket] = set()


def _seed_default_swarm(num_agents: int = 8) -> None:
    engine.agents.clear()
    for i in range(num_agents):
        engine.add_agent(
            DroneAgent(agent_id=f"drone-{i+1}", x=50 + (i % 4) * 40, y=50 + (i // 4) * 40)
        )


_seed_default_swarm()


class MissionRequest(BaseModel):
    mission_text: str


class EventRequest(BaseModel):
    kind: str  # "agent_lost" | "obstacle" | "comms_denied_zone"
    agent_id: str | None = None
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    radius: float | None = None


def _apply_allocation() -> None:
    tasks = commander.tasks
    living = engine.alive_agents()
    assignment = allocate(tasks, living)
    task_by_id = {t["id"]: t for t in tasks}
    for task_id, agent_id in assignment.items():
        agent = engine.agents[agent_id]
        task = task_by_id[task_id]
        agent.task_id = task_id
        agent.set_waypoints([(task["x"], task["y"])])


@app.post("/mission")
def start_mission(req: MissionRequest):
    commander.plan_mission(
        req.mission_text, engine.world.width, engine.world.height, len(engine.alive_agents())
    )
    _apply_allocation()
    return {"tasks": commander.tasks, "log": commander.log_as_dicts()[-1:]}


@app.post("/event")
def inject_event(req: EventRequest):
    description = req.kind
    if req.kind == "agent_lost" and req.agent_id:
        engine.kill_agent(req.agent_id)
        description = f"Agent {req.agent_id} lost contact and is no longer available."
    elif req.kind == "obstacle" and req.x is not None and req.y is not None:
        engine.add_obstacle(req.x, req.y, req.radius or 40.0)
        description = f"New obstacle discovered at ({req.x}, {req.y}), radius {req.radius or 40.0}."
    elif req.kind == "comms_denied_zone" and req.x is not None:
        engine.add_zone(req.x, req.y, req.width or 150.0, req.height or 150.0, "comms_denied")
        description = f"Comms-denied zone discovered near ({req.x}, {req.y})."

    commander.replan(description, engine.world.width, engine.world.height, len(engine.alive_agents()))
    _apply_allocation()
    return {"tasks": commander.tasks, "log": commander.log_as_dicts()[-1:]}


@app.get("/state")
def get_state():
    return engine.snapshot()


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_sockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_sockets.discard(websocket)


async def sim_loop() -> None:
    while True:
        engine.tick()
        payload = engine.snapshot()
        payload["reasoning_log"] = commander.log_as_dicts()
        stale = []
        for ws in connected_sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            connected_sockets.discard(ws)
        await asyncio.sleep(TICK_DT)


@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(sim_loop())
