from agents.graph.checkpointer import create_sqlite_checkpointer
from agents.graph.workflow import build_workflow
from agents.schemas.job import JobPosting


def make_initial_state():
    return {
        "cv_text": "Python developer with ML experience",
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


def test_sqlite_checkpoint_survives_reconnection(tmp_path):
    db_path = tmp_path / "checkpoints.sqlite"

    config = {
        "configurable": {
            "thread_id": "persistent-analysis-001"
        }
    }

    # First connection: execute workflow and save checkpoint.
    with create_sqlite_checkpointer(db_path) as checkpointer:
        graph = build_workflow(checkpointer)

        graph.invoke(
            make_initial_state(),
            config=config,
        )

        original_state = graph.get_state(config)

        assert original_state.values["cv_text"] == (
            "Python developer with ML experience"
        )

    # First connection is now closed.

    # Second connection: load checkpoint from the same database.
    with create_sqlite_checkpointer(db_path) as checkpointer:
        graph = build_workflow(checkpointer)

        restored_state = graph.get_state(config)

        assert restored_state.values["cv_text"] == (
            "Python developer with ML experience"
        )

        assert restored_state.next == ()