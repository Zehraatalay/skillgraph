"""Explicit, idempotent import of accepted code evidence into an existing Neo4j graph.

No DB connection is opened while constructing an import plan.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import PurePosixPath

from pydantic import BaseModel, Field

from app.ai.skill_profile import ValidatedSkillProfile


class ImportPlan(BaseModel):
    developer: str
    repository: str
    skills: list[dict] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)


def make_import_plan(profile: ValidatedSkillProfile) -> ImportPlan:
    owner, sep, repo = profile.repository.partition('/')
    if not sep or not owner or not repo or '/' in repo or owner.casefold() != profile.developer.casefold():
        raise ValueError('Profile developer and owner/repository must agree')
    skill_rows: dict[str, dict] = {}
    evidence_rows: dict[str, dict] = {}
    for skill in profile.skills:
        name = skill.name.strip()
        if not name:
            raise ValueError('Skill name cannot be blank')
        skill_rows[name.casefold()] = {'name': name, 'category': skill.category}
        for evidence in skill.evidence:
            if evidence.repository != profile.repository:
                raise ValueError('Cross-repository evidence is not allowed in a repository profile')
            path = PurePosixPath(evidence.file)
            if not evidence.file or path.is_absolute() or '..' in path.parts or '\\' in evidence.file:
                raise ValueError('Evidence must have a safe relative POSIX path')
            if not evidence.quote.strip():
                raise ValueError('Evidence quote cannot be blank')
            # Include skill so one source quote can support multiple distinct skills.
            raw_key = '\x00'.join((profile.repository.casefold(), name.casefold(), evidence.file, evidence.quote))
            evidence_id = sha256(raw_key.encode('utf-8')).hexdigest()
            evidence_rows[evidence_id] = {
                'id': evidence_id, 'skill_name': name, 'repository': profile.repository,
                'file': evidence.file, 'quote': evidence.quote,
                'evidence_type': evidence.evidence_type,
                'decision_reason': evidence.decision_reason,
                'explanation': evidence.explanation,
            }
    return ImportPlan(developer=profile.developer, repository=profile.repository,
                      skills=sorted(skill_rows.values(), key=lambda x: x['name'].casefold()),
                      evidence=sorted(evidence_rows.values(), key=lambda x: x['id']))


PREFLIGHT_QUERY = '''
OPTIONAL MATCH (d:Developer {login: $developer})
WITH d
OPTIONAL MATCH (r:Repository {full_name: $repository})
RETURN d IS NOT NULL AS developer_exists,
       count(DISTINCT r) AS repository_matches,
       count(DISTINCT CASE WHEN (d)-[:OWNS]->(r) THEN r END) AS owned_repository_matches
'''

# A single query performs the import, so it is atomic in Neo4j.
# MATCH instead of MERGE for Developer and Repository avoids phantom nodes.
IMPORT_QUERY = '''
MATCH (d:Developer {login: $developer})-[:OWNS]->(r:Repository {full_name: $repository})
CALL (d, r) {
  UNWIND $skills AS item
  MERGE (s:Skill {name: item.name})
  ON CREATE SET s.created_at = datetime()
  SET s.category = item.category
  MERGE (d)-[has:HAS_SKILL]->(s)
  SET has.updated_at = datetime()
  RETURN count(*) AS skills_processed
}
CALL (r) {
  UNWIND $evidence AS item
  MATCH (s:Skill {name: item.skill_name})
  MERGE (e:SkillEvidence {evidence_id: item.id})
  ON CREATE SET e.created_at = datetime()
  SET e.file = item.file,
      e.quote = item.quote,
      e.repository = item.repository,
      e.evidence_type = item.evidence_type,
      e.decision_reason = item.decision_reason,
      e.explanation = item.explanation
  MERGE (r)-[:HAS_EVIDENCE]->(e)
  MERGE (e)-[:SUPPORTS]->(s)
  RETURN count(*) AS evidence_processed
}
RETURN skills_processed, evidence_processed
'''

CONSTRAINTS = [
    'CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE',
    'CREATE CONSTRAINT skill_evidence_id_unique IF NOT EXISTS FOR (e:SkillEvidence) REQUIRE e.evidence_id IS UNIQUE',
]


def apply_import_plan(plan: ImportPlan, repository) -> dict:
    """Write only after verifying the existing Developer-OWNS-Repository chain.

    `repository` must expose run_query(query, params); intended for Neo4jRepository.
    """
    rows = repository.run_query(PREFLIGHT_QUERY, {'developer': plan.developer, 'repository': plan.repository})
    if len(rows) != 1 or not rows[0]['developer_exists'] or rows[0]['repository_matches'] != 1 or rows[0]['owned_repository_matches'] != 1:
        raise ValueError('Existing Developer OWNS Repository chain not found or ambiguous. Import GitHub data first.')
    for query in CONSTRAINTS:
        repository.run_query(query)
    result = repository.run_query(IMPORT_QUERY, plan.model_dump())
    if len(result) != 1:
        raise RuntimeError('Graph import returned no result; transaction may not have matched existing nodes')
    return result[0]
