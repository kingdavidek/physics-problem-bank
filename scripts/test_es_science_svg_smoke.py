"""Stage 2 — science_shared SVG contract (wrapper, labels, colour-independent cues).

Run: python scripts/test_es_science_svg_smoke.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app  # noqa: E402
from generators.eursc.science_shared import (  # noqa: E402
    SCIENCE_SVG_FIGURES,
    accuracy_targets,
    distance_time_graph,
    science_arrow,
    science_axes,
    science_branch,
    science_cue,
    science_legend,
)
from models.svg_kit import svg  # noqa: E402

TEMPLATES = ROOT / 'templates'


def _svg_open_tag(markup: str) -> str:
    match = re.search(r'<svg\b[^>]*>', markup)
    assert match, f'no <svg> root in {markup[:200]!r}'
    return match.group(0)


def _assert_wrapper(markup: str, name: str):
    root = _svg_open_tag(markup)
    assert 'role="img"' in root, name
    assert 'viewBox="' in root, name
    assert re.search(r'\bwidth\s*=', root) is None, (name, root)
    assert re.search(r'\bheight\s*=', root) is None, (name, root)
    assert '<title' in markup, name
    assert '<desc' in markup, name
    assert 'aria-hidden="true"' in markup, name
    assert '<text' in markup, name


def test_every_science_figure_meets_contract():
    assert len(SCIENCE_SVG_FIGURES) >= 30
    names = [name for name, _fn in SCIENCE_SVG_FIGURES]
    assert len(names) == len(set(names))
    assert 'ruler_scale' in names
    assert 'accuracy_targets' in names
    assert 'menstrual_cycle_steps' in names
    assert 'solar_scale' in names
    assert 'signal_detect' in names
    assert 'water_cycle_steps' in names
    assert 'carbon_cycle_steps' in names
    for name, builder in SCIENCE_SVG_FIGURES:
        markup = str(builder())
        _assert_wrapper(markup, name)


def test_colour_independent_cues_on_accuracy_targets():
    markup = str(accuracy_targets())
    assert '<circle' in markup
    assert '<rect' in markup
    assert '<polygon' in markup
    assert markup.count('<line') >= 6
    for letter in 'ABCD':
        assert f'>{letter}</text>' in markup or f'>{letter}<' in markup
    assert 'accurate' in markup
    assert 'precise' in markup


def test_reusable_primitives():
    markup = str(
        svg(
            280,
            160,
            title='Primitive kit sample',
            desc='Axes with units, a legend, a branch, and mixed cue shapes.',
            body=lambda ids: (
                science_axes(
                    ids,
                    origin=(48, 120),
                    x_len=140,
                    y_len=80,
                    x_label='time',
                    y_label='distance',
                    x_unit='s',
                    y_unit='m',
                )
                + science_legend(
                    (('circle', 'on centre'), ('square', 'off centre')),
                    x=200,
                    y=40,
                )
                + science_branch(
                    ids,
                    fork=(200, 120),
                    left=(160, 148),
                    right=(240, 148),
                    prompt='wings?',
                )
                + science_cue('diamond', 70, 50, size=4)
                + science_cue('plus', 90, 50, size=4)
                + science_arrow(ids, 48, 40, 90, 40)
            ),
        )
    )
    _assert_wrapper(markup, 'primitives')
    assert 'time (s)' in markup
    assert 'distance (m)' in markup
    assert 'marker-end=' in markup
    assert 'on centre' in markup
    assert 'wings?' in markup
    assert '<polygon' in markup


def test_measurement_lesson_uses_shared_svgs():
    src = (TEMPLATES / 'eursc_science_measurement_lesson.html').read_text(encoding='utf-8')
    assert '{{ ruler_fig }}' in src
    assert '{{ accuracy_fig }}' in src
    assert 'meas-ruler-title' not in src
    assert 'meas-target-title' not in src
    assert src.count('class="mcq-inline"') == 7
    assert 'style="' not in src
    assert 'lesson-gloss' in src
    with app.test_client() as client:
        r = client.get('/topic/eursc/science/measurement')
        assert r.status_code == 200, r.data[:400]
        html = r.data.decode()
        assert html.count('class="svg-kit') >= 2
        assert '4.7' in html
        assert 'accurate' in html
        assert 'lesson-figure-caption' in html
        assert '1.50' in html


def test_s1_priority_lessons_use_captions_and_sequences():
    breathing_src = (TEMPLATES / 'eursc_science_breathing_lesson.html').read_text(
        encoding='utf-8'
    )
    anatomy_src = (TEMPLATES / 'eursc_science_reproductive_anatomy_lesson.html').read_text(
        encoding='utf-8'
    )
    assert '{{ circulation_fig }}' in breathing_src
    assert breathing_src.count('class="mcq-inline"') == 7
    assert 'style="' not in breathing_src
    assert 'lesson-figure-caption' in breathing_src
    assert 'lesson-gloss' in breathing_src
    assert '{{ organ_labels_fig }}' in anatomy_src
    assert '{{ cycle_fig }}' in anatomy_src
    assert anatomy_src.count('class="mcq-inline"') == 5
    assert 'style="' not in anatomy_src
    assert 'ovulation' in anatomy_src
    dt = str(distance_time_graph())
    assert 'time (s)' in dt
    assert 'distance (m)' in dt
    with app.test_client() as client:
        br = client.get('/topic/eursc/science/breathing')
        assert br.status_code == 200, br.data[:400]
        bhtml = br.data.decode()
        assert 'svg-kit' in bhtml
        assert 'heart' in bhtml
        assert 'marker-end=' in bhtml
        ar = client.get('/topic/eursc/science/reproductive_anatomy')
        assert ar.status_code == 200, ar.data[:400]
        ahtml = ar.data.decode()
        assert ahtml.count('class="svg-kit') >= 2
        assert 'ovulation' in ahtml
        assert 'egg path' in ahtml


def test_s2_priority_lessons_use_captions_and_scale():
    solar_src = (TEMPLATES / 'eursc_science_solar_system_lesson.html').read_text(
        encoding='utf-8'
    )
    light_src = (TEMPLATES / 'eursc_science_light_telescopes_lesson.html').read_text(
        encoding='utf-8'
    )
    infection_src = (TEMPLATES / 'eursc_science_infectious_disease_lesson.html').read_text(
        encoding='utf-8'
    )
    senses_src = (TEMPLATES / 'eursc_science_nonhuman_senses_lesson.html').read_text(
        encoding='utf-8'
    )
    assert '{{ solar_scale_fig }}' in solar_src
    assert solar_src.count('class="mcq-inline"') == 8
    assert 'astronomical unit' in solar_src
    assert '{{ reflection_fig }}' in light_src
    assert 'light-year' in light_src
    assert '{{ infection_chain_fig }}' in infection_src
    assert infection_src.count('class="mcq-inline"') == 8
    assert 'source, then route, then a new host' in infection_src
    assert '{{ signal_fig }}' in senses_src
    assert senses_src.count('class="mcq-inline"') == 6
    assert 'chemical' in senses_src
    assert 'style="' not in solar_src
    assert 'style="' not in senses_src
    with app.test_client() as client:
        sr = client.get('/topic/eursc/science/solar_system')
        assert sr.status_code == 200, sr.data[:400]
        shtml = sr.data.decode()
        assert shtml.count('class="svg-kit') >= 2
        assert '1 AU' in shtml
        ir = client.get('/topic/eursc/science/infectious_disease')
        assert ir.status_code == 200, ir.data[:400]
        ihtml = ir.data.decode()
        assert 'source' in ihtml
        assert 'marker-end=' in ihtml
        nr = client.get('/topic/eursc/science/nonhuman_senses')
        assert nr.status_code == 200, nr.data[:400]
        nhtml = nr.data.decode()
        assert 'svg-kit' in nhtml
        assert 'sensor' in nhtml


def test_s3_priority_lessons_use_captions_and_sankey():
    energy_src = (TEMPLATES / 'eursc_science_energy_lesson.html').read_text(
        encoding='utf-8'
    )
    current_src = (TEMPLATES / 'eursc_science_electric_current_lesson.html').read_text(
        encoding='utf-8'
    )
    magnet_src = (TEMPLATES / 'eursc_science_magnetism_lesson.html').read_text(
        encoding='utf-8'
    )
    eco_src = (TEMPLATES / 'eursc_science_ecosystems_cycles_lesson.html').read_text(
        encoding='utf-8'
    )
    key_src = (TEMPLATES / 'eursc_science_classification_biodiversity_lesson.html').read_text(
        encoding='utf-8'
    )
    force_src = (TEMPLATES / 'eursc_science_force_work_machines_lesson.html').read_text(
        encoding='utf-8'
    )
    assert '{{ sankey_fig }}' in energy_src
    assert energy_src.count('class="mcq-inline"') == 8
    assert 'lesson-figure-caption' in energy_src
    assert 'lesson-gloss' in energy_src
    assert '100 J' in energy_src
    assert 'style="' not in energy_src
    assert '{{ circuit_fig }}' in current_src
    assert current_src.count('class="mcq-inline"') == 8
    assert 'does not claim V = IR' in current_src
    assert '{{ magnet_fig }}' in magnet_src
    assert magnet_src.count('class="mcq-inline"') == 7
    assert 'north' in magnet_src.lower()
    assert '{{ water_cycle_fig }}' in eco_src
    assert '{{ carbon_cycle_fig }}' in eco_src
    assert '{{ trophic_fig }}' in eco_src
    assert eco_src.count('class="mcq-inline"') == 8
    assert 'carbon dioxide + water' in eco_src
    assert '{{ key_fig }}' in key_src
    assert key_src.count('class="mcq-inline"') == 8
    assert 'wings?' in key_src
    assert 'style="' not in current_src
    assert 'style="' not in eco_src
    assert '{{ force_vectors_fig }}' in force_src
    assert '{{ simple_machines_fig }}' in force_src
    assert '{{ lever_fig }}' in force_src
    assert '{{ ramp_fig }}' in force_src
    assert '{{ work_fd_fig }}' in force_src
    assert '{{ body_lever_fig }}' in force_src
    assert force_src.count('class="mcq-inline"') == 8
    assert force_src.count('class="lesson-section"') == 8
    assert force_src.count('class="lesson-figure"') >= 5
    assert 'style="' not in force_src
    with app.test_client() as client:
        er = client.get('/topic/eursc/science/energy')
        assert er.status_code == 200, er.data[:400]
        ehtml = er.data.decode()
        assert 'svg-kit' in ehtml
        assert '100 J' in ehtml
        assert 'marker-end=' in ehtml
        cr = client.get('/topic/eursc/science/electric_current')
        assert cr.status_code == 200, cr.data[:400]
        chtml = cr.data.decode()
        assert 'closed loop' in chtml
        assert 'marker-end=' in chtml
        mr = client.get('/topic/eursc/science/magnetism')
        assert mr.status_code == 200, mr.data[:400]
        mhtml = mr.data.decode()
        assert 'north' in mhtml.lower()
        assert '>N</text>' in mhtml or '>N<' in mhtml
        xr = client.get('/topic/eursc/science/ecosystems_cycles')
        assert xr.status_code == 200, xr.data[:400]
        xhtml = xr.data.decode()
        assert xhtml.count('class="svg-kit') >= 3
        assert 'evaporate' in xhtml
        assert 'photosynthesis' in xhtml
        kr = client.get('/topic/eursc/science/classification_biodiversity')
        assert kr.status_code == 200, kr.data[:400]
        khtml = kr.data.decode()
        assert 'wings?' in khtml
        assert 'marker-end=' in khtml
        fr = client.get('/topic/eursc/science/force_work_machines')
        assert fr.status_code == 200, fr.data[:400]
        fhtml = fr.data.decode()
        assert fhtml.count('class="svg-kit') >= 5
        assert 'Force as a vector: size and direction' in fhtml
        assert 'Lever: effort, fulcrum and load' in fhtml
        assert '15 J' in fhtml
        assert 'marker-end=' in fhtml


def main():
    test_every_science_figure_meets_contract()
    test_colour_independent_cues_on_accuracy_targets()
    test_reusable_primitives()
    test_measurement_lesson_uses_shared_svgs()
    test_s1_priority_lessons_use_captions_and_sequences()
    test_s2_priority_lessons_use_captions_and_scale()
    test_s3_priority_lessons_use_captions_and_sankey()
    print('Science SVG contract smoke tests passed.')


if __name__ == '__main__':
    main()
