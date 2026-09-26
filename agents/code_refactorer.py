from __future__ import annotations

from models.schemas import RefactorResult
from prompts.code_refactorer_prompt import CODE_REFACTORER_SYSTEM_PROMPT, build_code_refactorer_user_prompt
from services.llm_service import LLMService


class CodeRefactorerAgent:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    def run(self, requirement: str, generated_code: str, review: dict) -> RefactorResult:
        if not requirement or not requirement.strip():
            raise ValueError("Requirement is required for the Code Refactorer agent.")
        if not generated_code or not generated_code.strip():
            raise ValueError("Generated code is required for the Code Refactorer agent.")

        user_prompt = build_code_refactorer_user_prompt(requirement, generated_code, review)
        payload = self.llm_service.generate(CODE_REFACTORER_SYSTEM_PROMPT, user_prompt)
        return RefactorResult.model_validate(payload)
