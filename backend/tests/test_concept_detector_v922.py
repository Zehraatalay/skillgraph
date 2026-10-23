from app.ai.concept_detector import concept_report, detect_concept_candidates
from app.ai.schemas import RepositoryContext, SourceFile


def ctx(source, path='agent.py'):
    return RepositoryContext(owner='dev', repository='game', files=[SourceFile(path=path, content=source, size=len(source))], skipped_files=0, total_characters=len(source))


def test_import_or_function_name_does_not_imply_algorithm():
    assert detect_concept_candidates(ctx('def minimax(board):\n    return 1\n')) == []


def test_queue_pattern_requires_loop_membership():
    code = '''from collections import deque

def traverse(start):
    queue = deque([start])
    seen = set()
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        for child in children(node):
            queue.append(child)
'''
    items = detect_concept_candidates(ctx(code))
    assert any(x.concept == 'Queue-based graph traversal' for x in items)
    assert all(x.status == 'needs_review' for x in items)


def test_priority_queue_pattern():
    code = '''from heapq import heappop, heappush

def search(q):
    while q:
        item = heappop(q)
        heappush(q, item)
'''
    assert 'Priority-queue search' in [x.concept for x in detect_concept_candidates(ctx(code))]


def test_memoization():
    assert 'Memoization' in [x.concept for x in detect_concept_candidates(ctx('@lru_cache(maxsize=10)\ndef f(x):\n    return x\n'))]


def test_invalid_syntax_and_nonpython_ignored():
    assert detect_concept_candidates(ctx('def nope(:')) == []
    assert detect_concept_candidates(ctx('def f(): pass', 'test.js')) == []


def test_report_does_not_claim_verified_skill():
    report = concept_report(ctx('def greedy(x):\n    return max(x)\n'))
    assert report['candidate_count'] == 0
    assert report['status'] == 'review_required'
    assert 'NOT verified skills' in report['warning']
