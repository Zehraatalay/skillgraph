import unittest
from app.ai.graph_import import apply_import_plan, make_import_plan
from app.ai.skill_profile import ValidatedSkillProfile, ProfileSkill, SkillEvidence


def example_profile():
    return ValidatedSkillProfile(developer='Zehraatalay', repository='Zehraatalay/stylematch',
        skills=[ProfileSkill(name='CNN', category='model_architecture', evidence_count=2, evidence=[
            SkillEvidence(repository='Zehraatalay/stylematch', file='a.py', quote='nn.Conv2d(3, 8, 3)', evidence_type='code_reference', decision_reason='matched', explanation='conv'),
            SkillEvidence(repository='Zehraatalay/stylematch', file='b.py', quote='resnet18(weights=weights)', evidence_type='code_reference', decision_reason='matched', explanation='resnet'),
        ])], accepted_evidence_count=2, excluded_findings_count=0)


class FakeDb:
    def __init__(self, preflight=None):
        self.calls = []
        self.preflight = preflight or {'developer_exists': True, 'repository_matches': 1, 'owned_repository_matches': 1}
    def run_query(self, query, parameters=None):
        self.calls.append((query, parameters))
        if 'developer_exists' in query:
            return [self.preflight]
        if 'RETURN skills_processed' in query:
            return [{'skills_processed': len(parameters['skills']), 'evidence_processed': len(parameters['evidence'])}]
        return []


class GraphImportTests(unittest.TestCase):
    def test_plan_deduplicates_evidence_and_is_deterministic(self):
        profile = example_profile()
        profile.skills[0].evidence.append(profile.skills[0].evidence[0].model_copy())
        first = make_import_plan(profile)
        self.assertEqual(len(first.skills), 1)
        self.assertEqual(len(first.evidence), 2)
        self.assertEqual(first.model_dump(), make_import_plan(profile).model_dump())

    def test_rejects_mismatched_owner(self):
        profile = example_profile()
        profile.developer = 'Other'
        with self.assertRaises(ValueError):
            make_import_plan(profile)

    def test_rejects_cross_repo_evidence(self):
        profile = example_profile()
        profile.skills[0].evidence[0].repository = 'other/repo'
        with self.assertRaises(ValueError):
            make_import_plan(profile)

    def test_rejects_unsafe_path(self):
        profile = example_profile()
        profile.skills[0].evidence[0].file = '../secret.py'
        with self.assertRaises(ValueError):
            make_import_plan(profile)

    def test_missing_graph_nodes_never_write(self):
        db = FakeDb({'developer_exists': True, 'repository_matches': 0, 'owned_repository_matches': 0})
        with self.assertRaises(ValueError):
            apply_import_plan(make_import_plan(example_profile()), db)
        self.assertEqual(len(db.calls), 1)

    def test_apply_uses_single_import_query(self):
        db = FakeDb()
        result = apply_import_plan(make_import_plan(example_profile()), db)
        self.assertEqual(result['evidence_processed'], 2)
        self.assertEqual(len(db.calls), 4)  # preflight, 2 constraints, one atomic import
        self.assertIn('MERGE (e:SkillEvidence', db.calls[-1][0])
