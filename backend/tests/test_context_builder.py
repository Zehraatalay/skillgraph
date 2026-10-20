import unittest
from app.ai.schemas import RepositoryContext, SourceFile
from app.ai.context_builder import build_context


class ContextTests(unittest.TestCase):
    def test_contains_provenance(self):
        ctx = RepositoryContext(owner='a', repository='b', files=[SourceFile(path='main.py', content='import numpy', size=12)])
        rendered = build_context(ctx)
        self.assertIn('main.py', rendered)
        self.assertIn('untrusted data', rendered)
