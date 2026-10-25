from agents.schemas.candidate import CandidateProfile
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job_requirement import RequirementPriority
from agents.schemas.requirement_group import (
    RequirementGroup,
    RequirementOperator,
)
from agents.schemas.semantic_matching import (
    SemanticMatchBatch,
    SemanticMatchDecision,
)
from agents.schemas.support_level import SupportLevel
from agents.services.hybrid_job_matcher import HybridJobMatcher


class FakeSemanticMatcher:
    def __init__(self, decisions):
        self.decisions = decisions
        self.calls = 0
        self.last_requirements = None

    def match(self, requirements, candidate_evidence):
        self.calls += 1
        self.last_requirements = requirements

        return SemanticMatchBatch(decisions=self.decisions)


def make_evidence(skill, reference=None):
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
        reference=reference or skill,
    )


def make_candidate(*skills):
    return CandidateProfile(skills=[make_evidence(skill) for skill in skills])


def make_job(*groups):
    return GroupedJobAnalysis(
        job_id="test-job",
        requirement_groups=list(groups),
    )


def make_group(
    skills,
    operator=RequirementOperator.ALL,
    priority=RequirementPriority.REQUIRED,
    evidence="Job requirement",
):
    return RequirementGroup(
        skills=skills,
        operator=operator,
        priority=priority,
        evidence=evidence,
    )


def make_decision(
    requirement_id,
    skill,
    support_level,
    indices=None,
):
    return SemanticMatchDecision(
        requirement_id=requirement_id,
        required_skill=skill,
        support_level=support_level,
        supporting_evidence_indices=indices or [],
        reasoning="Test decision",
    )


def test_hybrid_matcher_preserves_exact_matches():
    semantic = FakeSemanticMatcher([])

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("SQL"),
        make_job(make_group(["SQL"])),
    )

    assert result.required_coverage == 1.0
    assert result.requirements[0].satisfied is True
    assert semantic.calls == 0


def test_hybrid_matcher_adds_semantic_full_match():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "Data Analytics",
                SupportLevel.FULL,
                [0],
            )
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("Exploratory Data Analysis"),
        make_job(make_group(["Data Analytics"])),
    )

    skill = result.requirements[0].skills[0]

    assert skill.matched is True
    assert skill.support_level == SupportLevel.FULL
    assert result.required_coverage == 1.0
    assert semantic.calls == 1


def test_hybrid_matcher_adds_partial_support():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "MS Office",
                SupportLevel.PARTIAL,
                [0],
            )
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("Excel"),
        make_job(make_group(["MS Office"])),
    )

    skill = result.requirements[0].skills[0]

    assert skill.matched is False
    assert skill.support_level == SupportLevel.PARTIAL
    assert len(skill.partial_evidence) == 1
    assert result.required_coverage == 0.5
    assert result.requirements[0].satisfied is False


def test_hybrid_matcher_all_operator_coverage():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "MS Office",
                SupportLevel.PARTIAL,
                [0],
            ),
            make_decision(
                "0:1",
                "Data Analytics",
                SupportLevel.FULL,
                [1],
            ),
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate(
            "Excel",
            "Data Analysis",
        ),
        make_job(
            make_group(
                ["MS Office", "Data Analytics"],
                operator=RequirementOperator.ALL,
            )
        ),
    )

    requirement = result.requirements[0]

    assert requirement.coverage == 0.75
    assert requirement.satisfied is False


def test_hybrid_matcher_any_operator_coverage():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "Tableau",
                SupportLevel.NONE,
            ),
            make_decision(
                "0:1",
                "PowerBI",
                SupportLevel.PARTIAL,
                [0],
            ),
            make_decision(
                "0:2",
                "Qlik Sense",
                SupportLevel.NONE,
            ),
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("Data Visualization"),
        make_job(
            make_group(
                ["Tableau", "PowerBI", "Qlik Sense"],
                operator=RequirementOperator.ANY,
                priority=RequirementPriority.PREFERRED,
            )
        ),
    )

    requirement = result.requirements[0]

    assert requirement.coverage == 0.5
    assert requirement.satisfied is False
    assert result.preferred_coverage == 0.5


def test_hybrid_matcher_distinguishes_duplicate_skills():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "Python",
                SupportLevel.FULL,
                [0],
            ),
            make_decision(
                "1:0",
                "Python",
                SupportLevel.PARTIAL,
                [0],
            ),
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("Python Basics"),
        make_job(
            make_group(
                ["Python"],
                evidence="Knowledge of Python",
            ),
            make_group(
                ["Python"],
                evidence="Professional Python development experience",
            ),
        ),
    )

    first = result.requirements[0].skills[0]
    second = result.requirements[1].skills[0]

    assert first.support_level == SupportLevel.FULL
    assert second.support_level == SupportLevel.PARTIAL
    assert first.matched is True
    assert second.matched is False


def test_hybrid_matcher_rejects_invalid_evidence_indices():
    semantic = FakeSemanticMatcher(
        [
            make_decision(
                "0:0",
                "PowerBI",
                SupportLevel.FULL,
                [999],
            )
        ]
    )

    matcher = HybridJobMatcher(semantic)

    result = matcher.match(
        make_candidate("Python"),
        make_job(make_group(["PowerBI"])),
    )

    skill = result.requirements[0].skills[0]

    assert skill.matched is False
    assert skill.support_level == SupportLevel.NONE
    assert result.required_coverage == 0.0
