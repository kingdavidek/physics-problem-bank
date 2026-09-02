"""Static Zorp pose / costume stills for badges and other inserts.

Separate from the live corner mascot in templates/partials/buddy.html.
Unknown tokens fail closed to idle. Not E4.2 collectibles.
"""
from functools import lru_cache
import html
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = 'partials/zorp_kit.html'
VIEWBOX = '0 0 80 80'

ACTION_TOKENS = (
    'idle',
    'run',
    'jump',
    'sing',
    'eat',
    'wave',
    'think',
)
COSTUME_TOKENS = (
    'showman',
    'scholar',
    'explorer',
    'chef',
)
POSE_TOKENS = ACTION_TOKENS + COSTUME_TOKENS
_POSE_SET = frozenset(POSE_TOKENS)


@lru_cache(maxsize=1)
def _jinja_env():
    return Environment(
        loader=FileSystemLoader(str(ROOT / 'templates')),
        autoescape=select_autoescape(['html']),
    )


def resolve_pose(name):
    """Return an allowlisted pose token, or idle."""
    token = str(name or '').strip().lower().replace('-', '_')
    if token in _POSE_SET:
        return token
    return 'idle'


def _inner(name):
    tmpl = _jinja_env().get_template(TEMPLATE_NAME)
    return tmpl.module.inner(resolve_pose(name))


def pose(name, size=64, title=None):
    """Return a sized inline SVG for a named still.

    Decorative by default (``aria-hidden``). Pass ``title`` for a labelled image.
    """
    token = resolve_pose(name)
    try:
        size_n = int(size)
    except (TypeError, ValueError):
        size_n = 64
    if size_n < 16:
        size_n = 16
    if size_n > 256:
        size_n = 256
    attrs = [
        f'class="zorp-pose zorp-pose--{token}"',
        f'viewBox="{VIEWBOX}"',
        f'width="{size_n}"',
        f'height="{size_n}"',
        'focusable="false"',
    ]
    if title:
        attrs.append('role="img"')
        attrs.append(f'aria-label="{html.escape(str(title), quote=True)}"')
    else:
        attrs.append('aria-hidden="true"')
    return Markup(f'<svg {" ".join(attrs)}>{_inner(token)}</svg>')
