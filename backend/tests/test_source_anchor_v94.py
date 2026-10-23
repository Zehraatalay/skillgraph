from app.ai.validate_behaviors import review_report


def _item(line, quote, function="find_valid_moves"):
    return {"concept": "Conditional candidate enumeration", "repository": "user/repo",
            "file": "moves.py", "function": function, "line": line, "quote": quote}


def test_shifted_line_validated_inside_named_function(tmp_path):
    source = """# added header
# shifted line

def find_valid_moves(xs):
    valid_moves = []
    for x in xs:
        if is_valid_swap(x):
            valid_moves.append(x)
    return valid_moves
"""
    (tmp_path / "moves.py").write_text(source)
    result = review_report({"repository": "user/repo", "items": [
        _item(2, "valid_moves.append(x)")]}, tmp_path)
    assert result["counts"] == {"verified": 1}


def test_quote_in_other_function_cannot_verify(tmp_path):
    source = """def find_valid_moves(xs):
    for x in xs:
        if x:
            pass

def unrelated(xs):
    for x in xs:
        if x:
            valid_moves.append(x)
"""
    (tmp_path / "moves.py").write_text(source)
    result = review_report({"repository": "user/repo", "items": [
        _item(6, "valid_moves.append(x)")]}, tmp_path)
    assert result["counts"] == {"review_required": 1}


def test_duplicate_function_names_with_same_quote_not_verified(tmp_path):
    source = """def find_valid_moves(xs):
    for x in xs:
        if x:
            valid_moves.append(x)

def find_valid_moves(xs):
    for x in xs:
        if x:
            valid_moves.append(x)
"""
    (tmp_path / "moves.py").write_text(source)
    result = review_report({"repository": "user/repo", "items": [
        _item(3, "valid_moves.append(x)")]}, tmp_path)
    assert result["counts"] == {"review_required": 1}
