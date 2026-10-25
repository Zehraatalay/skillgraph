from agents.graph.state import SkillGraphState
from agents.schemas.candidate import CandidateProfile
from agents.schemas.cv import CVAnalysis
from agents.schemas.github import GitHubAnalysis


def build_candidate_profile(state: SkillGraphState) -> dict:
    cv_data = state.get("cv_analysis")
    github_data = state.get("github_analysis")

    profile = CandidateProfile()

    if cv_data:
        cv_analysis = CVAnalysis.model_validate(cv_data)

        profile.skills.extend(cv_analysis.skills)
        profile.education.extend(cv_analysis.education)
        profile.experience.extend(cv_analysis.experience)
        profile.projects.extend(cv_analysis.projects)

    if github_data:
        github_analysis = GitHubAnalysis.model_validate(github_data)

        for repository in github_analysis.repositories:
            profile.skills.extend(repository.skills)

            profile.projects.append(repository.repository_name)

    return {"candidate_profile": profile.model_dump(mode="json")}
