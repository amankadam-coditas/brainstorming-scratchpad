"""Structured output schema for the Commander's mission decomposition (OpenAI tool-call format)."""
from __future__ import annotations

TASK_GRAPH_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_task_graph",
        "description": "Submit the decomposed mission as a list of spatial tasks for the swarm.",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of the plan and why it addresses the mission/event.",
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Short unique task id, e.g. 'recon-north'"},
                            "description": {"type": "string"},
                            "x": {"type": "number", "description": "Target x coordinate in world units"},
                            "y": {"type": "number", "description": "Target y coordinate in world units"},
                            "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                        },
                        "required": ["id", "description", "x", "y", "priority"],
                    },
                },
            },
            "required": ["reasoning", "tasks"],
        },
    },
}
