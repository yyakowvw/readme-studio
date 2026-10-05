"""Themes and the shared SVG vocabulary.

Every generated file is a standalone SVG that GitHub serves through <img>: no
scripts, no remote fonts, no external images. The motion contract is the same
for every component:

* the default render is a complete, static composition;
* animation lives only inside `@media (prefers-reduced-motion: no-preference)`;
* elements that exist only for motion carry class `live` (hidden by default),
  their static stand-ins carry class `still`.
"""
from html import escape

FONT = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','Cascadia Mono',Menlo,Consolas,monospace"

# A theme is a background ramp, five accents (used in order for chips, steps,
# dividers and cards) and three text tones.
THEMES = {
    'aurora': {
        'night': '#08061A', 'ink': '#0D0A26', 'mid': '#170F45', 'deep': '#071B2B', 'glass': '#1A1548',
        'accents': ['#8B5CF6', '#F472B6', '#22D3EE', '#34D399', '#FBBF24'],
        'text': '#F7F5FF', 'soft': '#DCD6FF', 'muted': '#ADA6DA',
    },
    'sunset': {
        'night': '#160711', 'ink': '#1E0A18', 'mid': '#3A0F2E', 'deep': '#2B1206', 'glass': '#3A1530',
        'accents': ['#FB7185', '#F59E0B', '#F472B6', '#FDBA74', '#C084FC'],
        'text': '#FFF6F2', 'soft': '#FFDCD0', 'muted': '#D8A9A0',
    },
    'ocean': {
        'night': '#03111C', 'ink': '#061826', 'mid': '#0B2A44', 'deep': '#04202A', 'glass': '#0E2C44',
        'accents': ['#38BDF8', '#2DD4BF', '#818CF8', '#A3E635', '#F0ABFC'],
        'text': '#F0FAFF', 'soft': '#CDEBFA', 'muted': '#8DB5CB',
    },
    'matrix': {
        'night': '#020A05', 'ink': '#04110A', 'mid': '#082414', 'deep': '#03140F', 'glass': '#0B2416',
        'accents': ['#22C55E', '#A3E635', '#2DD4BF', '#FACC15', '#4ADE80'],
        'text': '#F0FFF4', 'soft': '#C9F5D6', 'muted': '#86B897',
    },
}


class Theme:
    def __init__(self, name='aurora', overrides=None):
        if name not in THEMES:
            raise ValueError(f'unknown theme {name!r}; choose one of {", ".join(THEMES)}')
        values = {**THEMES[name], **(overrides or {})}
        self.name = name
        self.__dict__.update(values)

    def accent(self, index):
        return self.accents[index % len(self.accents)]

    def pair(self, index):
        return self.accent(index), self.accent(index + 2)


def esc(value):
    return escape(str(value), quote=True)


def text(x, y, value, size=20, fill='#fff', weight=400, anchor=None, extra='', mono=False, spacing=None, cls=None):
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"']
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    classes = ' '.join(c for c in ('mono' if mono else '', cls or '') if c)
    if classes:
        attrs.append(f'class="{classes}"')
    if extra:
        attrs.append(extra)
    return f'<text {" ".join(attrs)}>{esc(value)}</text>'


def linear(id_, stops, x2=1, y2=0, x1=0, y1=0):
    body = ''
    for stop in stops:
        opacity = f' stop-opacity="{stop[2]}"' if len(stop) > 2 else ''
        body += f'<stop offset="{stop[0]}" stop-color="{stop[1]}"{opacity}/>'
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{body}</linearGradient>'


def radial(id_, color, opacity=0.5):
    return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
            f'<stop offset=".55" stop-color="{color}" stop-opacity="{opacity * .35:.3f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


def document(width, height, title, desc, body, defs='', motion='', css=''):
    """Wrap content in a standalone, accessible SVG with the motion contract."""
    style = (f'text{{font-family:{FONT}}}.mono{{font-family:{MONO}}}.live{{display:none}}{css}'
             f'@media (prefers-reduced-motion:no-preference){{.live{{display:inline}}.still{{display:none}}{motion}}}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" '
            f'role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>'
            f'<defs>{defs}</defs><style>{style}</style>{body}</svg>\n')


# System fonts differ per platform, so plain text is laid out against a
# deliberately generous estimate of its width.
def text_width(value, size, weight=400):
    factor = 0.0
    for char in str(value):
        if char == ' ':
            factor += .30
        elif char in 'il.,:;|!\'·':
            factor += .30
        elif char in 'mwMWЖШЩЮМ@%':
            factor += .92
        elif char.isupper() or 'Ѐ' <= char <= 'ӿ':
            factor += .68
        else:
            factor += .56
    return factor * size * (1.06 if weight >= 600 else 1.0)


def fit_text(value, size, max_width, weight=400, minimum=10):
    while size > minimum and text_width(value, size, weight) > max_width:
        size -= 1
    return size


def wrap(value, max_width, size, weight=400):
    """Greedy word wrap against the width estimate."""
    lines, line = [], ''
    for word in str(value).split():
        candidate = f'{line} {word}'.strip()
        if line and text_width(candidate, size, weight) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines
