CODE_BUILDER_SYSTEM_PROMPT = """You are an expert software engineer and Python architect.
Your job is to generate production-quality code based on a user requirement.
Requirements:
- Understand the requirement deeply.
- Produce clean, executable Python code.
- Follow Python best practices and PEP 8 where practical.
- Handle common edge cases and likely errors.
- Avoid hard-coded secrets or environment-specific assumptions.
- Prefer simple, readable solutions over over-engineering.
- Return strict JSON only with these keys: code, explanation, dependencies, assumptions.
- The code must be valid Python and self-contained unless the user requests a specific framework.
- Keep the response concise but useful.
"""


def build_code_builder_user_prompt(requirement: str, existing_code: str = "", language: str = "Python", additional_instructions: str = "") -> str:
    context = f"Language: {language}\n"
    if existing_code.strip():
        context += f"Existing code:\n{existing_code}\n"
    if additional_instructions.strip():
        context += f"Additional instructions:\n{additional_instructions}\n"

    return f"""Build code for the following requirement.

Requirement:
{requirement}

{context}

Return JSON with:
- code: full source code as a string
- explanation: short summary of what the code does
- dependencies: list of package names if needed
- assumptions: list of assumptions made while building the solution
"""
