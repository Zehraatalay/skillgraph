from agents.graph.state import SkillGraphState


def create_validate_input_node(
    require_job_postings: bool = True,
):
    def validate_input(state: SkillGraphState) -> dict:
        cv_text = (state.get("cv_text") or "").strip()
        github_username = (state.get("github_username") or "").strip()

        job_postings = state.get("job_postings") or []

        if not cv_text and not github_username:
            raise ValueError(
                "At least one candidate source is required: CV or GitHub username."
            )

        if require_job_postings and not job_postings:
            raise ValueError("At least one job posting is required.")

        return {}

    return validate_input


# Backward compatibility
validate_input = create_validate_input_node(require_job_postings=True)
