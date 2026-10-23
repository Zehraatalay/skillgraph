from app.ai.v10_graph_audit import summarize

def test_valid():
    data=summarize([{'repository':'u/a','evidence_id':'1','evidence_repository':'u/a','skill':'Python','file':'a.py','quote':'def a():'}], 'u')
    assert data['issue_count']==0
    assert data['unique_evidence_count']==1

def test_mismatched_repository():
    data=summarize([{'repository':'u/a','evidence_id':'1','evidence_repository':'u/b','skill':'Python','file':'a.py','quote':'x'}], 'u')
    assert any(x['kind']=='repository_mismatch' for x in data['issues'])

def test_missing_skill_and_quote():
    data=summarize([{'repository':'u/a','evidence_id':'1','evidence_repository':'u/a','skill':None,'file':'a.py','quote':''}], 'u')
    assert data['issue_count']==2

def test_empty_repository():
    data=summarize([{'repository':'u/a','evidence_id':None}], 'u')
    assert data['repository_count']==1 and data['unique_evidence_count']==0

def test_duplicate_rows():
    row={'repository':'u/a','evidence_id':'1','evidence_repository':'u/a','skill':'Python','file':'a.py','quote':'x'}
    assert summarize([row,row], 'u')['issue_count']==1
