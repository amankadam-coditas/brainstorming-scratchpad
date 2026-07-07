"""LLM-backed mission Commander: decomposes/replans task graphs. No flight-control authority."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import anthropic

from hivemind.commander.prompts import SYSTEM_PROMPT, mission_prompt, replan_prompt
from hivemind.commander.schemas import TASK_GRAPH_TOOL

MODEL = "claude-sonnet-5"


@dataclass
class ReasoningLogEntry:
    trigger: str
    reasoning: str
    tasks: list[dict]


@dataclass
class Commander:
    client: anthropic.Anthropic = field(default_factory=lambda: anthropic.Anthropic())
    tasks: list[dict] = field(default_factory=list)
    log: list[ReasoningLogEntry] = field(default_factory=list)

    def _call(self, user_prompt: str) -> tuple[str, list[dict]]:
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[TASK_GRAPH_TOOL],
            tool_choice={"type": "tool", "name": "submit_task_graph"},
            messages=[{"role": "user", "content": user_prompt}],
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_task_graph":
                return block.input["reasoning"], block.input["tasks"]
        raise RuntimeError("Commander did not return a task graph")

    def plan_mission(self, mission_text: str, world_width: float, world_height: float, num_agents: int) -> list[dict]:
        prompt = mission_prompt(mission_text, world_width, world_height, num_agents)
        reasoning, tasks = self._call(prompt)
        self.tasks = tasks
        self.log.append(ReasoningLogEntry(trigger=f"mission: {mission_text}", reasoning=reasoning, tasks=tasks))
        return tasks

    def replan(self, event_description: str, world_width: float, world_height: float, num_agents: int) -> list[dict]:
        prompt = replan_prompt(event_description, self.tasks, world_width, world_height, num_agents)
        reasoning, tasks = self._call(prompt)
        self.tasks = tasks
        self.log.append(ReasoningLogEntry(trigger=f"event: {event_description}", reasoning=reasoning, tasks=tasks))
        return tasks

    def log_as_dicts(self) -> list[dict]:
        return [{"trigger": e.trigger, "reasoning": e.reasoning, "tasks": e.tasks} for e in self.log]
