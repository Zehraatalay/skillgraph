import ast
from app.ai.finalize_v9 import _structural_check


def fn(src):
    return ast.parse(src).body[0]


def test_move_enumeration_requires_swap_validation():
    good = fn('def find_valid_moves(xs):\n for x in xs:\n  if is_valid_swap(x):\n   result.append(x)\n')
    assert _structural_check('Legal Move Enumeration', good)
    bad = fn('def find_valid_moves(xs):\n for x in xs:\n  if x:\n   result.append(x)\n')
    assert not _structural_check('Legal Move Enumeration', bad)


def test_mutation_not_cache_or_state_transformation():
    f = fn('def f(board):\n if board[0]:\n  board[0] = 1\n return board\n')
    assert not _structural_check('Game State Transformation', f)


def test_copied_updated_returned_state():
    f = fn('def f(board):\n result = board.copy()\n result[0] = 0\n return result\n')
    assert _structural_check('Game State Transformation', f)


def test_assertions():
    assert _structural_check('Automated Testing', fn('def test_x():\n assert 1 == 1\n'))
    assert not _structural_check('Automated Testing', fn('def test_x():\n pass\n'))
