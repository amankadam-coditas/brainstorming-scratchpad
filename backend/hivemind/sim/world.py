"""World model: static obstacles, no-fly/comms-denied zones, and geometry helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
import math


@dataclass
class Obstacle:
    x: float
    y: float
    radius: float


@dataclass
class Zone:
    """A rectangular zone with a kind: 'no_fly' blocks movement, 'comms_denied' blocks radio."""

    x: float
    y: float
    width: float
    height: float
    kind: str = "comms_denied"

    def contains(self, x: float, y: float) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height


@dataclass
class World:
    width: float = 1000.0
    height: float = 1000.0
    obstacles: list[Obstacle] = field(default_factory=list)
    zones: list[Zone] = field(default_factory=list)

    def is_blocked(self, x: float, y: float, clearance: float = 0.0) -> bool:
        if not (0 <= x <= self.width and 0 <= y <= self.height):
            return True
        for obs in self.obstacles:
            if math.hypot(x - obs.x, y - obs.y) <= obs.radius + clearance:
                return True
        for zone in self.zones:
            if zone.kind == "no_fly" and zone.contains(x, y):
                return True
        return False

    def comms_available(self, x: float, y: float) -> bool:
        for zone in self.zones:
            if zone.kind == "comms_denied" and zone.contains(x, y):
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "obstacles": [{"x": o.x, "y": o.y, "radius": o.radius} for o in self.obstacles],
            "zones": [
                {"x": z.x, "y": z.y, "width": z.width, "height": z.height, "kind": z.kind}
                for z in self.zones
            ],
        }
