import json
import logging

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from agents.schemas.evidence import SkillEvidence
from agents.schemas.semantic_matching import (
    SemanticMatchBatch,
    SemanticMatchDecision,
)
from agents.schemas.support_level import SupportLevel
from agents.services.cv_extractor import (
    is_temporary_gemini_error,
)

logger = logging.getLogger(__name__)


class SemanticSkillMatcher:
    def __init__(self, model):
        self.structured_model = model.with_structured_output(
            SemanticMatchBatch,
            method="json_schema",
        )

    @retry(
        retry=retry_if_exception(is_temporary_gemini_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=8,
        ),
        reraise=True,
    )
    def _invoke_model(self, prompt: str) -> SemanticMatchBatch:
        return self.structured_model.invoke(prompt)

    def match(
        self,
        requirements: list[dict],
        candidate_evidence: list[SkillEvidence],
    ) -> SemanticMatchBatch:
        if not requirements:
            return SemanticMatchBatch()

        if not candidate_evidence:
            return SemanticMatchBatch(
                decisions=[
                    SemanticMatchDecision(
                        required_skill=requirement["skill"],
                        support_level=SupportLevel.NONE,
                        supporting_evidence_indices=[],
                        reasoning="No candidate evidence was provided.",
                    )
                    for requirement in requirements
                ]
            )

        requirement_payload = [
            {
                "requirement_id": requirement.get("id"),
                "skill": requirement["skill"],
                "context": requirement.get("context", ""),
            }
            for requirement in requirements
        ]

        evidence_payload = [
            {
                "index": index,
                "skill": evidence.skill,
                "description": evidence.description,
                "source": evidence.source.value,
                "evidence_type": evidence.evidence_type.value,
                "reference": evidence.reference,
            }
            for index, evidence in enumerate(candidate_evidence)
        ]

        prompt = f"""
You are an evidence-grounded technical skill evaluator.

Your task is to determine how well candidate evidence
supports each job requirement.

IMPORTANT RULES:

1. Evaluate each requirement independently.
2. Use only the candidate evidence provided.
3. Do not invent skills, projects, employment, or experience.
4. Consider both skill names and requirement context.
5. Distinguish semantic equivalence from partial relevance.
6. Do not assume related technologies are interchangeable.
7. Do not treat academic coursework as professional experience.
8. Do not infer production deployment from academic knowledge.
9. A tool belonging to a software suite does not automatically
   demonstrate proficiency in the entire suite.
10. A programming language does not automatically demonstrate
    experience with every framework or application of that language.

SUPPORT LEVEL DEFINITIONS:

FULL:
The provided evidence sufficiently supports the requirement
at the level expressed in its context.

PARTIAL:
The evidence demonstrates relevant knowledge or experience,
but does not fully establish the requirement.

NONE:
The provided evidence does not establish meaningful support.

EXAMPLES:

Requirement: Data Analytics
Evidence: Python (data analysis)
Decision: FULL

Requirement: MS Office
Evidence: Excel
Decision: PARTIAL

Requirement: Professional ML deployment
Evidence: Machine Learning coursework
Decision: PARTIAL

Requirement: PowerBI
Evidence: Python
Decision: NONE

EVIDENCE RULES:

- Return only evidence indices from the provided list.
- Never invent evidence indices.
- Do not cite unrelated evidence.
- For NONE decisions, return an empty evidence index list.
- For FULL and PARTIAL decisions, return at least one
  supporting evidence index.
- Return exactly one decision per requirement.
- Preserve the required_skill text exactly.
- Keep reasoning concise and evidence-specific.
- Preserve the requirement_id exactly as provided.
- Use requirement_id to distinguish requirements with identical skill names.

JOB REQUIREMENTS:
{json.dumps(requirement_payload, ensure_ascii=False, indent=2)}

CANDIDATE EVIDENCE:
{json.dumps(evidence_payload, ensure_ascii=False, indent=2)}
"""

        result = self._invoke_model(prompt)

        return self._validate_result(
            result=result,
            requirements=requirements,
            candidate_evidence=candidate_evidence,
        )

    def _validate_result(
        self,
        result: SemanticMatchBatch,
        requirements: list[dict],
        candidate_evidence: list[SkillEvidence],
    ) -> SemanticMatchBatch:

        expected_by_id = {
            requirement["id"]: requirement["skill"]
            for requirement in requirements
            if requirement.get("id") is not None
        }

        expected_without_id = {
            requirement["skill"]
            for requirement in requirements
            if requirement.get("id") is None
        }

        decisions_by_key = {}

        for decision in result.decisions:
            if decision.requirement_id is not None:
                expected_skill = expected_by_id.get(decision.requirement_id)

                if expected_skill != decision.required_skill:
                    continue

                key = ("id", decision.requirement_id)

            else:
                if decision.required_skill not in expected_without_id:
                    continue

                key = ("skill", decision.required_skill)

            if key in decisions_by_key:
                continue

            valid_indices = [
                index
                for index in decision.supporting_evidence_indices
                if (
                    isinstance(index, int)
                    and not isinstance(index, bool)
                    and 0 <= index < len(candidate_evidence)
                )
            ]

            valid_indices = list(dict.fromkeys(valid_indices))

            if decision.support_level == SupportLevel.NONE:
                valid_indices = []

            elif not valid_indices:
                decision = decision.model_copy(
                    update={
                        "support_level": SupportLevel.NONE,
                        "reasoning": "No valid supporting evidence.",
                    }
                )

            decisions_by_key[key] = decision.model_copy(
                update={
                    "supporting_evidence_indices": valid_indices,
                }
            )

        validated = []

        for requirement in requirements:
            requirement_id = requirement.get("id")

            key = (
                ("id", requirement_id)
                if requirement_id is not None
                else ("skill", requirement["skill"])
            )

            decision = decisions_by_key.get(key)

            if decision is None:
                decision = SemanticMatchDecision(
                    requirement_id=requirement_id,
                    required_skill=requirement["skill"],
                    support_level=SupportLevel.NONE,
                    supporting_evidence_indices=[],
                    reasoning="No valid semantic decision returned.",
                )

            validated.append(decision)

        return SemanticMatchBatch(decisions=validated)
