from app.ai.schemas import RepositoryContext, SourceFile
from app.ai.technology_detector import detect_technology_skills
from app.ai.profile_merger import merge_profile_skills
from app.ai.skill_profile import ValidatedSkillProfile
from app.ai.graph_import import make_import_plan


def ctx(content, path='model.py'):
    return RepositoryContext(owner='dev', repository='repo', files=[SourceFile(path=path, content=content, size=len(content))])


def test_alias_api_usage():
    skills = detect_technology_skills(ctx('import torch.nn as neural\nlayer = neural.Conv2d(3, 4, 3)\n'))
    assert {s.name for s in skills} == {'Python', 'PyTorch'}


def test_from_import_usage():
    skills = detect_technology_skills(ctx('from torch.nn import Conv2d as Conv\nlayer = Conv(3, 4, 3)\n'))
    assert 'PyTorch' in {s.name for s in skills}


def test_import_only_not_usage():
    assert detect_technology_skills(ctx('import torch\n')) == []


def test_requirements_not_usage():
    assert detect_technology_skills(ctx('torch==2.0', 'requirements.txt')) == []


def test_invalid_python_skipped():
    assert detect_technology_skills(ctx('def bad(')) == []


def test_unrelated_calls_not_pytorch():
    skills = detect_technology_skills(ctx('import torch\nprint("hello")\n'))
    assert {s.name for s in skills} == {'Python'}


def test_merge_idempotent_and_importable():
    additions = detect_technology_skills(ctx('import torch.nn as nn\nmodel = nn.Conv2d(3, 4, 3)\n'))
    empty = ValidatedSkillProfile(developer='dev', repository='dev/repo', skills=[], accepted_evidence_count=0, excluded_findings_count=0)
    once = merge_profile_skills(empty, additions)
    twice = merge_profile_skills(once, additions)
    assert once.model_dump() == twice.model_dump()
    plan = make_import_plan(twice)
    assert len(plan.skills) == 2
    assert len(plan.evidence) == 2
