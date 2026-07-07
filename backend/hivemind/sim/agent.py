"""Drone agent kinematics and status."""
from __future__ import annotations

from dataclasses import dataclass, field
import math

MAX_SPEED = 40.0  # units/sec
MAX_TURN_RATE = math.pi  # rad/sec


@dataclass
class DroneAgent:
    agent_id: str
    x: float
    y: float
    heading: float = 0.0
    speed: float = 0.0
    comm_range: float = 250.0
    sensor_range: float = 120.0
    alive: bool = True
    task_id: str | None = None
    waypoints: list[tuple[float, float]] = field(default_factory=list)

    def set_waypoints(self, waypoints: list[tuple[float, float]]) -> None:
        self.waypoints = list(waypoints)

    def desired_heading_to(self, tx: float, ty: float) -> float:
        return math.atan2(ty - self.y, tx - self.x)

    def step(self, dt: float, desired_heading: float, desired_speed: float) -> None:
        if not self.alive:
            return
        heading_delta = _wrap_angle(desired_heading - self.heading)
        max_delta = MAX_TURN_RATE * dt
        heading_delta = max(-max_delta, min(max_delta, heading_delta))
        self.heading = _wrap_angle(self.heading + heading_delta)

        speed_target = max(0.0, min(MAX_SPEED, desired_speed))
        self.speed += max(-20.0 * dt, min(20.0 * dt, speed_target - self.speed))

        self.x += math.cos(self.heading) * self.speed * dt
        self.y += math.sin(self.heading) * self.speed * dt

    def advance_waypoint_if_reached(self, threshold: float = 8.0) -> None:
        if not self.waypoints:
            return
        tx, ty = self.waypoints[0]
        if math.hypot(tx - self.x, ty - self.y) <= threshold:
            self.waypoints.pop(0)

    def to_dict(self) -> dict:
        return {
            "id": self.agent_id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "heading": round(self.heading, 3),
            "speed": round(self.speed, 2),
            "alive": self.alive,
            "task_id": self.task_id,
            "waypoints": self.waypoints,
        }


def _wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi
