from prompts.planner_prompt import PLANNER_PROMPT

from core.provider import provider

from core.state import ProjectState

from agents.base_agent import BaseAgent


class PlannerAgent(

    BaseAgent

):

    def __init__(self):

        super().__init__("Planner")

    def run(

        self,

        state: ProjectState

    ):

        self.log("Planning...")

        prompt = PLANNER_PROMPT.substitute(

            problem=state.problem

        )

        result = provider.ask_json(

            prompt,

            "planner.json"

        )

        state.objective = result["objective"]

        state.domain = result["domain"]

        state.stakeholders = result["stakeholders"]

        state.constraints = result["constraints"]

        state.assumptions = result["assumptions"]

        self.log("Done")

        return state