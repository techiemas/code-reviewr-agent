from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from models.schemas import CodeReviewSummary, CodeReviewResult
from services.llm_service import LLMService
from utils.env_loader import load_project_env
from utils.logging_config import setup_logger
from workflow.orchestrator import WorkflowOrchestrator

load_project_env()
logger = setup_logger("code_reviewr")

st.set_page_config(page_title="Code Reviewr", page_icon="🧠", layout="wide")


def apply_custom_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0f172a;
            --panel: #111827;
            --panel-alt: #1f2937;
            --border: #2d3748;
            --text: #e5e7eb;
            --muted: #94a3b8;
            --accent: #60a5fa;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--bg);
            color: var(--text);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .section-card {
            background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(17,24,39,0.84));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1.25rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.35);
            margin-bottom: 1rem;
        }
        .tiny {
            color: var(--muted);
            font-size: 0.83rem;
        }
        .status-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            font-size: 0.82rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        .status-complete { background: rgba(34, 197, 94, 0.12); color: #86efac; }
        .status-running { background: rgba(245, 158, 11, 0.12); color: #fbbf24; }
        .status-waiting { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; }
        .status-failed { background: rgba(239, 68, 68, 0.12); color: #fca5a5; }
        .workflow-arrow {
            text-align: center; color: var(--muted); font-size: 1.4rem; padding: 0.2rem 0;
        }
        .review-finding {
            border-left: 4px solid var(--warning);
            padding: 0.9rem 1rem;
            background: rgba(31,41,55,0.55);
            border-radius: 10px;
            margin-bottom: 0.85rem;
        }
        .review-critical { border-left-color: #ef4444; }
        .review-high { border-left-color: #f97316; }
        .review-medium { border-left-color: #fbbf24; }
        .review-low { border-left-color: #60a5fa; }
        .review-info { border-left-color: #38bdf8; }
        code {
            background: rgba(15, 23, 42, 0.8);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    defaults = {
        "task_name": "",
        "language": "Python",
        "requirement": "",
        "additional_instructions": "",
        "existing_code": "",
        "workflow_result": None,
        "workflow_status": "waiting",
        "current_agent": "Waiting",
        "errors": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def status_badge(label: str, status: str) -> str:
    classes = {
        "Waiting": "status-waiting",
        "Running": "status-running",
        "Completed": "status-complete",
        "Failed": "status-failed",
    }
    return f'<span class="status-chip {classes.get(status, "status-waiting")}">{label}</span>'


def create_review_summary(review: CodeReviewResult | None) -> CodeReviewSummary:
    if review is None:
        return CodeReviewSummary()

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for finding in review.findings:
        counts[finding.severity] += 1
    return CodeReviewSummary(
        critical=counts["CRITICAL"],
        high=counts["HIGH"],
        medium=counts["MEDIUM"],
        low=counts["LOW"],
        info=counts["INFO"],
    )


def build_review_markdown(review: CodeReviewResult | None) -> str:
    if review is None:
        return "No review data available."

    summary = create_review_summary(review)
    lines = [
        "## Review Summary",
        review.summary or "No material issues were identified during the review.",
        "",
        "**Risk level:** " + review.risk_level,
        "",
        "**Positive aspects:**",
    ]
    if review.positive_aspects:
        for item in review.positive_aspects:
            lines.append(f"- {item}")
    else:
        lines.append("- No explicit strengths were identified.")

    lines.extend([
        "",
        "### Findings overview",
        f"- Critical: {summary.critical}",
        f"- High: {summary.high}",
        f"- Medium: {summary.medium}",
        f"- Low: {summary.low}",
        f"- Info: {summary.info}",
    ])

    for finding in review.findings:
        lines.extend([
            "",
            f"### {finding.severity} - {finding.location or 'Unspecified location'}",
            f"**Issue:** {finding.issue}",
            f"**Why it matters:** {finding.impact}",
            f"**Recommendation:** {finding.recommendation}",
        ])

    return "\n".join(lines)


def show_workflow_visualization(current_status: str) -> None:
    statuses = [
        ("Code Builder", "Waiting" if current_status not in {"Code Builder", "Code Reviewer", "Code Refactorer"} else "Completed" if current_status == "Completed" else "Running"),
        ("Code Reviewer", "Waiting" if current_status not in {"Code Reviewer", "Code Refactorer", "Completed"} else "Completed" if current_status == "Completed" else "Running"),
        ("Code Refactorer", "Waiting" if current_status not in {"Code Refactorer", "Completed"} else "Completed" if current_status == "Completed" else "Running"),
    ]

    cols = st.columns(3)
    mapping = {
        "Waiting": "◌ Waiting",
        "Running": "◐ Running",
        "Completed": "✓ Completed",
        "Failed": "✕ Failed",
    }
    for idx, (label, state) in enumerate(statuses):
        with cols[idx]:
            if idx > 0:
                st.markdown('<div class="workflow-arrow">↓</div>', unsafe_allow_html=True)
            st.markdown(f"<div class='section-card'><strong>{label}</strong><br>{mapping.get(state, '◌ Waiting')}</div>", unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        """
        <div style='text-align: center; padding: 4rem 0;'>
            <div style='font-size: 3rem;'>👨‍💻</div>
            <h2>Ready to review your code</h2>
            <p style='color: #94a3b8;'>Describe what you want to build and Code Reviewr will:</p>
            <p><strong>Build → Review → Refactor</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_result(result: Any) -> None:
    if result is None:
        return

    build_result = result.build
    review_result = result.review
    refactor_result = result.refactor

    st.subheader("Code Builder")
    st.markdown(f"Status: {status_badge('Completed', 'Completed')}", unsafe_allow_html=True)
    st.write(build_result.explanation)
    st.code(build_result.code, language="python")
    st.download_button(
        "Download Generated Code",
        data=build_result.code,
        file_name="generated_code.py",
        mime="text/x-python",
    )
    if build_result.dependencies:
        st.write("Dependencies:")
        st.write(", ".join(build_result.dependencies))
    if build_result.assumptions:
        st.write("Assumptions:")
        st.write("- " + "\n- ".join(build_result.assumptions))

    st.subheader("Code Reviewer")
    st.markdown(f"Risk level: <strong>{review_result.risk_level}</strong>", unsafe_allow_html=True)
    st.markdown(build_review_markdown(review_result), unsafe_allow_html=False)
    summary = create_review_summary(review_result)
    col_counts = st.columns(5)
    labels = ["Critical", "High", "Medium", "Low", "Info"]
    values = [summary.critical, summary.high, summary.medium, summary.low, summary.info]
    for col, label, value in zip(col_counts, labels, values):
        with col:
            st.metric(label, value)

    if review_result.findings:
        st.write("Findings:")
        for finding in review_result.findings:
            severity_class = finding.severity.lower()
            st.markdown(
                f"""
                <div class='review-finding review-{severity_class}'>
                    <strong>{finding.severity}</strong><br>
                    <strong>Location:</strong> {finding.location or 'Unspecified location'}<br>
                    <strong>Issue:</strong> {finding.issue}<br>
                    <strong>Why it matters:</strong> {finding.impact}<br>
                    <strong>Recommendation:</strong> {finding.recommendation}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Code Refactorer")
    st.code(refactor_result.code, language="python")
    st.download_button(
        "Download Refactored Code",
        data=refactor_result.code,
        file_name="refactored_code.py",
        mime="text/x-python",
    )
    if refactor_result.changes:
        st.write("Changes made:")
        for change in refactor_result.changes:
            st.write(f"- {change}")
    if refactor_result.remaining_considerations:
        st.write("Remaining considerations:")
        for item in refactor_result.remaining_considerations:
            st.write(f"- {item}")


def build_review_report(review: CodeReviewResult | None) -> str:
    if review is None:
        return "No review report available."

    lines = [
        "# Code Reviewr Review Report",
        "",
        "## Summary",
        review.summary or "No summary provided.",
        "",
        "## Risk Level",
        review.risk_level,
        "",
        "## Positive Aspects",
    ]
    for item in review.positive_aspects or ["No positive aspects recorded."]:
        lines.append(f"- {item}")
    lines.extend(["", "## Findings"]) 
    for finding in review.findings:
        lines.extend([
            "",
            f"### {finding.severity} - {finding.location or 'Unspecified location'}",
            f"**Problem:** {finding.issue}",
            f"**Why it matters:** {finding.impact}",
            f"**Recommendation:** {finding.recommendation}",
        ])
    return "\n".join(lines)


def main() -> None:
    apply_custom_theme()
    init_session_state()

    st.sidebar.title("Code Reviewr")
    st.sidebar.caption("Sequential AI Code Engineering")

    st.sidebar.header("Project Details")
    task_name = st.sidebar.text_input("Project / Task Name", value=st.session_state.task_name)
    language = st.sidebar.selectbox(
        "Language",
        ["Python", "JavaScript", "TypeScript", "Java", "Go", "Other"],
        index=["Python", "JavaScript", "TypeScript", "Java", "Go", "Other"].index(st.session_state.language or "Python"),
    )
    requirement = st.sidebar.text_area("Requirement", value=st.session_state.requirement, height=180)
    additional_instructions = st.sidebar.text_area("Additional Instructions", value=st.session_state.additional_instructions, height=120)
    existing_code = st.sidebar.text_area("Existing Code", value=st.session_state.existing_code, height=180)

    st.sidebar.markdown("---")
    st.sidebar.caption("Configuration")
    model_choice = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
    max_tokens = st.sidebar.number_input("Maximum Tokens", min_value=256, max_value=4096, value=2000, step=128)

    start_button = st.sidebar.button("Start Workflow", disabled=not requirement.strip())
    reset_button = st.sidebar.button("Reset")

    if reset_button:
        for key in [
            "task_name",
            "language",
            "requirement",
            "additional_instructions",
            "existing_code",
            "workflow_result",
            "workflow_status",
            "current_agent",
            "errors",
        ]:
            st.session_state[key] = "" if key in {"task_name", "language", "requirement", "additional_instructions", "existing_code", "workflow_status", "current_agent"} else None if key == "workflow_result" else []
        st.session_state.language = "Python"
        st.session_state.workflow_status = "waiting"
        st.session_state.current_agent = "Waiting"
        st.session_state.errors = []
        st.rerun()

    st.session_state.task_name = task_name
    st.session_state.language = language
    st.session_state.requirement = requirement
    st.session_state.additional_instructions = additional_instructions
    st.session_state.existing_code = existing_code

    st.title("Code Reviewr")
    st.caption("AI-Powered Sequential Code Engineering")

    if start_button:
        st.session_state.workflow_status = "running"
        st.session_state.current_agent = "Code Builder"
        st.session_state.errors = []
        logger.info("Workflow started")

        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            st.warning("Set OPENAI_API_KEY in your .env file before running the workflow.")
            st.session_state.workflow_status = "failed"
            st.session_state.current_agent = "Failed"
            st.session_state.errors = ["OpenAI API key is missing."]
        else:
            work_status = st.container()
            with work_status:
                st.markdown(
                    f"{status_badge('Requirement received', 'Completed')} {status_badge('Code Builder running', 'Running')} {status_badge('Code Reviewer waiting', 'Waiting')} {status_badge('Code Refactorer waiting', 'Waiting')}",
                    unsafe_allow_html=True,
                )
                st.caption("Running agent workflow...")

            try:
                llm_service = LLMService(
                    api_key=api_key,
                    model=model_choice,
                    temperature=float(temperature),
                    max_tokens=int(max_tokens),
                )
                orchestrator = WorkflowOrchestrator(llm_service=llm_service)
                result = orchestrator.run(
                    requirement=requirement,
                    existing_code=existing_code,
                    language=language,
                    task_name=task_name,
                    additional_instructions=additional_instructions,
                )
                st.session_state.workflow_result = result
                st.session_state.workflow_status = "completed"
                st.session_state.current_agent = "Completed"
                logger.info("Workflow completed successfully")
                st.success("Workflow completed successfully.")
            except Exception as exc:
                logger.exception("Workflow failed")
                st.session_state.workflow_status = "failed"
                st.session_state.current_agent = "Failed"
                st.session_state.errors = [str(exc)]
                st.error("Workflow failed. Please review the requirement and model configuration.")
                st.warning("No secrets or API keys are exposed in the UI.")

    result = st.session_state.get("workflow_result")
    if result is None:
        render_empty_state()
        return

    st.markdown("---")
    show_workflow_visualization(st.session_state.current_agent)

    if st.session_state.errors:
        st.warning("Last error: " + "; ".join(st.session_state.errors))

    render_workflow_result(result)

    st.download_button(
        "Download Review Report",
        data=build_review_report(result.review),
        file_name="review_report.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download Workflow JSON",
        data=json.dumps(result.model_dump(), indent=2),
        file_name="workflow_report.json",
        mime="application/json",
    )

    st.caption("Built by Vishnu")


if __name__ == "__main__":
    main()
