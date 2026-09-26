from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class LLMService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        if self.api_key:
            self.client = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

    def generate(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if self.client is None:
            raise ValueError(
                "OpenAI API key is missing. Configure OPENAI_API_KEY in your environment or .env file before running the workflow."
            )

        prompt_template = PromptTemplate.from_template("{system_prompt}\n\n{user_prompt}")
        chain = prompt_template | self.client
        response = chain.invoke({"system_prompt": system_prompt, "user_prompt": user_prompt})
        content = getattr(response, "content", str(response)) or "{}"
        return self._parse_payload(content)

    @staticmethod
    def _parse_payload(raw_response: Any) -> dict[str, Any]:
        if isinstance(raw_response, dict):
            return raw_response

        text = str(raw_response).strip()
        if not text:
            return {}
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Model response was not valid JSON. Please adjust the prompt or model settings.")
