"""V10 read-only graph integrity audit. No database mutations."""
from __future__ import annotations
import argparse
import json

AUDIT_QUERY = """
MATCH (d:Developer)-[:OWNS]->(r:Repository)
WHERE toLower(d.login) = toLower($username)
OPTIONAL MATCH (r)-[:HAS_EVIDENCE]->(e:SkillEvidence)
WITH r, e
OPTIONAL MATCH (e)-[:SUPPORTS]->(s:Skill)
RETURN r.full_name AS repository, e.evidence_id AS evidence_id,
       e.repository AS evidence_repository, s.name AS skill,
       e.file AS file, e.quote AS quote
ORDER BY repository, evidence_id, skill
"""

def summarize(rows: list[dict], username: str) -> dict:
    repos = set(); unique = set(); violations = []; skills = set()
    for row in rows:
        repo = row.get('repository')
        if not repo:
            violations.append({'kind':'missing_repository','row':row}); continue
        repos.add(repo)
        eid = row.get('evidence_id')
        if eid is None: continue  # repository with no evidence
        key = (repo, eid, row.get('skill'))
        if key in unique: violations.append({'kind':'duplicate_edge_row','repository':repo,'evidence_id':eid})
        unique.add(key)
        if row.get('evidence_repository') != repo:
            violations.append({'kind':'repository_mismatch','repository':repo,'evidence_id':eid})
        if not row.get('skill'):
            violations.append({'kind':'missing_skill_link','repository':repo,'evidence_id':eid})
        else: skills.add(row['skill'])
        if not row.get('file') or not str(row.get('quote') or '').strip():
            violations.append({'kind':'missing_source_evidence','repository':repo,'evidence_id':eid})
    return {'username':username,'repositories':sorted(repos),'repository_count':len(repos),
            'skill_count':len(skills),'unique_evidence_count':len({(r,e) for r,e,_ in unique}),
            'issues':violations,'issue_count':len(violations),
            'note':'Read-only structural audit; does not verify live GitHub source or remove stale evidence.'}

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--username',required=True)
    p.add_argument('--output')
    args=p.parse_args()
    from app.repositories.neo4j_repository import Neo4jRepository
    db=Neo4jRepository()
    try: rows=db.run_query(AUDIT_QUERY,{'username':args.username})
    finally: db.close()
    result=summarize(rows,args.username)
    rendered=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(rendered+'\n',encoding='utf-8')
    print(rendered)
    if result['issue_count']: raise SystemExit(2)

if __name__=='__main__': main()
