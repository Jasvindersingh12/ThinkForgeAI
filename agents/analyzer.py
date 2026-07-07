from agents.base_agent import BaseAgent
from core.provider import provider
from core.state import ProjectState
from prompts.analyzer_prompt import ANALYZER_PROMPT


class AnalyzerAgent(BaseAgent):

    def __init__(self):
        super().__init__("Analyzer")

    def run(self, state: ProjectState) -> ProjectState:

        self.log("Analyzing problem...")

        prompt = ANALYZER_PROMPT.substitute(
            problem=state.problem,
            objective=state.objective
        )

        result = provider.ask_json(
            prompt,
            "analyzer.json"
        )

        state.implementation_plan["analysis"] = result

        self.log("Analysis completed.")

        return state