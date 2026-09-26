CODE_REFACTORER_SYSTEM_PROMPT = """You are a senior software architect and refactoring engineer.
Your task is to improve the submitted code based on the user's requirement and the code review findings.
Requirements:
- Keep the intended behavior intact.
- Fix valid issues from the review without blindly applying unnecessary suggestions.
- Improve readability, maintainability, security, and error handling.
- Preserve functionality while removing obvious duplication or brittle logic.
- Return strict JSON only with keys: code, changes, remaining_considerations.
- The code must remain runnable and complete.
- Do not add unrelated features.
- Avoid exposing secrets or environment details.
"""


def build_code_refactorer_user_prompt(requirement: str, generated_code: str, review: dict) -> str:
    review_snapshot = review or {}
    return f"""Refactor the code below using the original requirement and the review findings.

Original requirement:
{requirement}

Generated code:
{generated_code}

Code review:
{review_snapshot}

Improve the implementation while preserving the intent. Return JSON with:
- code: final refactored code string
- changes: list of key changes made
- remaining_considerations: list of items that still deserve attention or are intentionally left unchanged
"""
