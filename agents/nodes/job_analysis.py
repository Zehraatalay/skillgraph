from agents.graph.state import SkillGraphState
from agents.schemas.job import JobPosting


def create_job_analysis_node(extractor):
    def analyze_jobs(state: SkillGraphState) -> dict:
        job_postings = state.get("job_postings") or []

        analyses = []

        for job_data in job_postings:
            job = JobPosting.model_validate(job_data)

            analysis = extractor.extract(job)

            analyses.append(analysis.model_dump(mode="json"))

        return {
            "job_analyses": analyses,
        }

    return analyze_jobs
