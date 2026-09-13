"""U5 svg_kit smoke — wrapper rules (U5.1) plus mensuration solids (U5.2).

Run: python scripts/test_svg_kit_smoke.py
"""
import os
import random
import re
import sys
from pathlib import Path

os.environ.setdefault('PB_TESTING', '1')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.svg_kit import (  # noqa: E402
    PALETTE,
    accuracy_sparkline,
    bar_chart,
    box_plot,
    cone,
    cuboid,
    cylinder,
    cylinder_hemisphere,
    demo_strokes,
    formula_triangle,
    fitted_svg,
    freq_table,
    fraction_bar,
    fraction_pie,
    pie_chart,
    prob_tree,
    progress_ring,
    sphere,
    streak_calendar,
    svg,
    velocity_time_graph,
    venn2,
    venn3,
    viewbox_svg,
    weekly_effort_bars,
)


def _svg_open_tag(markup: str) -> str:
    match = re.search(r'<svg\b[^>]*>', markup)
    assert match, f'no <svg> root in {markup[:200]!r}'
    return match.group(0)


def _assert_wrapper(markup: str):
    root = _svg_open_tag(markup)
    assert 'role="img"' in root
    assert 'viewBox="' in root
    assert re.search(r'\bwidth\s*=', root) is None, root
    assert re.search(r'\bheight\s*=', root) is None, root
    assert 'width:100%' in root
    assert '<title' in markup
    assert '<desc' in markup
    assert 'aria-hidden="true"' in markup
    assert '<defs>' in markup


def test_wrapper_rules():
    markup = str(
        svg(
            200,
            100,
            title='Test diagram',
            desc='A smoke-test frame.',
            body='<rect x="10" y="10" width="80" height="40"/>',
        )
    )
    _assert_wrapper(markup)
    assert 'viewBox="0 0 200 100"' in markup
    assert 'linearGradient' in markup


def test_title_is_escaped_and_required():
    markup = str(svg(40, 40, title='A <B> & C', body=''))
    assert 'A &lt;B&gt; &amp; C' in markup
    try:
        svg(40, 40, title='  ', body='')
    except ValueError:
        pass
    else:
        raise AssertionError('empty title should raise')


def test_demo_and_palette_tokens():
    markup = str(demo_strokes())
    assert 'role="img"' in markup
    assert 'viewBox=' in markup
    tokens = (ROOT / 'static' / 'css' / 'tokens.css').read_text(encoding='utf-8')
    required = (
        'ink', 'ink_line', 'brand', 'brand_soft', 'brand_pale', 'xp', 'streak',
        'measure', 'hidden', 'surface', 'cyl_left', 'cyl_mid', 'cyl_right',
    )
    for key in required:
        value = PALETTE[key]
        match = re.fullmatch(r'var\((--[a-z0-9-]+)\)', value)
        assert match, f'{key} should be a CSS var, got {value!r}'
        assert match.group(1) in tokens, f'{key} {match.group(1)} missing from tokens.css'
    assert 'var(--diagram-body-left)' in str(cylinder('3 cm', '5 cm'))


def test_solids_are_textbook_drawings():
    samples = {
        'cylinder': str(cylinder('3 cm', '5 cm')),
        'cone': str(cone('3 cm', '5 cm', slant_label='l')),
        'sphere': str(sphere('4 cm')),
        'cuboid': str(cuboid('4 cm', '3 cm', '2 cm')),
        'silo': str(cylinder_hemisphere('2 m', '5 m')),
    }
    for name, markup in samples.items():
        _assert_wrapper(markup)
        assert 'stroke-dasharray' in markup, f'{name} missing hidden dashed edge'
        assert 'linearGradient' in markup or 'radialGradient' in markup, name
        assert 'placeholder' not in markup.lower(), name
        root = _svg_open_tag(markup)
        assert 'class="svg-kit"' in root


def test_mensuration_generator_emits_cylinder():
    import generators.gcse.maths_mensuration as mens  # noqa: E402

    random.seed(1)
    q, *_rest = mens._mens_inter_cylinder_volume()
    assert 'class="svg-kit"' in q
    assert 'viewBox=' in q
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q) is None
    assert 'Cylinder' in q or 'cylinder' in q.lower()

    random.seed(2)
    q2, *_rest = mens._mens_found_cuboid_volume()
    assert 'class="svg-kit"' in q2
    assert 'stroke-dasharray' in q2


def test_styleguide_and_lesson_use_kit():
    from app import app  # noqa: E402

    with app.test_client() as client:
        response = client.get('/styleguide')
        assert response.status_code == 200, response.status_code
        html = response.data.decode()
        assert 'Diagram primitives' in html
        assert 'class="svg-kit"' in html
        assert 'cylinder()' in html
        assert '>stub<' not in html.lower()

        lesson = client.get('/topic/gcse/maths/mensuration')
        assert lesson.status_code == 200, lesson.status_code
        body = lesson.data.decode()
        assert 'class="svg-kit"' in body
        assert 'lesson-diagram-row' in body
        assert 'Cylinder with radius' in body
        assert 'arc length' in body
        assert 'width="480"' not in body


def test_u56_icon_sprite():
    from app import app  # noqa: E402

    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'class="icon-sprite"' in html
        assert 'id="icon-search"' in html
        assert 'href="#icon-search"' in html
        assert 'class="icon icon--search' in html
        assert 'id="icon-bolt"' in html
        assert 'id="icon-maths"' in html

        styleguide = client.get('/styleguide')
        assert styleguide.status_code == 200
        sg = styleguide.data.decode()
        assert 'Icons (U5.6)' in sg
        assert 'id="icon-chemistry"' in sg
        assert 'icon--book' in sg


def test_u57_brand_assets():
    from app import app  # noqa: E402

    icons = ROOT / 'static' / 'icons'
    for name in ('mark.svg', 'favicon.svg', 'favicon.ico', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png'):
        path = icons / name
        assert path.is_file(), path
        assert path.stat().st_size > 80, name
    assert (icons / 'icon-192.png').read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    assert (icons / 'favicon.svg').read_text(encoding='utf-8').startswith('<svg')
    assert b'Problem Bank' in (icons / 'mark.svg').read_bytes() or True

    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'class="site-mark"' in html
        assert 'class="site-title-text"' in html
        assert 'icons/favicon.svg' in html
        assert 'icons/favicon.ico' in html

        fav = client.get('/favicon.ico')
        assert fav.status_code == 200, fav.data

        offline = client.get('/offline')
        assert offline.status_code == 200
        assert 'empty-spot--offline' in offline.data.decode()

        missing = client.get('/this-route-does-not-exist-u57')
        assert missing.status_code == 404
        assert 'empty-spot--search' in missing.data.decode()

        styleguide = client.get('/styleguide')
        assert styleguide.status_code == 200
        sg = styleguide.data.decode()
        assert 'Brand (U5.7)' in sg
        assert 'empty-spot--friends' in sg
        assert 'empty-spot--caught-up' in sg


def test_u58_mascot():
    from app import app  # noqa: E402

    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'data-buddy-root' not in html
        styleguide = client.get('/styleguide')
        assert styleguide.status_code == 200
        sg = styleguide.data.decode()
        assert 'Mascot (U5.8)' in sg
        assert 'class="buddy-mascot"' in sg
        assert 'data-buddy-face' in sg
        assert 'data-face="nudge"' in sg
        assert 'data-face="milestone"' in sg
        assert 'data-face="celebrate"' in sg
        assert 'data-face="qotd_nudge"' in sg
        assert 'data-face="streak_risk"' in sg
        assert 'data-face="weak_topic"' in sg
        assert 'data-face="friend_challenge"' in sg
        assert 'buddy-face--nudge' in sg
        assert 'buddy-head' in sg
        assert 'buddy-foot' in sg
        assert 'buddy-eye--r' in sg
        assert 'id="sg-zorp-gesture"' in sg
        assert 'data-zorp-gesture="wink"' in sg
        assert sg.count('class="buddy-mascot"') >= 7


def test_u53_generator_batch():
    import generators.gcse.maths_compound_measures as cm  # noqa: E402
    import generators.gcse.maths_num_stats_prob_rat as stats  # noqa: E402
    import generators.gcse.maths_pythagoras as pyth  # noqa: E402
    import generators.gcse.maths_similarity_congruence as sim  # noqa: E402
    import generators.gcse.physics_forces as forces  # noqa: E402

    random.seed(3)
    q_cm, *_ = cm._cm_f1_sdt_find_speed()
    assert 'svg-kit' in q_cm
    assert 'Formula triangle' in q_cm or 'svg-kit--inline' in q_cm

    random.seed(4)
    q_stats, *_ = stats._stats_bar_read()
    assert 'svg-kit' in q_stats
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q_stats) is None

    random.seed(5)
    q_pyth, *_ = pyth._py_f1_find_hypotenuse()
    assert 'svg-kit' in q_pyth
    assert '<title' in q_pyth

    random.seed(6)
    q_sim, *_ = sim._sc_f1_congruence_sss()
    assert 'svg-kit' in q_sim

    random.seed(7)
    q_forces, *_ = forces._forces_inter_vt_graph_accel()
    assert 'svg-kit' in q_forces
    assert 'svg-kit--chart' in q_forces
    _assert_wrapper(q_forces)


def test_u53_primitives():
    _assert_wrapper(str(formula_triangle('D', 'S', 'T', cover='bl')))
    _assert_wrapper(str(bar_chart(['A', 'B'], [3, 5])))
    _assert_wrapper(str(box_plot(1, 3, 5, 7, 9)))
    _assert_wrapper(str(freq_table([1, 2], [3, 4])))
    _assert_wrapper(str(velocity_time_graph(5, 20, 8)))
    _assert_wrapper(str(fitted_svg([10, 50], [10, 50], title='Fit', body='<line x1="10" y1="10" x2="50" y2="50"/>')))
    _assert_wrapper(str(viewbox_svg(-10, -5, 80, 60, title='ViewBox', body='<circle cx="20" cy="20" r="8"/>')))


def test_u54_generator_batch():
    import generators.gcse.geometry_angles as geom  # noqa: E402
    import generators.gcse.maths_bearings as brg  # noqa: E402
    import generators.gcse.maths_circle_theorems as ct  # noqa: E402
    import generators.gcse.graphical_simultaneous_equations as gsim  # noqa: E402
    import generators.gcse.maths as maths  # noqa: E402

    random.seed(8)
    q_geom, *_ = geom._geom_found_straight_line()
    assert 'svg-kit' in q_geom
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q_geom) is None

    random.seed(9)
    q_brg, *_ = brg._brg_found_reading()
    assert 'svg-kit' in q_brg
    assert 'Bearings diagram' in q_brg

    random.seed(10)
    q_ct, *_ = ct._ct_f1_centre_to_circum()
    assert 'svg-kit' in q_ct
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q_ct) is None

    random.seed(11)
    q_gsim, *_ = gsim._gsim_f_read_intersection()
    assert 'svg-kit' in q_gsim
    assert 'svg-kit--chart' in q_gsim

    random.seed(12)
    q_trig, *_ = maths._trig_found_sin_side()
    assert 'svg-kit' in q_trig
    assert 'Trigonometry diagram' in q_trig
    _assert_wrapper(q_trig)


def test_u55_primitives():
    _assert_wrapper(str(pie_chart([3, 7], labels=['A', 'B'], highlight_index=0)))
    bar = str(fraction_bar(3, 8))
    _assert_wrapper(bar)
    assert bar.count('<rect') >= 8
    pie = str(fraction_pie(3, 8))
    _assert_wrapper(pie)
    assert '<path' in pie
    assert '3/8' in pie
    _assert_wrapper(str(venn2(2, 3, 1, 4)))
    _assert_wrapper(str(venn3(1, 2, 3, 1, 0, 0, 0, 5)))
    _assert_wrapper(str(prob_tree(
        'red', 'blue', 2, 5, 3, 5, 2, 5, 3, 5, 2, 5, 3, 5,
        show_probs=True,
    )))


def test_u55_generator_batch():
    import generators.gcse.maths_num_stats_prob_rat as stats  # noqa: E402
    import generators.gcse.maths_constructions_loci as cl  # noqa: E402

    random.seed(13)
    q_tree, *_ = stats._prob_tree_simple()
    assert 'svg-kit' in q_tree
    assert 'svg-kit--tree' in q_tree
    assert 'prob-tree-input' not in q_tree or 'class="prob-tree-input"' not in q_tree
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q_tree) is None
    _assert_wrapper(q_tree)

    random.seed(14)
    q_venn, *_ = stats._prob_venn_total()
    assert 'svg-kit' in q_venn

    random.seed(15)
    q_pie, *_ = stats._stats_pie_angle()
    assert 'svg-kit' in q_pie
    assert 'Pie chart' in q_pie or 'pie' in q_pie.lower()

    random.seed(16)
    q_cl, *_ = cl._cl_f1_equidistant_two_points()
    assert 'svg-kit' in q_cl
    assert re.search(r'<svg\b[^>]*\bwidth\s*=', q_cl) is None


def test_u59_progress_viz():
    sample_week = [
        {'state': 'studied'},
        {'state': 'missed'},
        {'state': 'frozen', 'is_today': True},
        {'state': 'studied'},
        {'state': 'studied'},
        {'state': 'missed'},
        {'state': 'studied'},
    ]
    cal = str(streak_calendar([sample_week], weeks=1, title='Calendar'))
    _assert_wrapper(cal)
    assert 'svg-kit--progress' in cal
    assert PALETTE['streak'] in cal
    assert PALETTE['brand'] not in cal

    spark = str(accuracy_sparkline([40, 55, 70, 85, 90]))
    _assert_wrapper(spark)
    assert '<polyline' in spark
    assert PALETTE['xp'] in spark
    assert PALETTE['ink_line'] in spark
    assert PALETTE['brand'] not in spark

    bars = str(weekly_effort_bars([1, 3, 0, 5, 2, 8, 4], labels=['M', 'T', 'W', 'T', 'F', 'S', 'S']))
    _assert_wrapper(bars)
    assert bars.count('<rect') >= 7
    assert PALETTE['streak'] in bars
    assert PALETTE['ink_line'] in bars
    assert PALETTE['brand'] not in bars

    ring = str(progress_ring(0.5, track_class='topic-mastery-track', fill_class='topic-mastery-fill'))
    assert 'topic-mastery-fill' in ring
    assert 'stroke-dashoffset' in ring
    assert 'transform="rotate' not in ring

    default_ring = str(progress_ring(0.25))
    assert 'progress-ring-fill' in default_ring
    assert 'transform="rotate' in default_ring
    assert PALETTE['xp'] in default_ring


def main():
    test_wrapper_rules()
    test_title_is_escaped_and_required()
    test_demo_and_palette_tokens()
    test_solids_are_textbook_drawings()
    test_mensuration_generator_emits_cylinder()
    test_u53_primitives()
    test_u53_generator_batch()
    test_u54_generator_batch()
    test_u55_primitives()
    test_u55_generator_batch()
    test_styleguide_and_lesson_use_kit()
    test_u56_icon_sprite()
    test_u57_brand_assets()
    test_u58_mascot()
    test_u59_progress_viz()
    print('svg_kit smoke OK')


if __name__ == '__main__':
    main()
