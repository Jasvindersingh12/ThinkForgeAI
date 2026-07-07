from agents.base_agent import BaseAgent
from core.provider import provider
from core.state import ProjectState

from prompts.debate_prompt import DEBATE_PROMPT


class DebateAgent(BaseAgent):

    def __init__(self):

        super().__init__("Expert Debate")

    def run(self, state: ProjectState):

        self.log("Starting expert debate...")

        expert_text = ""

        for expert in state.experts:

            expert_text += (
                f"{expert['name']} "
                f"({expert['role']})\n"
            )

        prompt = DEBATE_PROMPT.substitute(

            problem=state.problem,

            experts=expert_text

        )

        result = provider.ask_json(

            prompt,

            "debate.json"

        )

        state.debate = result

        state.confidence = result.get(

            "confidence",

            0.80

        )

        self.log("Debate finished.")

        return state