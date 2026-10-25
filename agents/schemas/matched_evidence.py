from pydantic import BaseModel

from agents.schemas.evidence import SkillEvidence
from agents.schemas.match_type import MatchType


class MatchedEvidence(BaseModel):
    evidence: SkillEvidence
    match_type: MatchType
