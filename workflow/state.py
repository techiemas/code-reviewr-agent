from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from models.schemas import CodeBuildResult, CodeReviewResult, RefactorResult


@dataclass
class WorkflowState:
    requirement: str = ""
    existing_code: str = ""
    language: str = "Python"
    task_name: str = ""
    additional_instructions: str = ""
    generated_code: str = ""
    review: Optional[CodeReviewResult] = None
    refactored_code: str = ""
    workflow_status: str = "waiting"
    current_agent: str = "Waiting"
    errors: list[str] = field(default_factory=list)
    build_result: Optional[CodeBuildResult] = None
    refactor_result: Optional[RefactorResult] = None

    def reset(self) -> None:
        self.requirement = ""
        self.existing_code = ""
        self.language = "Python"
        self.task_name = ""
        self.additional_instructions = ""
        self.generated_code = ""
        self.review = None
        self.refactored_code = ""
        self.workflow_status = "waiting"
        self.current_agent = "Waiting"
        self.errors = []
        self.build_result = None
        self.refactor_result = None
