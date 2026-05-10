

class Pipelines:
    BRAINSTORM = "Brainstorm"
    PLAN = "Plan"
    IMPLEMENT = "Implement"
    REFINEMENT = "Refinement"

class Agents:
    BRAINSTORM = "brainstorm"
    PLAN = "plan"
    PROJECT_MANAGER = "project_manager"
    TASK_DECOMPOSER = "task_decomposer"


PipelineAgents: dict[str, list[str]] = {
    Pipelines.BRAINSTORM: [Agents.BRAINSTORM],
    Pipelines.PLAN: [Agents.PLAN],
    Pipelines.IMPLEMENT: [Agents.PROJECT_MANAGER, Agents.TASK_DECOMPOSER]
}