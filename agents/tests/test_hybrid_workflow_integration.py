import pytest

from agents.graph.workflow import build_workflow
from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.github import GitHubAnalysis
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup
from agents.schemas.semantic_matching import (
    SemanticMatchBatch,
    SemanticMatchDecision,
)
from agents.schemas.support_level import SupportLevel
from agents.services.explainable_job_matcher import (
    ExplainableJobMatcher,
)
from agents.services.hybrid_job_matcher import HybridJobMatcher


class FakeCVExtractor:
    def extract(self, text):
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                ),
                SkillEvidence(
                    skill="Data Analysis",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.IMPLEMENTATION,
                    description=(
                        "Developed a sales forecasting "
                        "project using Pandas and LightGBM."
                    ),
                ),
                SkillEvidence(
                    skill="Excel",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                ),
            ],
        )


class FakeGitHubAnalyzer:
    def analyze_user(self, username):
        return GitHubAnalysis(
            username=username,
            repositories=[],
        )


class FakeJobExtractor:
    def extract(self, job):
        return GroupedJobAnalysis(
            job_id=job.id,
            requirement_groups=[
                RequirementGroup(
                    skills=["Python"],
                    operator="all",
                    priority="required",
                    evidence="Python proficiency is required.",
                ),
                RequirementGroup(
                    skills=["Data Analytics"],
                    operator="all",
                    priority="required",
                    evidence="Strong data analytics skills.",
                ),
                RequirementGroup(
                    skills=["MS Office"],
                    operator="all",
                    priority="required",
                    evidence="Proficiency in MS Office.",
                ),
                RequirementGroup(
                    skills=["Tableau"],
                    operator="all",
                    priority="preferred",
                    evidence="Tableau experience is preferred.",
                ),
            ],
        )


class FakeSemanticMatcher:
    def __init__(self):
        self.calls = []

    def match(self, requirements, candidate_evidence):
        self.calls.append(
            {
                "requirements": requirements,
                "candidate_evidence": candidate_evidence,
            }
        )

        decisions = []

        for requirement in requirements:
            skill = requirement["skill"]

            if skill == "Data Analytics":
                decisions.append(
                    SemanticMatchDecision(
                        requirement_id=requirement["id"],
                        required_skill=skill,
                        support_level=SupportLevel.FULL,
                        supporting_evidence_indices=[1],
                        reasoning=(
                            "Data Analysis is directly relevant to Data Analytics."
                        ),
                    )
                )

            elif skill == "MS Office":
                decisions.append(
                    SemanticMatchDecision(
                        requirement_id=requirement["id"],
                        required_skill=skill,
                        support_level=SupportLevel.PARTIAL,
                        supporting_evidence_indices=[2],
                        reasoning=("Excel provides partial evidence for MS Office."),
                    )
                )

            else:
                decisions.append(
                    SemanticMatchDecision(
                        requirement_id=requirement["id"],
                        required_skill=skill,
                        support_level=SupportLevel.NONE,
                        supporting_evidence_indices=[],
                        reasoning="No supporting evidence.",
                    )
                )

        return SemanticMatchBatch(
            decisions=decisions,
        )


@pytest.fixture
def hybrid_workflow():
    semantic_matcher = FakeSemanticMatcher()

    hybrid_matcher = HybridJobMatcher(
        semantic_matcher=semantic_matcher,
    )

    explainable_matcher = ExplainableJobMatcher(
        job_matcher=hybrid_matcher,
    )

    graph = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
        job_extractor=FakeJobExtractor(),
        job_matcher=explainable_matcher,
    )

    return graph, semantic_matcher


def test_hybrid_workflow_end_to_end(hybrid_workflow):
    graph, semantic_matcher = hybrid_workflow

    result = graph.invoke(
        {
            "cv_text": "Python, Data Analysis, Excel",
            "github_username": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Data Analyst",
                    "description": ("Python, Data Analytics, MS Office, Tableau."),
                }
            ],
        }
    )

    assert len(result["results"]) == 1

    match = result["results"][0]
    match_result = match["match_result"]

    # Semantic matching was executed.
    assert match_result["semantic_status"] == "completed"

    # Deterministic + semantic matching.
    assert match_result["required_coverage"] == pytest.approx((1.0 + 1.0 + 0.5) / 3)

    assert match_result["preferred_coverage"] == 0.0

    requirements = match_result["requirements"]

    assert len(requirements) == 4

    python_skill = requirements[0]["skills"][0]
    analytics_skill = requirements[1]["skills"][0]
    office_skill = requirements[2]["skills"][0]
    tableau_skill = requirements[3]["skills"][0]

    # Python: deterministic FULL.
    assert python_skill["matched"] is True
    assert python_skill["support_level"] == "full"

    # Data Analytics: semantic FULL.
    assert analytics_skill["matched"] is True
    assert analytics_skill["support_level"] == "full"

    assert len(analytics_skill["matched_evidence"]) == 1

    assert analytics_skill["matched_evidence"][0]["match_type"] == "alias"

    # MS Office: semantic PARTIAL.
    assert office_skill["matched"] is False
    assert office_skill["support_level"] == "partial"

    assert len(office_skill["partial_evidence"]) == 1

    assert office_skill["partial_evidence"][0]["skill"] == "Excel"

    # Tableau: NONE.
    assert tableau_skill["matched"] is False
    assert tableau_skill["support_level"] == "none"

    # Only unmatched deterministic skills
    # should be sent to semantic matching.
    assert len(semantic_matcher.calls) == 1

    semantic_requirements = semantic_matcher.calls[0]["requirements"]

    assert [requirement["skill"] for requirement in semantic_requirements] == [
        "MS Office",
        "Tableau",
    ]


def test_hybrid_workflow_preserves_explanations(
    hybrid_workflow,
):
    graph, _ = hybrid_workflow

    result = graph.invoke(
        {
            "cv_text": "Python, Data Analysis, Excel",
            "github_username": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Data Analyst",
                    "description": "Data analytics skills.",
                }
            ],
        }
    )

    match = result["results"][0]

    # Explainability output is preserved.
    assert "summary" in match
    assert "explained_requirements" in match

    summary = match["summary"]

    assert summary["required"]["coverage"] == pytest.approx((1.0 + 1.0 + 0.5) / 3)

    assert len(match["explained_requirements"]) == 4

    # Python and Data Analytics are satisfied.
    assert summary["required"]["satisfied"] == 2

    # MS Office is partially covered.
    assert summary["required"]["partial"] == 1

    # Tableau remains missing.
    assert summary["preferred"]["missing"] == 1


def test_hybrid_workflow_semantic_failure_fallback():
    class FailingSemanticMatcher:
        def match(self, requirements, candidate_evidence):
            raise RuntimeError("Simulated Gemini failure")

    hybrid_matcher = HybridJobMatcher(
        semantic_matcher=FailingSemanticMatcher(),
    )

    graph = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
        job_extractor=FakeJobExtractor(),
        job_matcher=ExplainableJobMatcher(
            job_matcher=hybrid_matcher,
        ),
    )

    result = graph.invoke(
        {
            "cv_text": "Python, Data Analysis, Excel",
            "github_username": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Data Analyst",
                    "description": "Python and data analytics.",
                }
            ],
        }
    )

    match_result = result["results"][0]["match_result"]

    assert match_result["semantic_status"] == "failed"

    # Deterministic matching is still available.
    assert match_result["requirements"][0]["skills"][0]["matched"] is True

    assert match_result["required_coverage"] == pytest.approx(2.0 / 3)
