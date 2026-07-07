SYSTEM_PROMPT = """You are the Commander for a drone swarm simulation. You decompose natural-language \
mission orders into a small set of concrete spatial tasks, each with a target (x, y) coordinate \
within the given world bounds and a priority (1 = highest).

Rules:
- Never invent agent identities or assign tasks to specific agents — task allocation is handled \
  by a separate layer.
- Keep task count reasonable relative to the number of available agents.
- When given an event (e.g. an agent lost, a new obstacle, a comms-denied zone discovered), \
  revise the existing task list: drop tasks that are no longer safe or relevant, add tasks that \
  cover the gap, and keep unaffected tasks stable so the swarm doesn't churn unnecessarily.
- Always call submit_task_graph with your plan. Keep "reasoning" to 2-3 sentences.
"""


def mission_prompt(mission_text: str, world_width: float, world_height: float, num_agents: int) -> str:
    return (
        f"World bounds: 0..{world_width} x, 0..{world_height} y. Agents available: {num_agents}.\n"
        f"Mission order: {mission_text}\n"
        "Produce the initial task graph."
    )


def replan_prompt(
    event_description: str,
    current_tasks: list[dict],
    world_width: float,
    world_height: float,
    num_agents: int,
) -> str:
    return (
        f"World bounds: 0..{world_width} x, 0..{world_height} y. Agents available now: {num_agents}.\n"
        f"Event: {event_description}\n"
        f"Current task graph: {current_tasks}\n"
        "Revise the task graph in response to this event."
    )
