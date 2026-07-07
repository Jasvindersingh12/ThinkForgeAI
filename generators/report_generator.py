"""
ThinkForge AI
PDF Report Generator

Generates a professional technical report from the
ProjectState object.

Author:
ThinkForge AI
"""

from pathlib import Path
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from core.state import ProjectState


class ReportGenerator:

    """
    Creates a professional PDF report.
    """

    def __init__(self):

        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(

            "Title",

            parent=self.styles["Heading1"],

            alignment=TA_CENTER,

            fontSize=24,

            spaceAfter=20

        )

        self.heading = self.styles["Heading2"]

        self.normal = self.styles["BodyText"]

        self.output_dir = Path(

            "outputs/reports"

        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    #######################################################

    def generate(

        self,

        state: ProjectState

    ) -> Path:

        filename = (

            self.output_dir /

            "ThinkForge_Report.pdf"

        )

        doc = SimpleDocTemplate(

            str(filename),

            rightMargin=40,

            leftMargin=40,

            topMargin=40,

            bottomMargin=40

        )

        story: List = []

        ###################################################
        # Cover
        ###################################################

        story.append(

            Paragraph(

                "ThinkForge AI",

                self.title_style

            )

        )

        story.append(

            Paragraph(

                "<b>Turn Problems Into Deployable Solutions</b>",

                self.normal

            )

        )

        story.append(

            Spacer(

                1,

                0.5 * inch

            )

        )

        story.append(

            Paragraph(

                f"<b>Problem</b><br/><br/>{state.problem}",

                self.normal

            )

        )

        story.append(

            Spacer(

                1,

                0.3 * inch

            )

        )

        story.append(

            Paragraph(

                f"Generated : {datetime.now()}",

                self.normal

            )

        )

        story.append(

            PageBreak()

        )

        ###################################################
        # Executive Summary
        ###################################################

        story.append(

            Paragraph(

                "Executive Summary",

                self.heading

            )

        )

        story.append(

            Paragraph(

                state.executive_summary,

                self.normal

            )

        )

        story.append(

            Spacer(

                1,

                0.3 * inch

            )

        )

        ###################################################
        # Problem Overview
        ###################################################

        story.append(

            Paragraph(

                "Problem Statement",

                self.heading

            )

        )

        story.append(

            Paragraph(

                state.problem,

                self.normal

            )

        )

        story.append(

            Spacer(

                1,

                0.2 * inch

            )

        )

        ###################################################
        # Objective
        ###################################################

        story.append(

            Paragraph(

                "Objective",

                self.heading

            )

        )

        story.append(

            Paragraph(

                state.objective,

                self.normal

            )

        )

        story.append(

            Spacer(

                1,

                0.2 * inch

            )

        )

        ###################################################
        # Domain
        ###################################################

        story.append(

            Paragraph(

                "Business Domain",

                self.heading

            )

        )

        story.append(

            Paragraph(

                state.domain,

                self.normal

            )

        )

        story.append(

            PageBreak()

        )

        ###################################################
        # Stakeholders
        ###################################################

        story.append(

            Paragraph(

                "Stakeholders",

                self.heading

            )

        )

        for stakeholder in state.stakeholders:

            story.append(

                Paragraph(

                    f"• {stakeholder}",

                    self.normal

                )

            )

        story.append(

            Spacer(

                1,

                0.3 * inch

            )

        )

        ###################################################
        # Constraints
        ###################################################

        story.append(

            Paragraph(

                "Constraints",

                self.heading

            )

        )

        for constraint in state.constraints:

            story.append(

                Paragraph(

                    f"• {constraint}",

                    self.normal

                )

            )

        story.append(

            Spacer(

                1,

                0.3 * inch

            )

        )

        ###################################################
        # Assumptions
        ###################################################

        story.append(

            Paragraph(

                "Assumptions",

                self.heading

            )

        )

        for assumption in state.assumptions:

            story.append(

                Paragraph(

                    f"• {assumption}",

                    self.normal

                )

            )
                    ###################################################
            # Expert Council
            ###################################################

            story.append(

                PageBreak()

            )

            story.append(

                Paragraph(

                    "Expert Council",

                    self.heading

                )

            )

            if state.experts:

                data = [

                    [

                        "Expert",

                        "Role",

                        "Reason"

                    ]

                ]

                for expert in state.experts:

                    data.append(

                        [

                            expert.get("name", ""),

                            expert.get("role", ""),

                            expert.get("reason", "")

                        ]

                    )

                table = Table(

                    data,

                    colWidths=[2 * inch, 2 * inch, 3 * inch]

                )

                table.setStyle(

                    TableStyle([

                        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),

                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

                        ("TOPPADDING", (0, 1), (-1, -1), 6)

                    ])

                )

                story.append(table)

            story.append(

                Spacer(

                    1,

                    0.4 * inch

                )

            )

            ###################################################
            # Debate Summary
            ###################################################

            story.append(

                Paragraph(

                    "Expert Debate",

                    self.heading

                )

            )

            if state.debate:

                for item in state.debate.get(

                    "discussion",

                    []

                ):

                    story.append(

                        Paragraph(

                            f"<b>{item['expert']}</b><br/>{item['opinion']}",

                            self.normal

                        )

                    )

                    story.append(

                        Spacer(

                            1,

                            0.1 * inch

                        )

                    )

                story.append(

                    Spacer(

                        1,

                        0.2 * inch

                    )

                )

                story.append(

                    Paragraph(

                        "<b>Final Consensus</b>",

                        self.heading

                    )

                )

                story.append(

                    Paragraph(

                        state.debate.get(

                            "final_consensus",

                            ""

                        ),

                        self.normal

                    )

                )

            ###################################################
            # Architecture
            ###################################################

            story.append(

                PageBreak()

            )

            story.append(

                Paragraph(

                    "Solution Architecture",

                    self.heading

                )

            )

            if state.architecture:

                story.append(

                    Paragraph(

                        state.architecture.get(

                            "title",

                            ""

                        ),

                        self.normal

                    )

                )

                story.append(

                    Spacer(

                        1,

                        0.2 * inch

                    )

                )

                for component in state.architecture.get(

                    "components",

                    []

                ):

                    story.append(

                        Paragraph(

                            f"• {component}",

                            self.normal

                        )

                    )

            ###################################################
            # Budget
            ###################################################

            story.append(

                Spacer(

                    1,

                    0.4 * inch

                )

            )

            story.append(

                Paragraph(

                    "Estimated Budget",

                    self.heading

                )

            )

            budget_data = [

                [

                    "Item",

                    "Estimated Cost"

                ]

            ]

            for item in state.budget.get(

                "items",

                []

            ):

                budget_data.append(

                    [

                        item["name"],

                        item["cost"]

                    ]

                )

            budget_data.append(

                [

                    "TOTAL",

                    state.budget.get(

                        "total",

                        ""

                    )

                ]

            )

            budget_table = Table(

                budget_data,

                colWidths=[4 * inch, 2 * inch]

            )

            budget_table.setStyle(

                TableStyle([

                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),

                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                    ("GRID", (0, 0), (-1, -1), 1, colors.black),

                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10)

                ])

            )

            story.append(

                budget_table

            )

            ###################################################
            # Timeline
            ###################################################

            story.append(

                Spacer(

                    1,

                    0.4 * inch

                )

            )

            story.append(

                Paragraph(

                    "Implementation Timeline",

                    self.heading

                )

            )

            timeline_data = [

                [

                    "Phase",

                    "Duration"

                ]

            ]

            for phase in state.timeline:

                timeline_data.append(

                    [

                        phase["phase"],

                        phase["duration"]

                    ]

                )

            timeline_table = Table(

                timeline_data,

                colWidths=[4 * inch, 2 * inch]

            )

            timeline_table.setStyle(

                TableStyle([

                    ("BACKGROUND", (0, 0), (-1, 0), colors.navy),

                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                    ("GRID", (0, 0), (-1, -1), 1, colors.black),

                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8)

                ])

            )

            story.append(

                timeline_table

            )

            ###################################################
            # Risks
            ###################################################

            story.append(

                PageBreak()

            )

            story.append(

                Paragraph(

                    "Risk Analysis",

                    self.heading

                )

            )

            for risk in state.risks:

                story.append(

                    Paragraph(

                        f"<b>{risk['risk']}</b>",

                        self.normal

                    )

                )

                story.append(

                    Paragraph(

                        f"Mitigation: {risk['mitigation']}",

                        self.normal

                    )

                )

                story.append(

                    Spacer(

                        1,

                        0.15 * inch

                    )

                )

            ###################################################
            # KPI
            ###################################################

            story.append(

                Paragraph(

                    "Success KPIs",

                    self.heading

                )

            )

            for kpi in state.kpis:

                story.append(

                    Paragraph(

                        f"• {kpi}",

                        self.normal

                    )

                )
                        ###################################################
                # Implementation Roadmap
                ###################################################

                story.append(
                    Spacer(1, 0.3 * inch)
                )

                story.append(
                    Paragraph(
                        "Implementation Roadmap",
                        self.heading
                    )
                )

                if state.implementation_plan:

                    if isinstance(state.implementation_plan, list):

                        for step in state.implementation_plan:

                            story.append(
                                Paragraph(
                                    f"• {step}",
                                    self.normal
                                )
                            )

                    elif isinstance(state.implementation_plan, dict):

                        for key, value in state.implementation_plan.items():

                            story.append(
                                Paragraph(
                                    f"<b>{key}</b>",
                                    self.heading
                                )
                            )

                            if isinstance(value, list):

                                for item in value:

                                    story.append(
                                        Paragraph(
                                            f"• {item}",
                                            self.normal
                                        )
                                    )

                            else:

                                story.append(
                                    Paragraph(
                                        str(value),
                                        self.normal
                                    )
                                )

                ###################################################
                # Confidence Score
                ###################################################

                story.append(
                    Spacer(1, 0.4 * inch)
                )

                story.append(
                    Paragraph(
                        "AI Confidence Score",
                        self.heading
                    )
                )

                confidence = round(
                    state.confidence * 100,
                    2
                )

                story.append(
                    Paragraph(
                        f"The overall confidence of this solution is "
                        f"<b>{confidence}%</b>.",
                        self.normal
                    )
                )

                ###################################################
                # Technical Report
                ###################################################

                if state.technical_report:

                    story.append(
                        PageBreak()
                    )

                    story.append(
                        Paragraph(
                            "Technical Report",
                            self.heading
                        )
                    )

                    story.append(
                        Paragraph(
                            state.technical_report,
                            self.normal
                        )
                    )

                ###################################################
                # Conclusion
                ###################################################

                story.append(
                    PageBreak()
                )

                story.append(
                    Paragraph(
                        "Conclusion",
                        self.heading
                    )
                )

                story.append(
                    Paragraph(
                        """
        This solution package was automatically generated
        by ThinkForge AI.

        The recommendations combine business analysis,
        expert collaboration, AI reasoning and
        implementation planning into one actionable
        solution.

        Generated outputs include:

        • Executive Summary

        • Technical Report

        • Budget Estimation

        • Timeline

        • Risk Analysis

        • KPIs

        • Implementation Roadmap

        • Architecture

        • PowerPoint Presentation

        The report should be reviewed by domain experts
        before production deployment.
                        """,
                        self.normal
                    )
                )

                ###################################################
                # Footer
                ###################################################

                story.append(
                    Spacer(
                        1,
                        0.5 * inch
                    )
                )

                story.append(
                    Paragraph(
                        "<b>ThinkForge AI</b><br/>"
                        "Turn Problems Into Deployable Solutions",
                        self.normal
                    )
                )

                ###################################################
                # Build PDF
                ###################################################

                doc.title = "ThinkForge AI Report"

                doc.author = "ThinkForge AI"

                doc.subject = "AI Solution Package"

                doc.build(story)

                return filename