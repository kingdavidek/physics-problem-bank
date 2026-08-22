"""U4.2a — topic registry syllabus order smoke test.

Run: python scripts/test_topic_registry_smoke.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, _annotate_topic_path_groups, _build_topic_groups, _topic_path_valid  # noqa: E402
from topic_registry import TOPICS, iter_topics, validate_topic_registry  # noqa: E402


def _maths_slugs():
    for group in _build_topic_groups():
        if group.get('subject') == 'maths' and group['title'].startswith('GCSE'):
            return [topic['slug'] for topic in group['topics']]
    raise AssertionError('GCSE Maths group not found')


def main():
    validate_topic_registry()

    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            slugs = [slug for slug, _cfg in iter_topics(topics)]
            assert slugs == sorted(slugs, key=lambda slug: topics[slug]['order'])

    maths = _maths_slugs()
    assert maths[0] == 'bidmas'
    assert maths.index('algebra') < maths.index('simultaneous_equations')
    assert maths.index('graphs') < maths.index('graphical_simultaneous_equations')
    assert maths.index('pythagoras') < maths.index('trigonometry')

    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for slug in topics:
                assert _topic_path_valid(level, subject, slug)

    with app.test_client() as client:
        for slug in ('bidmas', 'algebra', 'pythagoras'):
            r = client.get(f'/topic/gcse/maths/{slug}')
            assert r.status_code == 200, slug

        r = client.get('/topics')
        assert r.status_code == 200
        body = r.data.decode()
        bidmas_pos = body.index('/topic/gcse/maths/bidmas')
        algebra_pos = body.index('/topic/gcse/maths/algebra')
        assert bidmas_pos < algebra_pos
        assert 'topic-path-node' in body
        assert 'is-current' in body
        assert 'Start here' in body
        assert 'After Decimals' in body
        assert 'of ' in body and ' mastered' in body
        assert 'href="/topic/gcse/maths/fdp"' in body

        groups = _build_topic_groups()
        _annotate_topic_path_groups(groups, {})
        maths = next(
            group for group in groups
            if group['level'] == 'gcse' and group['subject'] == 'maths'
        )
        assert maths['topics'][0]['slug'] == 'bidmas'
        assert maths['topics'][0]['is_current']
        assert maths['completed_count'] == 0
        fdp = next(topic for topic in maths['topics'] if topic['slug'] == 'fdp')
        assert fdp['prereq_hint'] == 'Decimals'
        assert fdp['is_later']
        assert fdp['url'] == '/topic/gcse/maths/fdp'

        _annotate_topic_path_groups(groups, {('gcse', 'maths', 'bidmas'): 1.0})
        assert maths['topics'][0]['is_complete']
        assert maths['topics'][1]['is_current']
        assert maths['completed_count'] == 1

        r = client.get('/api/v1/topics')
        assert r.status_code == 200
        catalog = r.get_json()
        gcse_maths = next(
            sub['topics']
            for level in catalog['levels']
            if level['id'] == 'gcse'
            for sub in level['subjects']
            if sub['id'] == 'maths'
        )
        assert gcse_maths[0]['slug'] == 'bidmas'

        r = client.get('/')
        assert r.status_code == 200
        home = r.data.decode()
        bidmas_opt = home.index('value="bidmas"')
        algebra_opt = home.index('value="algebra"')
        vectors_opt = home.index('value="vectors"')
        assert bidmas_opt < algebra_opt < vectors_opt

    print('U4.2 topic registry + path UI smoke tests passed.')


if __name__ == '__main__':
    main()
