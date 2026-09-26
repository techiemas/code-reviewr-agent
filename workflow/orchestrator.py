from __future__ import annotations

import logging
from typing import Any

from agents.code_builder import CodeBuilderAgent
from agents.code_refactorer import CodeRefactorerAgent
from agents.code_reviewer import CodeReviewerAgent
from services.llm_service import LLMService
from workflow.state import WorkflowState
from models.schemas import CodeBuildResult, CodeReviewResult, RefactorResult, WorkflowResult

logger = logging.getLogger("code_reviewr")


class WorkflowOrchestrator:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()
        self.state = WorkflowState()

    def run(
        self,
        requirement: str,
        existing_code: str = "",
        language: str = "Python",
        task_name: str = "",
        additional_instructions: str = "",
    ) -> WorkflowResult:
        sanitized_requirement = (requirement or "").strip()
        if not sanitized_requirement:
            raise ValueError("Requirement is required to start the workflow.")

        logger.info("Workflow started")
        self.state.reset()
        self.state.requirement = sanitized_requirement
        self.state.existing_code = existing_code or ""
        self.state.language = language or "Python"
        self.state.task_name = task_name or ""
        self.state.additional_instructions = additional_instructions or ""
        self.state.workflow_status = "running"

        try:
            self.state.current_agent = "Code Builder"
            logger.info("Agent started: Code Builder")
            build_agent = CodeBuilderAgent(llm_service=self.llm_service)
            build_result = build_agent.run(
                requirement=sanitized_requirement,
                existing_code=existing_code,
                language=language,
                additional_instructions=additional_instructions,
            )
            self.state.build_result = build_result
            self.state.generated_code = build_result.code
            self.state.current_agent = "Code Reviewer"
            logger.info("Code Builder completed")

            review_agent = CodeReviewerAgent(llm_service=self.llm_service)
            review_result = review_agent.run(sanitized_requirement, build_result.code)
            self.state.review = review_result
            self.state.current_agent = "Code Refactorer"
            logger.info("Agent started: Code Reviewer")

            refactor_agent = CodeRefactorerAgent(llm_service=self.llm_service)
            refactor_result = refactor_agent.run(
                requirement=sanitized_requirement,
                generated_code=build_result.code,
                review=review_result.model_dump(),
            )
            self.state.refactor_result = refactor_result
            self.state.refactored_code = refactor_result.code
            self.state.workflow_status = "completed"
            self.state.current_agent = "Completed"
            logger.info("Workflow completed")

            return WorkflowResult(build=build_result, review=review_result, refactor=refactor_result)
        except Exception as exc:  # pragma: no cover - defensive catch for UI logic
            self.state.errors.append(str(exc))
            self.state.workflow_status = "failed"
            self.state.current_agent = "Failed"
            logger.exception("Workflow failed")
            raise
