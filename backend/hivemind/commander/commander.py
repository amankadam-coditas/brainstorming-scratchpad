"""LLM-backed mission Commander: decomposes/replans task graphs. No flight-control authority.

Provider-agnostic: uses the OpenAI SDK's chat-completions/tool-calling interface, which is
implemented by OpenAI, Azure OpenAI, and most third-party/proxy/local model servers. Point it
at a different provider by setting OPENAI_BASE_URL / OPENAI_API_KEY (or passing base_url/
api_key directly) and LLM_MODEL to that provider's model name.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from openai import OpenAI

from hivemind.commander.prompts import SYSTEM_PROMPT, mission_prompt, replan_prompt
from hivemind.commander.schemas import TASK_GRAPH_TOOL

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


@dataclass
class ReasoningLogEntry:
    trigger: str
    reasoning: str
    tasks: list[dict]


@dataclass
class Commander:
    client: OpenAI = field(default_factory=lambda: OpenAI())
    model: str = DEFAULT_MODEL
    tasks: list[dict] = field(default_factory=list)
    log: list[ReasoningLogEntry] = field(default_factory=list)

    def _call(self, user_prompt: str) -> tuple[str, list[dict]]:
        response = self.client.chat.completions.create(
            model=self.model,
            tools=[TASK_GRAPH_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_task_graph"}},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        tool_calls = response.choices[0].message.tool_calls or []
        for call in tool_calls:
            if call.function.name == "submit_task_graph":
                args = json.loads(call.function.arguments)
                return args["reasoning"], args["tasks"]
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
