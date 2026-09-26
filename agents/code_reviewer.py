from __future__ import annotations

from services.llm_service import LLMService
from prompts.code_reviewer_prompt import CODE_REVIEWER_SYSTEM_PROMPT, build_code_reviewer_user_prompt
from models.schemas import CodeReviewResult


class CodeReviewerAgent:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    def run(self, requirement: str, generated_code: str) -> CodeReviewResult:
        if not requirement or not requirement.strip():
            raise ValueError("Requirement is required for the Code Reviewer agent.")
        if not generated_code or not generated_code.strip():
            raise ValueError("Generated code is required for the Code Reviewer agent.")

        user_prompt = build_code_reviewer_user_prompt(requirement, generated_code)
        payload = self.llm_service.generate(CODE_REVIEWER_SYSTEM_PROMPT, user_prompt)
        return CodeReviewResult.model_validate(payload)
