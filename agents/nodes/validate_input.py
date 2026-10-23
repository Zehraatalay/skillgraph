from agents.graph.state import SkillGraphState


def validate_input(state: SkillGraphState) -> dict:
    cv_text = (state.get("cv_text") or "").strip()
    github_username = (state.get("github_username") or "").strip()
    job_postings = state.get("job_postings") or []

    if not cv_text and not github_username:
        raise ValueError(
            "At least one candidate source is required: "
            "CV or GitHub username."
        )

    if not job_postings:
        raise ValueError(
            "At least one job posting is required."
        )

    return {}