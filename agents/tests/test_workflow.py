from agents.graph.checkpointer import create_checkpointer
from agents.graph.workflow import build_workflow
from agents.schemas.job import JobPosting


def test_workflow_streaming():
    graph = build_workflow(create_checkpointer())

    config = {"configurable": {"thread_id": "test-session-001"}}

    initial_state = {
        "cv_text": "Python developer with ML experience",
        "github_username": None,
        "preferences_text": "Interested in ML Engineer roles",
        "job_postings": [
            JobPosting(
                id="job-001",
                title="ML Engineer",
                description="Python and machine learning",
            ).model_dump(mode="json")
        ],
        "candidate_profile": None,
        "results": [],
    }

    events = list(
        graph.stream(
            initial_state,
            config=config,
            stream_mode="updates",
        )
    )

    executed_nodes = [node_name for event in events for node_name in event]

    assert executed_nodes == [
        "validate_input",
        "analyze_cv",
        "check_github",
        "build_candidate_profile",
    ]

    final_state = graph.get_state(config)

    assert isinstance(
        final_state.values["cv_analysis"],
        dict,
    )

    assert final_state.next == ()
