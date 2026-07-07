from abc import ABC, abstractmethod

from core.state import ProjectState


class BaseAgent(ABC):

    def __init__(

        self,

        name: str

    ):

        self.name = name

    def log(

        self,

        message: str

    ):

        print(

            f"[{self.name}] {message}"

        )

    @abstractmethod

    def run(

        self,

        state: ProjectState

    ) -> ProjectState:

        pass