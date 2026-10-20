import unittest

from app.matching.evidence_matching import _group_evidence, rank_jobs, score_job


def job(required=None, preferred=None):
    return {'job_id': 'job-1', 'title': 'Engineer', 'role_family': 'ai',
            'seniority': 'junior', 'technology_stack_id': 'ai',
            'required_skills': required or [], 'preferred_skills': preferred or []}


def skill(name, weight=1.0):
    return {'name': name, 'weight': weight}


class EvidenceMatchingTests(unittest.TestCase):
    def test_required_only_can_reach_100(self):
        result = score_job(job([skill('CNN')]), {'cnn': [{'file': 'a.py'}]})
        self.assertEqual(result['verified_skill_coverage_score'], 100)

    def test_weighted_required_and_preferred(self):
        result = score_job(job([skill('python', 1), skill('docker', .5)],
                               [skill('redis')]), {'python': [{'file': 'a.py'}]})
        self.assertAlmostEqual(result['verified_skill_coverage_score'], 53.33, places=2)

    def test_unknown_is_unverified_not_missing(self):
        result = score_job(job([skill('pytorch')]), {})
        self.assertEqual(result['unverified_required_skills'], ['pytorch'])
        self.assertEqual(result['verified_required_skills'], [])

    def test_deduplicate_evidence_by_id(self):
        row = {'skill': 'CNN', 'evidence_id': 'id1', 'repository': 'a/b',
               'file': 'x.py', 'quote': 'nn.Conv2d(', 'evidence_type': 'code',
               'explanation': ''}
        grouped = _group_evidence([row, row])
        self.assertEqual(len(grouped['cnn']), 1)

    def test_no_evidence_does_not_infer_technology(self):
        result = score_job(job([skill('python')]), {})
        self.assertEqual(result['verified_skill_coverage_score'], 0)

    def test_deterministic_order(self):
        result = rank_jobs([job([skill('python')])], [], 10)
        self.assertEqual(result['total_jobs_evaluated'], 1)
        self.assertEqual(result['verified_skill_count'], 0)

    def test_empty_groups_have_zero_score(self):
        result = score_job(job(), {})
        self.assertEqual(result['verified_skill_coverage_score'], 0)
        self.assertIsNone(result['required_coverage'])


if __name__ == '__main__':
    unittest.main()
