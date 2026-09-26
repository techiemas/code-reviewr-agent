from __future__ import annotations

from services.llm_service import LLMService
from prompts.code_builder_prompt import CODE_BUILDER_SYSTEM_PROMPT, build_code_builder_user_prompt
from models.schemas import CodeBuildResult


class CodeBuilderAgent:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    def run(
        self,
        requirement: str,
        existing_code: str = "",
        language: str = "Python",
        framework: str | None = None,
        additional_instructions: str = "",
    ) -> CodeBuildResult:
        if not requirement or not requirement.strip():
            raise ValueError("Requirement is required for the Code Builder agent.")

        user_prompt = build_code_builder_user_prompt(
            requirement=requirement,
            existing_code=existing_code,
            language=language,
            additional_instructions=additional_instructions or (framework or ""),
        )
        payload = self.llm_service.generate(CODE_BUILDER_SYSTEM_PROMPT, user_prompt)
        return CodeBuildResult.model_validate(payload)
