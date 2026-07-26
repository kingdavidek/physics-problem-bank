"""GCSE SQL query comparison — structural token match (not keyword-only)."""
import re

_SQL_TOKEN_RE = re.compile(
    r"'(?:[^']|'')*'"
    r'|>=|<=|<>|!='
    r'|[=(),*]'
    r'|\w+(?:\.\w+)*',
    re.IGNORECASE,
)

_SQL_STATEMENTS = frozenset({'select', 'insert', 'update', 'delete'})


def normalize_sql_query(sql: str) -> str:
    return ' '.join(str(sql or '').split()).strip().rstrip(';').strip()


def _normalize_string_literal(token: str) -> str:
    inner = token[1:-1].replace("''", "'")
    return f"'{inner.lower()}'"


def _normalize_word_token(token: str) -> str:
    return token.lower()


def tokenize_sql(sql: str) -> list[str]:
    s = normalize_sql_query(sql)
    if not s:
        return []
    tokens = []
    for match in _SQL_TOKEN_RE.finditer(s):
        token = match.group(0)
        if token.startswith("'"):
            tokens.append(_normalize_string_literal(token))
        elif token.isalnum() or '.' in token or token.isidentifier():
            tokens.append(_normalize_word_token(token))
        else:
            tokens.append(token)
    return tokens


def _identifier_tokens_match(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    if '.' in expected and actual == expected.split('.')[-1]:
        return True
    if '.' in actual and expected == actual.split('.')[-1]:
        return True
    return False


def _sql_token_equal(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    if expected.startswith("'") and actual.startswith("'"):
        return expected == actual
    if re.fullmatch(r'[\w.]+', expected) and re.fullmatch(r'[\w.]+', actual):
        return _identifier_tokens_match(expected, actual)
    return False


def _expand_order_by(tokens: list[str]) -> list[str]:
    """Treat ``ORDER Score`` as ``ORDER BY Score`` for lenient GCSE marking."""
    out: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        out.append(tok)
        if tok == 'order' and i + 1 < len(tokens) and tokens[i + 1] != 'by':
            out.append('by')
        i += 1
    return out


def _strip_limit_clause(tokens: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if tokens[i] == 'limit' and i + 1 < len(tokens):
            i += 2
            continue
        out.append(tokens[i])
        i += 1
    return out


def _lcs_sql_length(expected: list[str], actual: list[str]) -> int:
    m, n = len(expected), len(actual)
    if not m or not n:
        return 0
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        exp_tok = expected[i - 1]
        for j in range(1, n + 1):
            if _sql_token_equal(exp_tok, actual[j - 1]):
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[n]


def sql_tokens_match(expected: list[str], actual: list[str]) -> bool:
    if len(expected) != len(actual):
        return False
    return all(_sql_token_equal(e, a) for e, a in zip(expected, actual))


def compare_sql_queries(correct: str, user: str) -> bool:
    if not str(user or '').strip():
        return False
    expected = tokenize_sql(correct)
    actual = _expand_order_by(tokenize_sql(user))
    if sql_tokens_match(expected, actual):
        return True
    if sql_tokens_match(_strip_limit_clause(expected), actual):
        return True
    if sql_tokens_match(expected, _strip_limit_clause(actual)):
        return True
    return False


def score_sql_queries(correct: str, user: str) -> dict:
    """Score SQL by ordered token overlap; award partial credit when mostly correct."""
    expected = tokenize_sql(correct)
    total = len(expected)
    if not total:
        return {'score': 0, 'score_total': 0, 'ratio': 0.0}

    user_s = str(user or '').strip()
    if not user_s:
        return {'score': 0, 'score_total': total, 'ratio': 0.0}

    actual = _expand_order_by(tokenize_sql(user_s))
    if compare_sql_queries(correct, user_s):
        return {'score': total, 'score_total': total, 'ratio': 1.0}

    if expected[0] in _SQL_STATEMENTS:
        if not actual or not _sql_token_equal(expected[0], actual[0]):
            return {'score': 0, 'score_total': total, 'ratio': 0.0}

    matched = _lcs_sql_length(expected, actual)
    ratio = matched / total if total else 0.0
    return {'score': matched, 'score_total': total, 'ratio': ratio}


def sql_partial_credit_threshold(score: int, total: int) -> bool:
    if total <= 0 or score <= 0 or score >= total:
        return False
    if score >= total - 1:
        return True
    if total <= 4:
        return score >= 2
    return (score / total) >= 0.5
