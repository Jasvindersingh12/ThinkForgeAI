from agents.base_agent import BaseAgent
from core.provider import provider
from core.state import ProjectState
from prompts.experts_prompt import EXPERTS_PROMPT


class ExpertGeneratorAgent(BaseAgent):

    def __init__(self):
        super().__init__("Expert Generator")

    def run(self, state: ProjectState) -> ProjectState:

        self.log("Generating expert council...")

        prompt = EXPERTS_PROMPT.substitute(
            problem=state.problem
        )

        result = provider.ask_json(
            prompt,
            "experts.json"
        )

        state.experts = result["experts"]

        self.log(f"{len(state.experts)} experts selected.")

        return state