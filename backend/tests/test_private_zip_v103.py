import io
import zipfile
import pytest
from app.ai.private_zip_v103 import analyze_zip


def make_zip(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in entries.items():
            z.writestr(name, content)
    return stream.getvalue()


def test_numpy_detection():
    blob = make_zip({'src/main.py': 'import numpy as np\nx = np.array([1,2])\n'})
    result = analyze_zip(blob)
    assert result['visibility'] == 'private'
    assert 'NumPy' in {s['name'] for s in result['skills']}
    assert result['neo4j_writes'] is False


def test_python_detection():
    result = analyze_zip(make_zip({'main.py': 'def hello():\n    return 1\n'}))
    assert 'Python' in {s['name'] for s in result['skills']}

@pytest.mark.parametrize('name', ['../evil.py','/tmp/evil.py','folder/../../evil.py','C:/foo.py'])
def test_path_traversal(name):
    with pytest.raises(ValueError, match='Unsafe ZIP path'):
        analyze_zip(make_zip({name: 'hello'}))


def test_reject_symlink():
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        info=zipfile.ZipInfo('link.py')
        info.create_system=3
        info.external_attr=(0o120777 << 16)
        z.writestr(info,'target.py')
    with pytest.raises(ValueError, match='Unsupported ZIP entry'):
        analyze_zip(stream.getvalue())


def test_reject_bad_archive():
    with pytest.raises(ValueError, match='Invalid ZIP'):
        analyze_zip(b'not zip')


def test_reject_wrong_extension():
    with pytest.raises(ValueError, match='filename'):
        analyze_zip(make_zip({'a.py':'x=1'}),filename='source.tar')


def test_reject_excessive_compression():
    with pytest.raises(ValueError, match='compression ratio'):
        analyze_zip(make_zip({'a.py': 'x' * 10000}))


def test_same_archive_stable_id():
    blob=make_zip({'a.py':'x=1'})
    assert analyze_zip(blob)['project_id'] == analyze_zip(blob)['project_id']
