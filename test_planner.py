from core.state import ProjectState
from agents.planner import PlannerAgent

state = ProjectState(
    problem="Reduce food waste in restaurants"
)

planner = PlannerAgent()

state = planner.run(state)

print(state)