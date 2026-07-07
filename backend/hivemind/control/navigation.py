"""Waypoint-following navigation. Deterministic, runs every tick."""
from __future__ import annotations

from hivemind.sim.agent import MAX_SPEED, DroneAgent

ARRIVAL_SLOWDOWN_RADIUS = 40.0


def desired_heading_and_speed(agent: DroneAgent) -> tuple[float, float]:
    if not agent.waypoints:
        return agent.heading, 0.0

    tx, ty = agent.waypoints[0]
    heading = agent.desired_heading_to(tx, ty)

    import math

    dist = math.hypot(tx - agent.x, ty - agent.y)
    speed = MAX_SPEED if dist > ARRIVAL_SLOWDOWN_RADIUS else MAX_SPEED * (dist / ARRIVAL_SLOWDOWN_RADIUS)
    return heading, speed
