"""
ThinkForge AI
=============

Main Streamlit application.

Turn Problems Into Deployable Solutions.

This file only touches the presentation layer (this file). The existing
backend pipeline (agents/, providers/, prompts/, core/, generators/) is
used exactly as-is and is never modified here.

Pipeline (unchanged):

    Planner -> Analyzer -> Expert Generator -> Debate -> Solution Generator
    -> Report Generator -> PowerPoint Generator -> Architecture Diagram Generator
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

from core.state import ProjectState

from agents.planner import PlannerAgent
from agents.analyzer import AnalyzerAgent
from agents.expert_generator import ExpertGeneratorAgent
from agents.debate import DebateAgent
from agents.solution_generator import SolutionGeneratorAgent

from generators.report_generator import ReportGenerator
from generators.ppt_generator import PPTGenerator
from generators.diagram_generator import DiagramGenerator


# =============================================================================
# Constants
# =============================================================================

APP_NAME = "ThinkForge AI"
APP_TAGLINE = "Turn Problems into Deployable Solutions"

HISTORY_DIR = Path("history")
REPORTS_DIR = Path("reports")
PPT_DIR = Path("ppt")
DIAGRAM_DIR = Path("diagram")

for _dir in (HISTORY_DIR, REPORTS_DIR, PPT_DIR, DIAGRAM_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Canonical pipeline steps, used for the animated status widget and the Logs tab.
PIPELINE_STEPS: List[str] = [
    "Planner",
    "Analyzer",
    "Experts",
    "Debate",
    "Solution",
    "PDF",
    "PPT",
    "Diagram",
]

# Fields captured from a ProjectState (or a mocked / loaded equivalent) so the
# UI can render identically whether the state was just generated, reloaded
# from disk, or produced by Mock Mode.
STATE_FIELDS: List[str] = [
    "problem",
    "objective",
    "domain",
    "executive_summary",
    "technical_report",
    "implementation_plan",
    "architecture",
    "budget",
    "timeline",
    "kpis",
    "risks",
    "experts",
    "debate",
    "confidence",
    "execution_history",
]


# =============================================================================
# Small generic helpers
# =============================================================================

def g(obj: Any, name: str, default: Any = None) -> Any:
    """Safe attribute getter that works for ProjectState, SimpleNamespace, or dicts."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def slugify(text: str, max_len: int = 48) -> str:
    """Turn free text into a filesystem-safe slug."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:max_len] or "untitled-project"


def auto_title(problem: str, max_words: int = 5, max_len: int = 40) -> str:
    """Derive a short, human-friendly project name from the problem statement."""
    words = re.sub(r"\s+", " ", problem.strip()).split(" ")
    title = " ".join(words[:max_words]).title()
    return (title[:max_len] + "...") if len(title) > max_len else (title or "Untitled Project")


def read_bytes(path: Optional[str]) -> Optional[bytes]:
    """Read a file as bytes if it exists, else None (used for download buttons)."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return p.read_bytes()


# =============================================================================
# Serialization: ProjectState <-> plain dict, for the history/*.json files
# =============================================================================

def serialize_state(state: Any) -> Dict[str, Any]:
    """Convert a ProjectState (or compatible object) into a JSON-safe dict."""
    if is_dataclass(state) and not isinstance(state, type):
        try:
            data = asdict(state)
            return {k: data.get(k) for k in STATE_FIELDS}
        except Exception:
            pass
    return {field: g(state, field) for field in STATE_FIELDS}


def deserialize_state(data: Dict[str, Any]) -> SimpleNamespace:
    """Rebuild a lightweight, read-only state object from a saved dict.

    This is intentionally NOT a ProjectState instance: reloaded projects are
    for viewing/downloading only and never re-enter the agent pipeline.
    """
    return SimpleNamespace(**{field: data.get(field) for field in STATE_FIELDS})


# =============================================================================
# Project history persistence (history/*.json)
# =============================================================================

def history_path(name: str) -> Path:
    return HISTORY_DIR / f"{slugify(name)}.json"


def save_project(name: str, state: Any, generated_files: Dict[str, Optional[str]]) -> None:
    """Persist a completed project so it survives across sessions."""
    record = {
        "name": name,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "state": serialize_state(state),
        "files": generated_files,
    }
    history_path(name).write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")


@st.cache_data(show_spinner=False)
def _read_history_file(path_str: str, mtime: float) -> Dict[str, Any]:
    """Cached read of a single history file, invalidated by mtime."""
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def list_projects() -> List[Dict[str, Any]]:
    """List saved projects, most recently saved first."""
    records = []
    for path in HISTORY_DIR.glob("*.json"):
        try:
            data = _read_history_file(str(path), path.stat().st_mtime)
            records.append({"file": path.name, **data})
        except Exception:
            continue
    records.sort(key=lambda r: r.get("saved_at", ""), reverse=True)
    return records


def load_project(filename: str) -> Optional[Dict[str, Any]]:
    path = HISTORY_DIR / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def delete_project(filename: str) -> None:
    path = HISTORY_DIR / filename
    if path.exists():
        path.unlink()
    _read_history_file.clear()


# =============================================================================
# Mock Mode: instant, offline sample data for demos / UI testing
# =============================================================================

def build_mock_state(problem: str, objective: str) -> SimpleNamespace:
    """Produce a fake-but-complete state so the UI can be exercised with no API calls."""
    return SimpleNamespace(
        problem=problem,
        objective=objective or "Improve efficiency, reduce cost, and increase reliability.",
        domain="General / Demo",
        executive_summary=(
            "This is a Mock Mode executive summary. It stands in for the real "
            "AI-generated summary so the workspace UI can be reviewed without "
            "calling any AI provider."
        ),
        technical_report=(
            "Mock technical report. Enable a real run (turn off Mock Mode) to "
            "generate an in-depth, model-authored technical analysis."
        ),
        implementation_plan=(
            "Mock implementation plan: Phase 1 discovery, Phase 2 build, "
            "Phase 3 pilot, Phase 4 rollout."
        ),
        architecture={
            "title": "Mock Reference Architecture",
            "components": [
                "API Gateway",
                "Multi-Agent Orchestrator",
                "Vector / Data Store",
                "Reporting & Dashboard Layer",
            ],
        },
        budget={
            "items": [
                {"Item": "Cloud Hosting", "Cost": "$500 / mo"},
                {"Item": "AI Provider Usage", "Cost": "$300 / mo"},
                {"Item": "Monitoring", "Cost": "$100 / mo"},
            ],
            "total": "$900 / mo",
        },
        timeline=[
            {"Phase": "Discovery", "Duration": "2 weeks"},
            {"Phase": "Build", "Duration": "4 weeks"},
            {"Phase": "Pilot", "Duration": "2 weeks"},
            {"Phase": "Rollout", "Duration": "1 week"},
        ],
        kpis=[
            "Reduce operating cost by 20%",
            "Cut manual processing time by 35%",
            "Reach 90%+ user satisfaction in pilot",
        ],
        risks=[
            {"risk": "Data Privacy", "mitigation": "Encrypt data at rest and in transit."},
            {"risk": "Adoption Resistance", "mitigation": "Run a guided pilot with training."},
        ],
        experts=[
            {"name": "AI Architect", "role": "Designs the technical architecture.",
             "reason": "Needed to translate the problem into a system design."},
            {"name": "Financial Expert", "role": "Analyzes budget, ROI, and cost risk.",
             "reason": "Needed to keep the solution within a realistic budget."},
            {"name": "Product Manager", "role": "Defines scope, KPIs, and rollout plan.",
             "reason": "Needed to keep the solution outcome-focused."},
        ],
        debate={
            "discussion": [
                {"expert": "AI Architect", "opinion": "A modular, microservice-based design will scale best."},
                {"expert": "Financial Expert", "opinion": "Keep monthly infrastructure spend under $1,000."},
                {"expert": "Product Manager", "opinion": "Prioritize a pilot with a single site before full rollout."},
            ],
            "final_consensus": "Adopt a cost-efficient, modular architecture validated by a limited pilot.",
        },
        confidence=0.87,
        execution_history=["Planner", "Analyzer", "Experts", "Debate", "Solution"],
    )


# =============================================================================
# Pipeline execution
# =============================================================================

def make_project_state(problem: str, objective: str) -> Any:
    """Instantiate ProjectState, passing objective through if the constructor accepts it."""
    try:
        return ProjectState(problem=problem, objective=objective)
    except TypeError:
        state = ProjectState(problem=problem)
        try:
            setattr(state, "objective", objective)
        except Exception:
            pass
        return state


def run_pipeline(problem: str, objective: str, mock: bool) -> Tuple[Any, Dict[str, Optional[str]]]:
    os.environ["THINKFORGE_MOCK"] = "1" if mock else "0"

    status_box = st.status("Running ThinkForge AI pipeline...", expanded=True)
    generated_files: Dict[str, Optional[str]] = {
        "pdf": None, "ppt": None, "diagram_png": None,
        "diagram_mermaid": None, "diagram_dot": None,
    }

    state = make_project_state(problem, objective)
    state.execution_history = getattr(state, "execution_history", []) or []

    agents = [
        ("Planner", PlannerAgent()),
        ("Analyzer", AnalyzerAgent()),
        ("Experts", ExpertGeneratorAgent()),
        ("Debate", DebateAgent()),
        ("Solution", SolutionGeneratorAgent()),
    ]

    for label, agent in agents:
        status_box.write(f"⏳ {label}...")
        try:
            state = agent.run(state)
        except Exception as exc:
            status_box.update(label=f"{label} failed", state="error")
            st.error(f"{getattr(agent, 'name', label)} failed.")
            st.exception(exc)
            st.stop()
        state.execution_history.append(getattr(agent, "name", label))
        status_box.write(f"✅ {label} complete")

    status_box.write("⏳ Generating PDF report...")
    generated_files["pdf"] = ReportGenerator().generate(state)
    status_box.write("✅ PDF report ready")

    status_box.write("⏳ Generating PowerPoint...")
    generated_files["ppt"] = PPTGenerator().generate(state)
    status_box.write("✅ PowerPoint ready")

    status_box.write("⏳ Generating architecture diagram...")
    diagram_files = DiagramGenerator().generate(state)
    generated_files["diagram_png"] = diagram_files.get("graphviz")
    generated_files["diagram_mermaid"] = diagram_files.get("mermaid")
    generated_files["diagram_dot"] = diagram_files.get("dot")
    status_box.write("✅ Diagram ready")

    status_box.update(label="Completed" + (" (Mock Mode)" if mock else ""), state="complete")
    return state, generated_files

# =============================================================================
# Styling
# =============================================================================

def inject_css(theme: str) -> None:
    """Modern, rounded, dark-mode-friendly workspace styling."""
    dark = theme == "Dark"
    card_bg = "#161b22" if dark else "#ffffff"
    card_border = "#2b3138" if dark else "#e6e8eb"
    text_muted = "#9aa4af" if dark else "#5c6672"
    accent = "#6c5ce7"

    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 1.5rem; max-width: 1200px; }}

        .tf-hero {{
            padding: 0.25rem 0 0.75rem 0;
        }}
        .tf-hero h1 {{
            font-size: 2.2rem;
            margin-bottom: 0.15rem;
            font-weight: 800;
        }}
        .tf-hero p {{
            color: {text_muted};
            font-size: 1.05rem;
            margin-top: 0;
        }}

        .tf-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.8rem;
        }}

        .tf-download-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 1rem;
            text-align: center;
            margin-bottom: 0.6rem;
        }}
        .tf-download-card h4 {{
            margin: 0.2rem 0 0.6rem 0;
        }}

        .tf-project-row button {{
            text-align: left !important;
        }}

        [data-testid="stMetricValue"] {{
            font-weight: 700;
            color: {accent};
        }}

        section[data-testid="stSidebar"] .stButton button {{
            border-radius: 10px;
        }}

        .stButton button {{
            border-radius: 10px;
            font-weight: 600;
        }}

        .tf-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            background: {accent}22;
            color: {accent};
            font-size: 0.78rem;
            font-weight: 700;
            margin-left: 0.4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Session state initialization
# =============================================================================

def init_session_state() -> None:
    defaults = {
        "current_state": None,
        "current_files": None,
        "current_name": None,
        "mock_mode": False,
        "theme": "Dark",
        "input_key_suffix": 0,
        "confirm_delete": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_new_project() -> None:
    """Clear the workspace so a fresh problem statement can be entered."""
    st.session_state.current_state = None
    st.session_state.current_files = None
    st.session_state.current_name = None
    st.session_state.input_key_suffix += 1


def open_project(record: Dict[str, Any]) -> None:
    st.session_state.current_state = deserialize_state(record.get("state", {}))
    st.session_state.current_files = record.get("files", {})
    st.session_state.current_name = record.get("name", "Untitled Project")


# =============================================================================
# Sidebar
# =============================================================================

@st.dialog("About ThinkForge AI")
def about_dialog() -> None:
    st.write(
        "**ThinkForge AI** is a multi-agent AI Solution Factory. It turns a "
        "problem statement into a deployable solution package: an expert "
        "council, a debated recommendation, a written report, a PowerPoint "
        "deck, and an architecture diagram."
    )
    st.write("Pipeline: Planner → Analyzer → Experts → Debate → Solution → "
             "Report → PowerPoint → Architecture Diagram.")
    st.caption("Built with Streamlit • Multi-Agent AI")
    if st.button("Close", use_container_width=True):
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### ⚙ ThinkForge AI")
        st.caption("AI Solution Workspace")
        st.markdown("---")

        if st.button("➕ New Project", use_container_width=True, type="primary"):
            start_new_project()
            st.rerun()

        st.markdown("#### 🗂 Saved Projects")
        projects = list_projects()

        if not projects:
            st.caption("No saved projects yet.")
        else:
            for record in projects:
                name = record.get("name", "Untitled Project")
                filename = record["file"]
                col_open, col_del = st.columns([5, 1])
                with col_open:
                    if st.button(f"📄 {name}", key=f"open_{filename}", use_container_width=True):
                        open_project(record)
                        st.rerun()
                with col_del:
                    if st.button("❌", key=f"del_{filename}", help="Delete project"):
                        st.session_state.confirm_delete = filename
                        st.rerun()

                if st.session_state.confirm_delete == filename:
                    st.warning(f"Delete '{name}'? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirm", key=f"confirm_del_{filename}", use_container_width=True):
                        delete_project(filename)
                        if st.session_state.current_name == name:
                            start_new_project()
                        st.session_state.confirm_delete = None
                        st.rerun()
                    if c2.button("Cancel", key=f"cancel_del_{filename}", use_container_width=True):
                        st.session_state.confirm_delete = None
                        st.rerun()

        st.markdown("---")

        with st.expander("⚙ Settings", expanded=False):
            st.session_state.theme = st.radio(
                "Theme", ["Dark", "Light"],
                index=0 if st.session_state.theme == "Dark" else 1,
                horizontal=True,
            )
            st.session_state.mock_mode = st.toggle(
                "Mock Mode (no AI calls, instant demo data)",
                value=st.session_state.mock_mode,
            )

            if st.button("🧹 Clear Cache", use_container_width=True):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Cache cleared.")

            if st.button("🔄 Refresh History", use_container_width=True):
                _read_history_file.clear()
                st.rerun()

            if st.session_state.current_state is not None:
                export_payload = json.dumps(
                    {
                        "name": st.session_state.current_name or "Untitled Project",
                        "state": serialize_state(st.session_state.current_state),
                        "files": st.session_state.current_files or {},
                    },
                    indent=2,
                    default=str,
                )
                st.download_button(
                    "⬇ Export Current Project (JSON)",
                    data=export_payload,
                    file_name=f"{slugify(st.session_state.current_name or 'project')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            uploaded = st.file_uploader("⬆ Import Project (JSON)", type=["json"])
            if uploaded is not None:
                try:
                    record = json.loads(uploaded.read().decode("utf-8"))
                    open_project(record)
                    st.success("Project imported.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not import project: {exc}")

        if st.button("ℹ️ About", use_container_width=True):
            about_dialog()


# =============================================================================
# Main input form
# =============================================================================

def render_input_form() -> None:
    st.markdown(
        f"""
        <div class="tf-hero">
            <h1>💡 {APP_NAME}</h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.mock_mode:
        st.info("🧪 Mock Mode is ON — the pipeline will use instant sample data instead of calling AI agents.")

    suffix = st.session_state.input_key_suffix
    problem = st.text_area(
        "Problem Statement",
        height=180,
        placeholder="Example: Reduce food waste in restaurants",
        key=f"problem_input_{suffix}",
    )
    objective = st.text_input(
        "Objective (optional)",
        placeholder="Example: Cut waste by 30% within 6 months",
        key=f"objective_input_{suffix}",
    )

    run = st.button("🚀 Generate Solution", type="primary", use_container_width=True)

    if run:
        if not problem.strip():
            st.error("Please enter a problem statement.")
            st.stop()

        state, generated_files = run_pipeline(problem, objective, st.session_state.mock_mode)
        name = auto_title(problem)

        st.session_state.current_state = state
        st.session_state.current_files = generated_files
        st.session_state.current_name = name

        try:
            save_project(name, state, generated_files)
            _read_history_file.clear()
        except Exception as exc:
            st.warning(f"Project generated, but could not be saved to history: {exc}")

        st.rerun()


# =============================================================================
# Results: tabs
# =============================================================================

def render_mermaid(mermaid_text: str) -> None:
    components.html(
        f"""
        <div class="mermaid" style="background:transparent;">{mermaid_text}</div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js"></script>
        <script>mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});</script>
        """,
        height=420,
        scrolling=True,
    )


def render_overview_tab(state: Any) -> None:
    confidence = g(state, "confidence", 0) or 0
    experts = g(state, "experts", []) or []
    risks = g(state, "risks", []) or []
    budget = g(state, "budget", {}) or {}
    timeline = g(state, "timeline", []) or []

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Confidence", f"{round(confidence * 100, 1)}%")
    c2.metric("Experts", len(experts))
    c3.metric("Risks", len(risks))
    c4.metric("Budget", budget.get("total", "—"))
    c5.metric("Timeline Phases", len(timeline))

    st.markdown("#### 📋 Executive Summary")
    st.markdown(f'<div class="tf-card">{g(state, "executive_summary", "—")}</div>', unsafe_allow_html=True)


def render_experts_tab(state: Any) -> None:
    experts = g(state, "experts", []) or []
    debate = g(state, "debate", {}) or {}

    if not experts:
        st.caption("No expert data available.")
    for expert in experts:
        with st.expander(f"👤 {expert.get('name', 'Expert')}", expanded=False):
            st.write(expert.get("role", ""))
            if expert.get("reason"):
                st.caption(expert["reason"])

    discussion = debate.get("discussion", [])
    if discussion:
        st.markdown("#### 🧠 Expert Debate")
        for turn in discussion:
            st.markdown(f"**{turn.get('expert', '')}**")
            st.write(turn.get("opinion", ""))
        if debate.get("final_consensus"):
            st.success(debate["final_consensus"])


def render_architecture_tab(state: Any, files: Dict[str, Optional[str]]) -> None:
    architecture = g(state, "architecture", {}) or {}
    if architecture:
        st.subheader(architecture.get("title", "Architecture"))
        for component in architecture.get("components", []):
            st.markdown(f"- {component}")

    mermaid_path = files.get("diagram_mermaid") if files else None
    if mermaid_path and Path(mermaid_path).exists():
        st.markdown("#### 🧭 Mermaid Diagram")
        mermaid_text = Path(mermaid_path).read_text(encoding="utf-8", errors="ignore")
        render_mermaid(mermaid_text)
        with st.expander("View Mermaid source"):
            st.code(mermaid_text, language="text")

    png_path = files.get("diagram_png") if files else None
    if png_path and Path(png_path).exists():
        st.markdown("#### 🖼 Rendered Diagram (Graphviz)")
        st.image(png_path, use_container_width=True)

    dot_path = files.get("diagram_dot") if files else None
    if dot_path and Path(dot_path).exists():
        with st.expander("View DOT source"):
            st.code(Path(dot_path).read_text(encoding="utf-8", errors="ignore"), language="text")

    if not any([architecture, mermaid_path, png_path, dot_path]):
        st.caption("No architecture data available.")


def render_business_tab(state: Any) -> None:
    budget = g(state, "budget", {}) or {}
    timeline = g(state, "timeline", []) or []
    kpis = g(state, "kpis", []) or []
    risks = g(state, "risks", []) or []
    plan = g(state, "implementation_plan", None)

    st.markdown("#### 💰 Budget")
    if budget.get("items"):
        st.table(budget["items"])
    if budget.get("total"):
        st.success(f"Total Budget: {budget['total']}")

    st.markdown("#### 📅 Timeline")
    if timeline:
        st.table(timeline)

    if plan:
        st.markdown("#### 🗺 Implementation Plan")
        st.write(plan)

    st.markdown("#### 📈 KPIs")
    for kpi in kpis:
        st.success(kpi)

    st.markdown("#### ⚠ Risks")
    for risk in risks:
        st.markdown(f"**{risk.get('risk', '')}**")
        st.write(risk.get("mitigation", ""))


def render_report_tab(state: Any) -> None:
    st.markdown("#### 📋 Executive Summary")
    st.write(g(state, "executive_summary", "—"))

    st.markdown("#### 📄 Technical Report")
    st.write(g(state, "technical_report", "—"))

    plan = g(state, "implementation_plan", None)
    if plan:
        st.markdown("#### 🗺 Implementation Plan")
        st.write(plan)


def download_card(label: str, path: Optional[str], file_name: str, mime: str) -> None:
    data = read_bytes(path)
    st.markdown(f'<div class="tf-download-card"><h4>{label}</h4></div>', unsafe_allow_html=True)
    st.download_button(
        f"Download {label}",
        data=data or b"",
        file_name=file_name,
        mime=mime,
        use_container_width=True,
        disabled=data is None,
    )
    if data is None:
        st.caption("Not available for this project.")


def render_downloads_tab(state: Any, files: Dict[str, Optional[str]]) -> None:
    files = files or {}
    col1, col2 = st.columns(2)
    with col1:
        download_card("PDF Report", files.get("pdf"), "ThinkForge_Report.pdf", "application/pdf")
    with col2:
        download_card(
            "PowerPoint", files.get("ppt"), "ThinkForge_Presentation.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    if files.get("diagram_dot"):
        download_card("DOT File", files.get("diagram_dot"), "architecture.dot", "text/vnd.graphviz")
    st.markdown("#### 📦 Raw Export")
    col6, col7 = st.columns(2)
    technical_report = g(state, "technical_report", "") or ""
    with col6:
        st.download_button(
            "Download Markdown Report",
            data=technical_report,
            file_name="ThinkForge_Report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col7:
        st.download_button(
            "Download JSON",
            data=json.dumps(serialize_state(state), indent=2, default=str),
            file_name="ThinkForge_Project.json",
            mime="application/json",
            use_container_width=True,
        )


def render_logs_tab(state: Any) -> None:
    history = g(state, "execution_history", []) or []
    done = set(history)
    st.markdown("#### 🧾 Execution Log")
    for step in PIPELINE_STEPS:
        matched = any(step.lower() in item.lower() or item.lower() in step.lower() for item in done)
        icon = "✅" if matched else "⬜"
        st.markdown(f"{icon} **{step}**")

    with st.expander("Raw execution history"):
        st.write(history)


def render_results(state: Any, files: Dict[str, Optional[str]], name: str) -> None:
    st.markdown(
        f"""
        <div class="tf-hero">
            <h1>💡 {APP_NAME} <span class="tf-badge">{name}</span></h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        ["📊 Overview", "👥 Experts", "🏗 Architecture", "💼 Business",
         "📄 Reports", "📥 Downloads", "🧾 Logs"]
    )
    with tabs[0]:
        render_overview_tab(state)
    with tabs[1]:
        render_experts_tab(state)
    with tabs[2]:
        render_architecture_tab(state, files)
    with tabs[3]:
        render_business_tab(state)
    with tabs[4]:
        render_report_tab(state)
    with tabs[5]:
        render_downloads_tab(state, files)
    with tabs[6]:
        render_logs_tab(state)


# =============================================================================
# App entry point
# =============================================================================

def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")
    init_session_state()
    inject_css(st.session_state.theme)
    render_sidebar()

    if st.session_state.current_state is None:
        render_input_form()
    else:
        render_results(
            st.session_state.current_state,
            st.session_state.current_files or {},
            st.session_state.current_name or "Untitled Project",
        )

    st.divider()
    st.caption(f"{APP_NAME} • {APP_TAGLINE}")
    st.caption("Powered by Multi-Agent AI | Planner → Analyzer → Experts → Debate → Solution")


if __name__ == "__main__":
    main()