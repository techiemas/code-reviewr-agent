from models.schemas import CodeBuildResult, CodeReviewResult, ReviewFinding, RefactorResult, WorkflowResult


def test_models_are_valid():
    finding = ReviewFinding(
        severity="HIGH",
        location="app.py:10",
        issue="Potential bug",
        impact="Could crash on empty input",
        recommendation="Validate before use",
    )

    build = CodeBuildResult(
        code="print('hello')",
        explanation="Simple script",
        dependencies=["streamlit"],
        assumptions=["User wants a demo"],
    )

    review = CodeReviewResult(
        summary="Looks okay",
        risk_level="LOW",
        positive_aspects=["Clean structure"],
        findings=[finding],
    )

    refactor = RefactorResult(
        code="print('hello world')",
        changes=["Improved greeting"],
        remaining_considerations=["None"],
    )

    workflow = WorkflowResult(build=build, review=review, refactor=refactor)

    assert build.code == "print('hello')"
    assert review.findings[0].severity == "HIGH"
    assert workflow.refactor.code == "print('hello world')"


def test_review_finding_severity_validation():
    try:
        ReviewFinding(
            severity="INVALID",
            location="module.py",
            issue="bad",
            impact="bad",
            recommendation="bad",
        )
    except ValueError:
        return
    raise AssertionError("Severity validation should reject invalid enum values")
