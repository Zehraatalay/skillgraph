import logging

from agents.schemas.candidate import CandidateProfile
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job_requirement import RequirementPriority
from agents.schemas.match_type import MatchType
from agents.schemas.matched_evidence import MatchedEvidence
from agents.schemas.matching import JobMatchResult
from agents.schemas.support_level import SupportLevel
from agents.services.job_matcher import JobMatcher
from agents.services.semantic_skill_matcher import (
    SemanticSkillMatcher,
)

logger = logging.getLogger(__name__)


class HybridJobMatcher:
    def __init__(
        self,
        semantic_matcher: SemanticSkillMatcher,
        job_matcher: JobMatcher | None = None,
    ):
        self.semantic_matcher = semantic_matcher
        self.job_matcher = job_matcher or JobMatcher()

    def match(
        self,
        candidate: CandidateProfile,
        job: GroupedJobAnalysis,
    ) -> JobMatchResult:

        # --------------------------------------------------
        # 1. Deterministic matching
        # --------------------------------------------------

        deterministic_result = self.job_matcher.match(
            candidate,
            job,
        )

        # --------------------------------------------------
        # 2. Collect unmatched requirements
        # --------------------------------------------------

        unmatched_requirements = []

        for group_index, (
            requirement_group,
            requirement_match,
        ) in enumerate(
            zip(
                job.requirement_groups,
                deterministic_result.requirements,
            )
        ):
            for skill_index, skill_match in enumerate(requirement_match.skills):
                if skill_match.matched:
                    continue

                unmatched_requirements.append(
                    {
                        "id": f"{group_index}:{skill_index}",
                        "skill": skill_match.skill,
                        "context": requirement_group.evidence,
                    }
                )

        if not unmatched_requirements:
            return deterministic_result

        # --------------------------------------------------
        # 3. Semantic matching (single batch)
        # --------------------------------------------------

        try:
            semantic_result = self.semantic_matcher.match(
                requirements=unmatched_requirements,
                candidate_evidence=candidate.skills,
            )
        except Exception:
            logger.exception(
                "Semantic matching failed; falling back to deterministic matching."
            )

            return deterministic_result.model_copy(
                update={
                    "semantic_status": "failed",
                }
            )

        # Decisions are indexed by unique requirement ID,
        # not by skill name.
        semantic_decisions = {
            decision.requirement_id: decision
            for decision in semantic_result.decisions
            if decision.requirement_id is not None
        }

        # --------------------------------------------------
        # 4. Merge semantic decisions
        # --------------------------------------------------

        updated_requirements = []

        for group_index, (
            requirement_group,
            requirement_match,
        ) in enumerate(
            zip(
                job.requirement_groups,
                deterministic_result.requirements,
            )
        ):
            updated_skills = []

            for skill_index, skill_match in enumerate(requirement_match.skills):
                # Deterministic matches take precedence.
                if skill_match.matched:
                    updated_skills.append(skill_match)
                    continue

                requirement_id = f"{group_index}:{skill_index}"

                decision = semantic_decisions.get(requirement_id)

                if decision is None:
                    updated_skills.append(skill_match)
                    continue

                # Defensive validation:
                # Only use indices from candidate evidence.
                valid_indices = [
                    index
                    for index in decision.supporting_evidence_indices
                    if (
                        isinstance(index, int)
                        and not isinstance(index, bool)
                        and 0 <= index < len(candidate.skills)
                    )
                ]

                valid_indices = list(dict.fromkeys(valid_indices))

                supporting_evidence = [
                    candidate.skills[index] for index in valid_indices
                ]

                # --------------------------------------------------
                # FULL support
                # --------------------------------------------------

                if decision.support_level == SupportLevel.FULL and supporting_evidence:
                    updated_skill = skill_match.model_copy(
                        update={
                            "matched": True,
                            "support_level": SupportLevel.FULL,
                            "matched_evidence": [
                                MatchedEvidence(
                                    evidence=evidence,
                                    match_type=MatchType.SEMANTIC,
                                )
                                for evidence in supporting_evidence
                            ],
                            "partial_evidence": [],
                        }
                    )

                # --------------------------------------------------
                # PARTIAL support
                # --------------------------------------------------

                elif (
                    decision.support_level == SupportLevel.PARTIAL
                    and supporting_evidence
                ):
                    updated_skill = skill_match.model_copy(
                        update={
                            "matched": False,
                            "support_level": SupportLevel.PARTIAL,
                            "matched_evidence": [],
                            "partial_evidence": supporting_evidence,
                        }
                    )

                # --------------------------------------------------
                # NONE / invalid evidence
                # --------------------------------------------------

                else:
                    updated_skill = skill_match

                updated_skills.append(updated_skill)

            # Recalculate group coverage after semantic merging.
            updated_requirement = self.job_matcher.requirement_matcher.build_result(
                requirement_group,
                updated_skills,
            )

            updated_requirements.append(updated_requirement)

        # --------------------------------------------------
        # 5. Recalculate job-level coverage
        # --------------------------------------------------

        required_matches = [
            requirement
            for requirement in updated_requirements
            if requirement.priority == RequirementPriority.REQUIRED
        ]

        preferred_matches = [
            requirement
            for requirement in updated_requirements
            if requirement.priority == RequirementPriority.PREFERRED
        ]

        return JobMatchResult(
            job_id=job.job_id,
            requirements=updated_requirements,
            required_coverage=self.job_matcher._average_coverage(required_matches),
            preferred_coverage=self.job_matcher._average_coverage(preferred_matches),
            semantic_status="completed",
        )
