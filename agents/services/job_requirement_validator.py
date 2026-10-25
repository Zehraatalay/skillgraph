from agents.schemas.job_analysis import JobAnalysis


def validate_job_requirements(
    analysis: JobAnalysis,
    description: str,
) -> None:
    for requirement in analysis.requirements:
        if requirement.evidence not in description:
            raise ValueError(
                f"Job requirement evidence not found for skill: {requirement.skill}"
            )
