from agents.graph.state import SkillGraphState


def route_after_validation(state: SkillGraphState) -> str:
    has_cv = bool((state.get("cv_text") or "").strip())

    if has_cv:
        return "analyze_cv"

    return "check_github"


def route_github(state: SkillGraphState) -> str:
    has_github = bool((state.get("github_username") or "").strip())

    if has_github:
        return "analyze_github"

    return "build_candidate_profile"