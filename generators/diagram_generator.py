"""
ThinkForge AI

Architecture Diagram Generator

Creates:

1. Mermaid Diagram (.md)

2. Graphviz Diagram (.png)

3. DOT File (.dot)
"""

from pathlib import Path

from graphviz import Digraph

from core.state import ProjectState


class DiagramGenerator:

    def __init__(self):

        self.output_dir = Path(

            "outputs/diagrams"

        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    ########################################################

    def generate_mermaid(

        self,

        state: ProjectState

    ) -> Path:

        mermaid_file = (

            self.output_dir /

            "architecture.md"

        )

        if state.solution.get("mermaid"):

            diagram = state.solution["mermaid"]

        elif hasattr(

            state,

            "mermaid_diagram"

        ):

            diagram = state.mermaid_diagram

        else:

            diagram = """

            graph TD

            A[Problem]

            -->

            B[Planner]

            -->

            C[Analyzer]

            -->

            D[Expert Generator]

            -->

            E[Expert Debate]

            -->

            F[Chief Decision]

            -->

            G[Reports]

            -->

            H[PowerPoint]

            -->

            I[Deployment]

            """

        with open(

            mermaid_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(diagram)

        return mermaid_file

    ########################################################

    def generate_graphviz(

        self,

        state: ProjectState

    ) -> Path:

        graph = Digraph(

            "ThinkForge",

            format="png"

        )

        graph.attr(

            rankdir="LR"

        )

        graph.node(

            "A",

            "Problem"

        )

        graph.node(

            "B",

            "Planner"

        )

        graph.node(

            "C",

            "Analyzer"

        )

        graph.node(

            "D",

            "Experts"

        )

        graph.node(

            "E",

            "Debate"

        )

        graph.node(

            "F",

            "Solution"

        )

        graph.node(

            "G",

            "Reports"

        )

        graph.node(

            "H",

            "PowerPoint"

        )

        graph.node(

            "I",

            "Deployment"

        )

        graph.edge("A", "B")

        graph.edge("B", "C")

        graph.edge("C", "D")

        graph.edge("D", "E")

        graph.edge("E", "F")

        graph.edge("F", "G")

        graph.edge("G", "H")

        graph.edge("H", "I")
    
                ########################################################
        # Export Diagram
        ########################################################

        output_path = self.output_dir / "architecture"

        graph.render(

            filename=str(output_path),

            cleanup=True

        )

        return output_path.with_suffix(".png")

    ########################################################

    def generate_dot(

        self,

        state: ProjectState

    ) -> Path:

        dot_file = self.output_dir / "architecture.dot"

        dot_content = """
digraph ThinkForge {

    rankdir=LR;

    Problem -> Planner;

    Planner -> Analyzer;

    Analyzer -> ExpertGenerator;

    ExpertGenerator -> Debate;

    Debate -> Solution;

    Solution -> Reports;

    Reports -> PowerPoint;

    PowerPoint -> Deployment;

}
"""

        with open(

            dot_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(dot_content)

        return dot_file

    ########################################################

    def generate(

        self,

        state: ProjectState

    ) -> dict:

        files = {}

        try:

            files["mermaid"] = self.generate_mermaid(

                state

            )

        except Exception as e:

            print(

                "Mermaid generation failed:",

                e

            )

        try:

            files["graphviz"] = self.generate_graphviz(

                state

            )

        except Exception as e:

            print(

                "Graphviz generation failed:",

                e

            )

        try:

            files["dot"] = self.generate_dot(

                state

            )

        except Exception as e:

            print(

                "DOT generation failed:",

                e

            )

        return files