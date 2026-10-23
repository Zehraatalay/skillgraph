from agents.graph.checkpointer import create_checkpointer
from agents.graph.workflow import build_workflow
from agents.schemas.job import JobPosting


def make_initial_state(cv_text: str):
    return {
        "cv_text": cv_text,
        "github_username": None,
        "preferences_text": None,
        "job_postings": [
            JobPosting(
                id="job-001",
                title="ML Engineer",
                description="Python and machine learning",
            )
        ],
        "candidate_profile": None,
        "results": [],
    }


def test_checkpoint_state():
    graph = build_workflow(create_checkpointer())

    config = {
        "configurable": {
            "thread_id": "analysis-001"
        }
    }

    graph.invoke(
        make_initial_state("Python developer"),
        config=config,
    )

    snapshot = graph.get_state(config)

    assert snapshot.values["cv_text"] == "Python developer"
    assert snapshot.next == ()


def test_thread_isolation():
    graph = build_workflow(create_checkpointer())

    config_1 = {
        "configurable": {
            "thread_id": "analysis-001"
        }
    }

    config_2 = {
        "configurable": {
            "thread_id": "analysis-002"
        }
    }

    graph.invoke(
        make_initial_state("Python developer"),
        config=config_1,
    )

    graph.invoke(
        make_initial_state("SQL analyst"),
        config=config_2,
    )

    state_1 = graph.get_state(config_1)
    state_2 = graph.get_state(config_2)

    assert state_1.values["cv_text"] == "Python developer"
    assert state_2.values["cv_text"] == "SQL analyst"


def test_checkpoint_history():
    graph = build_workflow(create_checkpointer())

    config = {
        "configurable": {
            "thread_id": "analysis-history"
        }
    }

    graph.invoke(
        make_initial_state("Python developer"),
        config=config,
    )

    history = list(graph.get_state_history(config))

    assert len(history) >= 2
    assert history[0].values["cv_text"] == "Python developer"