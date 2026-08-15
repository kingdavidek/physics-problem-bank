"""SQLite FTS5 index of lesson titles, summaries, formulae, and tips."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3

from topic_registry import TOPICS
from topics_data import TOPIC_CONTENT, extract_lesson_search_text

_LEVEL_LABELS = {
    'gcse': 'GCSE',
    'alevel': 'A-Level',
    'myp': 'MYP',
}
_SUBJECT_LABELS = {
    'maths': 'Maths',
    'physics': 'Physics',
    'cs': 'Computer Science',
    'chemistry': 'Chemistry',
}
_TOKEN_RE = re.compile(r'[a-z0-9]{2,}', re.I)


def _group_label(level, subject):
    return (
        f"{_LEVEL_LABELS.get(level, str(level).title())} "
        f"{_SUBJECT_LABELS.get(subject, str(subject).title())}"
    )


def build_lesson_search_docs():
    docs = []
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for slug, cfg in topics.items():
                content = TOPIC_CONTENT.get((level, subject, slug), {})
                name = cfg.get('name', slug.replace('_', ' ').title())
                body = ' '.join([
                    name,
                    slug.replace('_', ' '),
                    extract_lesson_search_text(content),
                ]).strip()
                docs.append({
                    'path': f'{level}/{subject}/{slug}',
                    'level': level,
                    'subject': subject,
                    'topic': slug,
                    'name': name,
                    'group': _group_label(level, subject),
                    'url': f'/topic/{level}/{subject}/{slug}',
                    'body': body,
                })
    docs.sort(key=lambda item: item['path'])
    return docs


def corpus_hash(docs=None):
    docs = docs if docs is not None else build_lesson_search_docs()
    payload = [(item['path'], item['body']) for item in docs]
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def fts_query_from_user(query):
    tokens = _TOKEN_RE.findall((query or '').lower())[:8]
    if not tokens:
        return ''
    return ' AND '.join(f'{token}*' for token in tokens)


def _fts5_ready(conn):
    for tokenize in ('porter unicode61', 'porter', 'unicode61'):
        try:
            conn.execute(
                f'''
                CREATE VIRTUAL TABLE IF NOT EXISTS lesson_search_fts USING fts5(
                    path UNINDEXED,
                    name,
                    group_label,
                    body,
                    tokenize = "{tokenize}"
                )
                '''
            )
            return True
        except sqlite3.OperationalError:
            continue
    return False


def ensure_lesson_search_index(conn):
    docs = build_lesson_search_docs()
    digest = corpus_hash(docs)
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS lesson_search_meta (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            source_hash TEXT NOT NULL
        )
        '''
    )
    row = conn.execute(
        'SELECT source_hash FROM lesson_search_meta WHERE id = 1'
    ).fetchone()
    fts_ok = _fts5_ready(conn)
    if row and row['source_hash'] == digest:
        return fts_ok

    if fts_ok:
        conn.execute('DELETE FROM lesson_search_fts')
        conn.executemany(
            '''
            INSERT INTO lesson_search_fts (path, name, group_label, body)
            VALUES (?, ?, ?, ?)
            ''',
            [(d['path'], d['name'], d['group'], d['body']) for d in docs],
        )
    conn.execute(
        '''
        INSERT INTO lesson_search_meta (id, source_hash)
        VALUES (1, ?)
        ON CONFLICT(id) DO UPDATE SET source_hash = excluded.source_hash
        ''',
        (digest,),
    )
    conn.commit()
    return fts_ok


def search_lesson_keywords(conn, query, limit=8):
    """Return topic dicts matching lesson body keywords (FTS5 or substring fallback)."""
    query = (query or '').strip()
    tokens = _TOKEN_RE.findall(query.lower())
    if not tokens or limit <= 0:
        return []

    ensure_lesson_search_index(conn)
    fts = fts_query_from_user(query)
    if fts:
        try:
            rows = conn.execute(
                '''
                SELECT path, name, group_label
                FROM lesson_search_fts
                WHERE lesson_search_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                ''',
                (fts, int(limit)),
            ).fetchall()
            out = []
            for row in rows:
                path = row['path']
                parts = path.split('/')
                if len(parts) != 3:
                    continue
                level, subject, topic = parts
                out.append({
                    'name': row['name'],
                    'slug': topic,
                    'url': f'/topic/{level}/{subject}/{topic}',
                    'group': row['group_label'],
                    'via': 'keywords',
                })
            if out:
                return out
        except sqlite3.OperationalError:
            pass

    matches = []
    for doc in build_lesson_search_docs():
        hay = doc['body'].lower()
        if all(token in hay for token in tokens):
            matches.append({
                'name': doc['name'],
                'slug': doc['topic'],
                'url': doc['url'],
                'group': doc['group'],
                'via': 'keywords',
            })
            if len(matches) >= limit:
                break
    return matches
