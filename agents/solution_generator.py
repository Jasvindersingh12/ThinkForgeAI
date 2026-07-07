import json

from agents.base_agent import BaseAgent

from core.provider import provider

from core.state import ProjectState

from prompts.solution_prompt import SOLUTION_PROMPT


class SolutionGeneratorAgent(BaseAgent):

    def __init__(self):

        super().__init__("Chief Decision Agent")

    def run(self, state: ProjectState):

        self.log("Generating final solution...")

        prompt = SOLUTION_PROMPT.substitute(

            problem=state.problem,

            objective=state.objective,

            analysis=json.dumps(

                state.implementation_plan,

                indent=2

            ),

            debate=json.dumps(

                state.debate,

                indent=2

            )

        )

        result = provider.ask_json(

            prompt,

            "solution.json"

        )

        state.executive_summary = result["executive_summary"]

        state.technical_report = result["technical_report"]

        state.architecture = result["architecture"]

        state.budget = result["budget"]

        state.timeline = result["timeline"]

        state.risks = result["risks"]

        state.kpis = result["kpis"]

        state.implementation_plan = result["implementation_plan"]

        state.ppt_content = result["ppt"]

        state.architecture = result["architecture"]

        state.confidence = 0.96

        self.log("Solution package created.")

        return state