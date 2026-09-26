from workflow.state import WorkflowState
from workflow.orchestrator import WorkflowOrchestrator


def test_workflow_state_tracks_status():
    state = WorkflowState()
    state.workflow_status = "running"
    state.current_agent = "Code Builder"
    state.requirement = "Build a greeter"

    assert state.workflow_status == "running"
    assert state.current_agent == "Code Builder"
    assert state.requirement == "Build a greeter"


def test_orchestrator_requires_requirement():
    orchestrator = WorkflowOrchestrator()
    try:
        orchestrator.run("")
    except ValueError:
        return
    raise AssertionError("Empty requirement should raise ValueError")
