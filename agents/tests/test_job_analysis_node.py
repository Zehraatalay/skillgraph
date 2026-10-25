from agents.nodes.job_analysis import create_job_analysis_node
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup


class FakeJobExtractor:
    def extract(self, job):
        return GroupedJobAnalysis(
            job_id=job.id,
            requirement_groups=[
                RequirementGroup(
                    skills=["Python"],
                    priority="required",
                    evidence="Python is required.",
                )
            ],
        )


def test_job_analysis_node():
    node = create_job_analysis_node(FakeJobExtractor())

    result = node(
        {
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Python Developer",
                    "description": "Python is required.",
                }
            ]
        }
    )

    assert len(result["job_analyses"]) == 1

    analysis = result["job_analyses"][0]

    assert analysis["job_id"] == "job-001"
    assert len(analysis["requirement_groups"]) == 1
    assert analysis["requirement_groups"][0]["skills"] == ["Python"]


def test_job_analysis_node_multiple_jobs():
    node = create_job_analysis_node(FakeJobExtractor())

    result = node(
        {
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Python Developer",
                    "description": "Python is required.",
                },
                {
                    "id": "job-002",
                    "title": "ML Engineer",
                    "description": "Python is required.",
                },
            ]
        }
    )

    assert len(result["job_analyses"]) == 2

    assert [analysis["job_id"] for analysis in result["job_analyses"]] == [
        "job-001",
        "job-002",
    ]


def test_job_analysis_node_empty_jobs():
    node = create_job_analysis_node(FakeJobExtractor())

    result = node({"job_postings": []})

    assert result["job_analyses"] == []
