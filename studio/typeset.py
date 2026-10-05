"""Outline text with the Unbounded typeface (SIL OFL 1.1, fonts/unbounded/).

GitHub serves README images without web fonts, so display headlines are drawn
as SVG paths. Visible meaning is always repeated in the SVG <title>/<desc> and
in the README alt text.
"""
from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).resolve().parents[1] / 'fonts/unbounded'


@lru_cache(maxsize=None)
def _fonts(weight):
    return [TTFont(FONT_DIR / f'unbounded-{subset}-{weight}-normal.woff') for subset in ('latin', 'cyrillic')]


def _glyph(char, weight):
    for font in _fonts(weight):
        name = font.getBestCmap().get(ord(char))
        if name:
            return font, name
    raise ValueError(f'Unbounded has no glyph for {char!r}')


def measure(text, size, weight=700, spacing=0.0):
    width = 0.0
    for char in text:
        font, name = _glyph(char, weight)
        width += font['hmtx'][name][0] * size / font['head'].unitsPerEm + spacing
    return width - (spacing if text else 0)


def outline(text, x, y, size, weight=700, anchor='start', spacing=0.0):
    """Return SVG path data for `text` with its baseline at y."""
    width = measure(text, size, weight, spacing)
    if anchor == 'middle':
        x -= width / 2
    elif anchor == 'end':
        x -= width
    parts, cursor = [], x
    for char in text:
        font, name = _glyph(char, weight)
        scale = size / font['head'].unitsPerEm
        pen = SVGPathPen(font.getGlyphSet(), ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
        font.getGlyphSet()[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
        parts.append(pen.getCommands())
        cursor += font['hmtx'][name][0] * scale + spacing
    return ''.join(parts)


def fit(text, size, max_width, weight=700, spacing=0.0, minimum=10):
    """Largest size <= size that keeps `text` within max_width."""
    while size > minimum and measure(text, size, weight, spacing) > max_width:
        size -= 1
    return size
