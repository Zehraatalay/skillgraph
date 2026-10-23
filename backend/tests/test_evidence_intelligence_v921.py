from app.ai.evidence_intelligence import assess_evidence, build_quality_report, detect_additional_technologies
from app.ai.schemas import RepositoryContext, SourceFile
from app.ai.skill_profile import SkillEvidence, ProfileSkill, ValidatedSkillProfile


def context(files):
    return RepositoryContext(owner='dev', repository='repo', files=[SourceFile(path=p, content=c, size=len(c)) for p, c in files.items()], skipped_files=0, total_characters=sum(map(len, files.values())))


def test_actual_api_call_and_alias():
    found = detect_additional_technologies(context({'a.py': 'import cv2 as cv\nx = cv.imread("a.png")\n'}))
    assert [s.name for s in found] == ['OpenCV']
    assert found[0].evidence[0].quote == 'x = cv.imread("a.png")'


def test_import_only_not_enough():
    assert detect_additional_technologies(context({'a.py': 'import cv2\n'})) == []


def test_unrelated_name_not_detected():
    assert detect_additional_technologies(context({'a.py': 'cv2.imread("a")\n'})) == []


def test_shadowed_import_not_detected():
    assert detect_additional_technologies(context({'a.py': 'import cv2\ncv2 = object()\ncv2.imread("a")\n'})) == []


def test_syntax_error_skipped():
    assert detect_additional_technologies(context({'a.py': 'def nope(:\n'})) == []


def test_from_import_usage():
    found = detect_additional_technologies(context({'a.py': 'from numpy import array as arr\nx = arr([1])\n'}))
    assert [s.name for s in found] == ['NumPy']


def test_one_evidence_per_file():
    found = detect_additional_technologies(context({'a.py': 'import numpy as np\na = np.array([1])\nb = np.zeros(3)\n'}))
    assert found[0].evidence_count == 1


def test_quality_verbatim_and_missing_quote():
    ev = SkillEvidence(repository='dev/repo', file='a.py', quote='def run():', evidence_type='ast_source_usage', decision_reason='', explanation='')
    result = assess_evidence(ev, 'def run():\n    return 3\n')
    assert result.quality == 'medium'
    assert 'return 3' in result.snippet
    assert assess_evidence(ev, 'x = 1').quality == 'unverified'


def test_report_no_score_or_profile_mutation():
    ev = SkillEvidence(repository='dev/repo', file='a.py', quote='x = 1', evidence_type='ast_source_usage', decision_reason='', explanation='')
    profile = ValidatedSkillProfile(developer='dev', repository='dev/repo', skills=[ProfileSkill(name='Python', category='programming_language', evidence_count=1, evidence=[ev])], accepted_evidence_count=1, excluded_findings_count=0)
    before = profile.model_dump_json()
    report = build_quality_report(profile, context({'a.py': 'x = 1\n'}))
    assert report['items'][0]['quality'] == 'weak'
    assert profile.model_dump_json() == before
