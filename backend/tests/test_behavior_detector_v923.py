from app.ai.behavior_detector import behavior_report
from app.ai.schemas import RepositoryContext, SourceFile


def report(code: str):
    ctx = RepositoryContext(owner='dev', repository='repo', files=[SourceFile(path='logic.py', content=code, size=len(code))], skipped_files=0, total_characters=len(code))
    return behavior_report(ctx)


def concepts(code: str):
    return {i['concept'] for i in report(code)['items']}


def test_conditional_enumeration():
    assert 'Conditional candidate enumeration' in concepts('def f(xs):\n    out=[]\n    for x in xs:\n        if x > 0:\n            out.append(x)\n    return out\n')


def test_no_enumeration_without_filter():
    assert 'Conditional candidate enumeration' not in concepts('def f(xs):\n    out=[]\n    for x in xs:\n        out.append(x)\n    return out\n')


def test_best_candidate():
    assert 'Iterative best-candidate selection' in concepts('def f(xs):\n    best=0\n    for x in xs:\n        if x > best:\n            best=x\n    return best\n')


def test_copy_and_update():
    assert 'Copy-and-update state transformation' in concepts('def f(state):\n    new=state.copy()\n    new[0]=1\n    return new\n')


def test_assertion_detection():
    assert 'Executable behavioral assertions' in concepts('def check(x):\n    assert x > 0\n')


def test_name_only_not_a_skill():
    assert concepts('def greedy_search():\n    return 1\n') == set()


def test_cache_read_and_write():
    assert 'Explicit cache lookup and update' in concepts('def f(cache, key):\n    if key in cache:\n        return cache[key]\n    cache[key] = 3\n    return cache[key]\n')


def test_no_cache_without_write():
    assert 'Explicit cache lookup and update' not in concepts('def f(cache, key):\n    if key in cache:\n        return cache[key]\n    return None\n')


def test_nested_function_does_not_leak_to_parent():
    data = report('def outer():\n    def inner():\n        assert True\n    return inner\n')
    assert len([x for x in data['items'] if x['function'] == 'outer']) == 0
    assert len([x for x in data['items'] if x['function'] == 'inner']) == 1


def test_syntax_error_is_reported():
    data = report('def broken(:\n')
    assert data['candidate_count'] == 0
    assert data['parse_errors'][0]['file'] == 'logic.py'
