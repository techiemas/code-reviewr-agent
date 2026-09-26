from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
RiskLevel = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


class CodeBuildResult(BaseModel):
    code: str = Field(..., min_length=1)
    explanation: str = ""
    dependencies: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    severity: Severity
    location: str = ""
    issue: str = Field(..., min_length=1)
    impact: str = Field(..., min_length=1)
    recommendation: str = Field(..., min_length=1)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        allowed = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
        if value.upper() not in allowed:
            raise ValueError(f"Severity must be one of {sorted(allowed)}")
        return value.upper()


class CodeReviewResult(BaseModel):
    summary: str = ""
    risk_level: RiskLevel = "LOW"
    positive_aspects: list[str] = Field(default_factory=list)
    findings: list[ReviewFinding] = Field(default_factory=list)


class RefactorResult(BaseModel):
    code: str = Field(..., min_length=1)
    changes: list[str] = Field(default_factory=list)
    remaining_considerations: list[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    build: CodeBuildResult
    review: CodeReviewResult
    refactor: RefactorResult


class CodeReviewSummary(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

    @property
    def total(self) -> int:
        return self.critical + self.high + self.medium + self.low + self.info
