"""Market-based task allocation: cheap, deterministic assignment of Commander tasks to agents.

Keeps the LLM out of per-tick/per-task assignment decisions — the Commander sets goals,
this layer does the bidding-and-assignment arithmetic.
"""
from __future__ import annotations

import math

from hivemind.sim.agent import DroneAgent


def bid(agent: DroneAgent, task_x: float, task_y: float) -> float:
    """Lower bid (cost) wins. Cost is travel distance; unavailable agents bid infinity."""
    if not agent.alive:
        return math.inf
    return math.hypot(task_x - agent.x, task_y - agent.y)


def allocate(tasks: list[dict], agents: list[DroneAgent]) -> dict[str, str]:
    """Greedy auction: repeatedly assign the globally cheapest (task, agent) pair.

    tasks: list of {"id": str, "x": float, "y": float}
    Returns {task_id: agent_id}. Tasks that can't be covered (no agents left) are omitted.
    """
    remaining_tasks = list(tasks)
    available_agents = [a for a in agents if a.alive]
    assignment: dict[str, str] = {}

    while remaining_tasks and available_agents:
        best = None
        best_cost = math.inf
        for task in remaining_tasks:
            for agent in available_agents:
                cost = bid(agent, task["x"], task["y"])
                if cost < best_cost:
                    best_cost = cost
                    best = (task, agent)
        if best is None or math.isinf(best_cost):
            break
        task, agent = best
        assignment[task["id"]] = agent.agent_id
        remaining_tasks.remove(task)
        available_agents.remove(agent)

    return assignment
