"""
Shared state across the ThinkForge AI pipeline.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ProjectState(BaseModel):

    # ==========================
    # User Input
    # ==========================
    problem: str = ""
    objective: str = ""

    # ==========================
    # Analysis
    # ==========================
    domain: str = ""

    stakeholders: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)

    # ==========================
    # Expert System
    # ==========================
    experts: List[Dict[str, Any]] = Field(default_factory=list)

    expert_opinions: Dict[str, Any] = Field(default_factory=dict)

    debate: Dict[str, Any] = Field(default_factory=dict)

    # NEW
    debate_history: List[Dict[str, Any]] = Field(default_factory=list)

    # NEW
    execution_history: List[str] = Field(default_factory=list)

    # ==========================
    # Final Outputs
    # ==========================
    executive_summary: str = ""

    technical_report: str = ""

    architecture: Dict[str, Any] = Field(default_factory=dict)

    budget: Dict[str, Any] = Field(default_factory=dict)

    timeline: List[Dict[str, Any]] = Field(default_factory=list)

    risks: List[Dict[str, Any]] = Field(default_factory=list)

    kpis: List[str] = Field(default_factory=list)

    implementation_plan: Dict[str, Any] = Field(default_factory=dict)

    ppt_content: List[Dict[str, Any]] = Field(default_factory=list)

    confidence: float = 0.0

    # ==========================
    # Downloads
    # ==========================
    report_path: str = ""
    ppt_path: str = ""
    diagram_path: str = ""