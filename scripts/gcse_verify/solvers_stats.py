"""Solvers for statistics, including answers read from the chart the pupil is shown.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library, sympy and the sibling verification modules.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction

from .core import Cannot, Pick, norm_text, parse_num
from .registry import diagram, fr, solver
from .solvers_svg import (PX, one_svg, pearson, read_bar_chart, read_box_plot, read_cf_curve, read_freq_table,
                          read_histogram, read_pie_sectors, read_scatter_points, x_axis_from_labels,
                          y_axis_from_labels)


def _mean(values):
    values = [fr(v) for v in values]
    return sum(values) / len(values)


# ─────────────────────────────────────────────────────────────────────────────
# Lists and tables
# ─────────────────────────────────────────────────────────────────────────────

@solver('stats_list')
def _stats_list(stat_word, values):
    vals = sorted(fr(v) for v in values)
    stat = str(stat_word)
    if stat == 'range':
        return [vals[-1] - vals[0]]
    if stat == 'mean':
        return [sum(vals) / len(vals)]
    if stat == 'median':
        mid = len(vals) // 2
        return [vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2]
    if stat == 'mode':
        ranked = Counter(vals).most_common()
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            raise Cannot('the data have more than one mode')
        return [ranked[0][0]]
    raise Cannot(f'unknown statistic {stat_word!r}')


@solver('stats_midpoint')
def _stats_midpoint(low, high):
    if fr(high) <= fr(low):
        raise Cannot('the class is empty')
    return [(fr(low) + fr(high)) / 2]


@solver('stats_freq_mean')
def _stats_freq_mean(values, freqs):
    if len(values) != len(freqs):
        raise Cannot('values and frequencies differ in length')
    return [sum(fr(v) * fr(f) for v, f in zip(values, freqs)) / sum(fr(f) for f in freqs)]


@diagram('stats_freq_mean')
def _check_freq_table(inputs, html):
    rows = read_freq_table(one_svg(html))
    want = [(fr(v), fr(f)) for v, f in zip(inputs['values'], inputs['freqs'])]
    got = [(x, f) for x, f, _ in rows]
    return [] if got == want else [f'the table shows {got} but the question was built with {want}']


@solver('stats_bar')
def _stats_bar(a, b, c):
    return [fr(a) + fr(b) + fr(c)]


@diagram('stats_bar')
def _check_bar(inputs, html):
    bars = read_bar_chart(one_svg(html))
    want = [fr(inputs[k]) for k in ('a', 'b', 'c')]
    out = []
    if len(bars) != 3:
        return [f'the chart has {len(bars)} bars, not 3']
    for (cat, height, printed), w in zip(bars, want):
        if abs(height - float(w)) > 0.3:
            out.append(f'bar {cat} is drawn {height:.2f} high on the scale but should be {w}')
        if printed != w:
            out.append(f'bar {cat} is labelled {printed} but should be {w}')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Pie chart
# ─────────────────────────────────────────────────────────────────────────────

@solver('stats_pie')
def _stats_pie(freq, total):
    if fr(freq) >= fr(total):
        raise Cannot('the category is the whole total')
    return [360 * fr(freq) / fr(total)]


@diagram('stats_pie')
def _check_pie(inputs, html):
    sectors = read_pie_sectors(one_svg(html))
    want = float(360 * fr(inputs['freq']) / fr(inputs['total']))
    out = []
    if abs(sectors[0] - want) > 1.5:
        out.append(f'the first sector is drawn {sectors[0]:.1f} degrees but should be {want:.1f}')
    if abs(sum(sectors) - 360) > 1.5:
        out.append(f'the sectors add to {sum(sectors):.1f} degrees')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Histograms
# ─────────────────────────────────────────────────────────────────────────────

def _histogram_classes(svg):
    """[(low, high, frequency)] from the drawn bars: whole-number boundaries, whole-number densities."""
    classes = []
    for low, high, density in read_histogram(svg):
        lo, hi = round(low), round(high)
        if abs(low - lo) > 0.3 or abs(high - hi) > 0.3:
            raise Cannot('histogram class boundaries are not whole numbers on the axis')
        if abs(density - round(density)) > 0.12:
            raise Cannot(f'a histogram bar of height {density:.2f} cannot be read from the frequency density scale')
        classes.append((lo, hi, Fraction(round(density)) * (hi - lo)))
    return classes


def _grouped_mean(classes):
    total = sum(f for _, _, f in classes)
    return sum((Fraction(lo + hi, 2)) * f for lo, hi, f in classes) / total, total


@solver('stats_hist_mean', problem=True)
def _stats_hist_mean(intervals, freqs, n, _p=None, _records=None):
    classes = _histogram_classes(one_svg(_p['question']))
    mean, total = _grouped_mean(classes)
    if total != fr(n):
        raise Cannot(f'the histogram bars give {total} items but the question says {n}')
    return [mean]


@diagram('stats_hist_mean')
def _check_hist_mean(inputs, html):
    classes = _histogram_classes(one_svg(html))
    want = [(lo, hi, fr(f)) for (lo, hi), f in zip(inputs['intervals'], inputs['freqs'])]
    return [] if classes == want else [f'the histogram shows {classes} but the question was built with {want}']


@solver('stats_hist_multi', problem=True)
def _stats_hist_multi(intervals, freqs, n, t_low, t_high, _p=None, _records=None):
    classes = _histogram_classes(one_svg(_p['question']))
    mean, total = _grouped_mean(classes)
    if total != fr(n):
        raise Cannot(f'the histogram bars give {total} items but the question says {n}')
    target = [c for c in classes if c[0] == fr(t_low) and c[1] == fr(t_high)]
    if len(target) != 1:
        raise Cannot(f'no single histogram class {t_low} to {t_high}')
    lo, hi, f = target[0]
    return [mean, f / (hi - lo), f / total]


@diagram('stats_hist_multi')
def _check_hist_multi(inputs, html):
    return _check_hist_mean(inputs, html)


@solver('stats_fd')
def _stats_fd(freq, width):
    return [_div(freq, width)]


def _div(a, b):
    if fr(b) == 0:
        raise Cannot('zero class width')
    return fr(a) / fr(b)


@diagram('stats_fd')
def _check_fd(inputs, html):
    bars = read_histogram(one_svg(html))
    want = float(_div(inputs['freq'], inputs['width']))
    if abs(bars[0][2] - want) > 0.1:
        return [f'the first bar is drawn at density {bars[0][2]:.2f} but should be {want}']
    if abs((bars[0][1] - bars[0][0]) - float(inputs['width'])) > 0.5:
        return [f'the first bar is {bars[0][1] - bars[0][0]:.1f} wide but the question says {inputs["width"]}']
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Box plot
# ─────────────────────────────────────────────────────────────────────────────

@solver('stats_box')
def _stats_box(min_val, q1, q2, q3, max_val):
    if not fr(min_val) <= fr(q1) <= fr(q2) <= fr(q3) <= fr(max_val):
        raise Cannot('box plot values are out of order')
    return [fr(q3) - fr(q1)]


@diagram('stats_box')
def _check_box(inputs, html):
    box = read_box_plot(one_svg(html))
    out = []
    names = {'min': 'min_val', 'q1': 'q1', 'median': 'q2', 'q3': 'q3', 'max': 'max_val'}
    for key, name in names.items():
        if box['labelled'][key] != fr(inputs[name]):
            out.append(f'the plot labels {key} as {box["labelled"][key]} but the question was built with {inputs[name]}')
    slack = box['per_px'] * PX + 1e-9
    for key, name in (('q1', 'q1'), ('q3', 'q3'), ('median', 'q2')):
        if box['drawn'][key] is None or abs(box['drawn'][key] - float(fr(inputs[name]))) > slack:
            out.append(f'the {key} is drawn at {box["drawn"][key]} but is labelled {inputs[name]}')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Comparing two distributions (a choice of statements)
# ─────────────────────────────────────────────────────────────────────────────

@solver('stats_compare')
def _stats_compare(med1, iqr1, med2, iqr2):
    if fr(med1) > fr(med2):
        typical = 'greater typical value: class a'
    elif fr(med2) > fr(med1):
        typical = 'greater typical value: class b'
    else:
        typical = 'equal medians (same typical value in both classes)'
    if fr(iqr1) < fr(iqr2):
        steady = 'more consistent: class a (smaller iqr)'
    elif fr(iqr2) < fr(iqr1):
        steady = 'more consistent: class b (smaller iqr)'
    else:
        steady = 'equal iqrs (same consistency in both classes)'
    want = f'{typical}; {steady}'
    return [Pick(lambda text: norm_text(text) == want, f'the statement {want!r}')]


# ─────────────────────────────────────────────────────────────────────────────
# Scatter graphs
# ─────────────────────────────────────────────────────────────────────────────

@solver('stats_scatter', problem=True)
def _stats_scatter(n, _p=None, _records=None):
    points = read_scatter_points(one_svg(_p['question']))
    if len(points) != int(n):
        raise Cannot(f'{len(points)} points are drawn but the question says {n}')
    r = pearson(points)
    # screen y runs downwards, so the sign of the correlation flips
    r = -r
    if r > 0.5:
        want = 'positive correlation'
    elif r < -0.5:
        want = 'negative correlation'
    elif abs(r) < 0.3:
        want = 'no correlation'
    else:
        raise Cannot(f'the points have r = {r:.2f}: neither a clear trend nor a clear lack of one')
    return [Pick(lambda text: norm_text(text) == want, f'the option {want!r} (r = {r:.2f})')]


@solver('stats_lobf')
def _stats_lobf(x1, y1, x2, y2, xq):
    if fr(x1) == fr(x2):
        raise Cannot('the two points have the same x')
    gradient = (fr(y2) - fr(y1)) / (fr(x2) - fr(x1))
    return [fr(y1) + gradient * (fr(xq) - fr(x1))]


# ─────────────────────────────────────────────────────────────────────────────
# Cumulative frequency
# ─────────────────────────────────────────────────────────────────────────────

def _cf_points(upper_bounds, cum_freqs):
    ub = [fr(u) for u in upper_bounds]
    cf = [fr(c) for c in cum_freqs]
    if len(ub) != len(cf) or len(ub) < 2:
        raise Cannot('cumulative frequency table is incomplete')
    width = ub[1] - ub[0]
    return [(ub[0] - width, Fraction(0))] + list(zip(ub, cf))


def _cf_value_at_fraction(points, fraction):
    target = points[-1][1] * fraction
    for (x0, c0), (x1, c1) in zip(points, points[1:]):
        if c1 >= target > c0 or (target == 0 and c0 == 0 and c1 > 0):
            return x0 + (target - c0) / (c1 - c0) * (x1 - x0)
    raise Cannot('the cumulative frequency never reaches the required value')


def _cf_count_below(points, x):
    for (x0, c0), (x1, c1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            return c0 + (x - x0) / (x1 - x0) * (c1 - c0)
    raise Cannot('the value is outside the graph')


@solver('stats_cf')
def _stats_cf(upper_bounds, cum_freqs):
    median = _cf_value_at_fraction(_cf_points(upper_bounds, cum_freqs), Fraction(1, 2))
    # an estimate read from a graph is keyed as the nearest whole number
    return [Pick(lambda text: parse_num(text) is not None and abs(parse_num(text) - median) <= Fraction(1, 2),
                 f'a whole-number estimate of the median {float(median):.2f}')]


@solver('stats_cf_multi')
def _stats_cf_multi(upper_bounds, cum_freqs, threshold):
    points = _cf_points(upper_bounds, cum_freqs)
    median = _cf_value_at_fraction(points, Fraction(1, 2))
    q1 = _cf_value_at_fraction(points, Fraction(1, 4))
    q3 = _cf_value_at_fraction(points, Fraction(3, 4))
    return [median, q3 - q1, _cf_count_below(points, fr(threshold))]


@diagram('stats_cf')
def _check_cf(inputs, html):
    drawn = read_cf_curve(one_svg(html))
    want = _cf_points(inputs['upper_bounds'], inputs['cum_freqs'])
    out = []
    if len(drawn) != len(want):
        return [f'the curve has {len(drawn)} points but the table has {len(want)}']
    top = float(want[-1][1])
    svg = one_svg(html)
    x_per_px = abs(x_axis_from_labels(svg, 308).scale)
    y_per_px = abs(y_axis_from_labels(svg, 55).scale)
    for (dx, dy), (wx, wy) in zip(drawn, want):
        if abs(dx - float(wx)) > x_per_px * PX or abs(dy - float(wy)) > y_per_px * PX:
            out.append(f'the curve passes through ({dx:.1f}, {dy:.1f}) but the data say ({float(wx):.1f}, {float(wy):.1f})')
    if top <= 0:
        out.append('the curve is empty')
    return out


@diagram('stats_cf_multi')
def _check_cf_multi(inputs, html):
    return _check_cf(inputs, html)

