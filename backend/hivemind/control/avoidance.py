"""Deterministic local collision avoidance (reciprocal velocity obstacles, simplified).

This layer never calls the LLM — it runs every tick and must be cheap and predictable.
"""
from __future__ import annotations

import math

from hivemind.sim.agent import DroneAgent
from hivemind.sim.world import World

AVOIDANCE_RADIUS = 60.0
AGENT_CLEARANCE = 15.0


def avoid_heading(agent: DroneAgent, others: list[DroneAgent], world: World, desired_heading: float) -> float:
    """Nudge the desired heading away from nearby agents and static obstacles."""
    push_x, push_y = 0.0, 0.0

    for other in others:
        if other.agent_id == agent.agent_id or not other.alive:
            continue
        dx, dy = agent.x - other.x, agent.y - other.y
        dist = math.hypot(dx, dy)
        if 0 < dist < AVOIDANCE_RADIUS:
            weight = (AVOIDANCE_RADIUS - dist) / AVOIDANCE_RADIUS
            push_x += (dx / dist) * weight
            push_y += (dy / dist) * weight

    for obs in world.obstacles:
        dx, dy = agent.x - obs.x, agent.y - obs.y
        dist = math.hypot(dx, dy)
        margin = obs.radius + AGENT_CLEARANCE + AVOIDANCE_RADIUS
        if 0 < dist < margin:
            weight = (margin - dist) / margin
            push_x += (dx / dist) * weight * 2.0
            push_y += (dy / dist) * weight * 2.0

    if push_x == 0.0 and push_y == 0.0:
        return desired_heading

    avoid_heading_rad = math.atan2(push_y, push_x)
    goal_x, goal_y = math.cos(desired_heading), math.sin(desired_heading)
    avoid_x, avoid_y = math.cos(avoid_heading_rad), math.sin(avoid_heading_rad)

    blend = min(1.0, math.hypot(push_x, push_y))
    combined_x = goal_x * (1 - blend) + avoid_x * blend
    combined_y = goal_y * (1 - blend) + avoid_y * blend
    return math.atan2(combined_y, combined_x)
