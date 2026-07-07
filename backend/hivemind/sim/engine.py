"""Tick-based simulation engine. Owns world + agent state, applies classical control each tick."""
from __future__ import annotations

from dataclasses import dataclass, field

from hivemind.control.avoidance import avoid_heading
from hivemind.control.navigation import desired_heading_and_speed
from hivemind.sim.agent import DroneAgent
from hivemind.sim.world import Obstacle, World, Zone

TICK_DT = 0.1  # seconds


@dataclass
class SimulationEngine:
    world: World = field(default_factory=World)
    agents: dict[str, DroneAgent] = field(default_factory=dict)
    tick_count: int = 0

    def add_agent(self, agent: DroneAgent) -> None:
        self.agents[agent.agent_id] = agent

    def kill_agent(self, agent_id: str) -> DroneAgent | None:
        agent = self.agents.get(agent_id)
        if agent:
            agent.alive = False
            agent.waypoints = []
        return agent

    def add_obstacle(self, x: float, y: float, radius: float) -> Obstacle:
        obs = Obstacle(x=x, y=y, radius=radius)
        self.world.obstacles.append(obs)
        return obs

    def add_zone(self, x: float, y: float, width: float, height: float, kind: str) -> Zone:
        zone = Zone(x=x, y=y, width=width, height=height, kind=kind)
        self.world.zones.append(zone)
        return zone

    def alive_agents(self) -> list[DroneAgent]:
        return [a for a in self.agents.values() if a.alive]

    def tick(self) -> None:
        living = self.alive_agents()
        for agent in living:
            agent.advance_waypoint_if_reached()
            heading, speed = desired_heading_and_speed(agent)
            heading = avoid_heading(agent, living, self.world, heading)
            agent.step(TICK_DT, heading, speed)
        self.tick_count += 1

    def snapshot(self) -> dict:
        return {
            "tick": self.tick_count,
            "world": self.world.to_dict(),
            "agents": [a.to_dict() for a in self.agents.values()],
        }
