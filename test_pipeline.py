from core.state import ProjectState

from agents.planner import PlannerAgent
from agents.analyzer import AnalyzerAgent
from agents.expert_generator import ExpertGeneratorAgent
from agents.debate import DebateAgent
from agents.solution_generator import SolutionGeneratorAgent

state = ProjectState(

    problem="Reduce food waste in restaurants"

)

pipeline = [

    PlannerAgent(),

    AnalyzerAgent(),

    ExpertGeneratorAgent(),

    DebateAgent(),

    SolutionGeneratorAgent()

]

for agent in pipeline:

    state = agent.run(state)

print("\n")

print("="*80)

print("EXECUTIVE SUMMARY")

print("="*80)

print(state.executive_summary)

print("\n")

print("="*80)

print("BUDGET")

print("="*80)

print(state.budget)

print("\n")

print("="*80)

print("TIMELINE")

print("="*80)

print(state.timeline)