export interface AgentState {
  id: string;
  x: number;
  y: number;
  heading: number;
  speed: number;
  alive: boolean;
  task_id: string | null;
  waypoints: [number, number][];
}

export interface Obstacle {
  x: number;
  y: number;
  radius: number;
}

export interface Zone {
  x: number;
  y: number;
  width: number;
  height: number;
  kind: string;
}

export interface WorldState {
  width: number;
  height: number;
  obstacles: Obstacle[];
  zones: Zone[];
}

export interface ReasoningLogEntry {
  trigger: string;
  reasoning: string;
  tasks: { id: string; description: string; x: number; y: number; priority: number }[];
}

export interface SimSnapshot {
  tick: number;
  world: WorldState;
  agents: AgentState[];
  reasoning_log: ReasoningLogEntry[];
}
