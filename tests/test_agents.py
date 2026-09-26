from types import SimpleNamespace

from agents.code_builder import CodeBuilderAgent
from agents.code_reviewer import CodeReviewerAgent
from agents.code_refactorer import CodeRefactorerAgent


class FakeLLM:
    def __init__(self, payload):
        self.payload = payload

    def generate(self, *args, **kwargs):
        return self.payload


def test_code_builder_agent_parses_response():
    agent = CodeBuilderAgent(llm_service=FakeLLM({
        "code": "print('hello')",
        "explanation": "Greets the user",
        "dependencies": ["streamlit"],
        "assumptions": ["No framework specified"],
    }))

    result = agent.run("Build a greeting script")
    assert result.code == "print('hello')"
    assert result.explanation == "Greets the user"


def test_code_reviewer_agent_handles_review_payload():
    agent = CodeReviewerAgent(llm_service=FakeLLM({
        "summary": "Looks fine",
        "risk_level": "LOW",
        "positive_aspects": ["Readable"],
        "findings": [{
            "severity": "LOW",
            "location": "script.py",
            "issue": "Minor naming issue",
            "impact": "Not significant",
            "recommendation": "Rename variable",
        }],
    }))

    result = agent.run("Build a greeting script", "print('hello')")
    assert result.risk_level == "LOW"
    assert len(result.findings) == 1


def test_code_refactorer_agent_parses_output():
    agent = CodeRefactorerAgent(llm_service=FakeLLM({
        "code": "print('hello world')",
        "changes": ["Improved output"],
        "remaining_considerations": ["None"],
    }))

    result = agent.run(
        "Build a greeting script",
        "print('hello')",
        {"summary": "Looks fine", "risk_level": "LOW", "positive_aspects": ["Readable"], "findings": []},
    )
    assert result.code == "print('hello world')"
    assert result.changes[0] == "Improved output"
