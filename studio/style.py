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


# Backgrounds can be combined with any accents ("colors": {"background": "navy"}).
BACKGROUNDS = {
    'midnight': {'night': '#08061A', 'ink': '#0D0A26', 'mid': '#170F45', 'deep': '#071B2B', 'glass': '#1A1548',
                 'text': '#F7F5FF', 'soft': '#DCD6FF', 'muted': '#ADA6DA'},
    'black':    {'night': '#050505', 'ink': '#0B0B0D', 'mid': '#17171C', 'deep': '#0E0E12', 'glass': '#1C1C22',
                 'text': '#FAFAFA', 'soft': '#E4E4E7', 'muted': '#A1A1AA'},
    'navy':     {'night': '#030B1E', 'ink': '#06132B', 'mid': '#0D2250', 'deep': '#061A2E', 'glass': '#11285A',
                 'text': '#F1F6FF', 'soft': '#D2E0FF', 'muted': '#93A8D4'},
    'forest':   {'night': '#030D08', 'ink': '#06150D', 'mid': '#0E2C1C', 'deep': '#05181A', 'glass': '#123222',
                 'text': '#F1FFF6', 'soft': '#CFEFDC', 'muted': '#8DB8A0'},
    'wine':     {'night': '#12040A', 'ink': '#1A0710', 'mid': '#3A0C22', 'deep': '#220812', 'glass': '#3B1226',
                 'text': '#FFF3F7', 'soft': '#FFD6E4', 'muted': '#D29AB0'},
    'plum':     {'night': '#0E0518', 'ink': '#150822', 'mid': '#2E0F48', 'deep': '#1B0A2E', 'glass': '#32164E',
                 'text': '#FBF4FF', 'soft': '#EBD8FF', 'muted': '#B79AD6'},
    'slate':    {'night': '#0B0E14', 'ink': '#11151D', 'mid': '#1E2532', 'deep': '#121822', 'glass': '#232B3A',
                 'text': '#F5F7FA', 'soft': '#D6DCE6', 'muted': '#97A1B3'},
    'espresso': {'night': '#100A06', 'ink': '#170F09', 'mid': '#2E1D12', 'deep': '#1C120A', 'glass': '#33231A',
                 'text': '#FFF8F1', 'soft': '#F2DECB', 'muted': '#C2A68C'},
}
PRESETS = {
    'neon':     ('black', ['#FF2BD6', '#00F0FF', '#B4FF39', '#FFE600', '#8A5CFF']),
    'candy':    ('plum', ['#FF7AB6', '#FFD166', '#7CF2C8', '#9B8CFF', '#FF9F6E']),
    'rose':     ('wine', ['#FB7185', '#F9A8D4', '#FDA4AF', '#E879F9', '#FCD34D']),
    'forest':   ('forest', ['#34D399', '#A3E635', '#FACC15', '#5EEAD4', '#86EFAC']),
    'ice':      ('navy', ['#7DD3FC', '#A5B4FC', '#E0F2FE', '#67E8F9', '#C4B5FD']),
    'ember':    ('espresso', ['#F97316', '#FACC15', '#EF4444', '#FDBA74', '#FB923C']),
    'gold':     ('black', ['#FACC15', '#F59E0B', '#FDE68A', '#D97706', '#FEF3C7']),
    'mono':     ('slate', ['#E5E7EB', '#9CA3AF', '#F9FAFB', '#D1D5DB', '#6B7280']),
    'cyber':    ('navy', ['#22D3EE', '#F472B6', '#FDE047', '#818CF8', '#4ADE80']),
    'lavender': ('plum', ['#C4B5FD', '#F0ABFC', '#A5B4FC', '#FBCFE8', '#DDD6FE']),
    'coral':    ('slate', ['#FB7185', '#FDBA74', '#2DD4BF', '#FCD34D', '#F472B6']),
    'galaxy':   ('midnight', ['#6366F1', '#EC4899', '#06B6D4', '#F59E0B', '#A855F7']),
    'mint':     ('black', ['#5EEAD4', '#A7F3D0', '#34D399', '#99F6E4', '#BEF264']),
    'retro':    ('espresso', ['#F59E0B', '#EF4444', '#14B8A6', '#FDE68A', '#FB923C']),
}
for _name, (_bg, _accents) in PRESETS.items():
    THEMES[_name] = {**BACKGROUNDS[_bg], 'accents': _accents}

NAMED = {
    'red': '#EF4444', 'orange': '#F97316', 'amber': '#F59E0B', 'yellow': '#FACC15', 'lime': '#A3E635',
    'green': '#22C55E', 'emerald': '#10B981', 'mint': '#5EEAD4', 'teal': '#14B8A6', 'cyan': '#22D3EE',
    'sky': '#38BDF8', 'blue': '#3B82F6', 'indigo': '#6366F1', 'violet': '#8B5CF6', 'purple': '#A855F7',
    'fuchsia': '#D946EF', 'pink': '#EC4899', 'rose': '#F43F5E', 'coral': '#FB7185', 'gold': '#EAB308',
    'white': '#F8FAFC', 'silver': '#CBD5E1', 'gray': '#9CA3AF', 'grey': '#9CA3AF', 'peach': '#FDBA74', 'lavender': '#C4B5FD',
    # Bulgarian names
    'червен': '#EF4444', 'оранжев': '#F97316', 'жълт': '#FACC15', 'зелен': '#22C55E', 'тюркоаз': '#14B8A6',
    'син': '#3B82F6', 'светлосин': '#38BDF8', 'лилав': '#8B5CF6', 'виолетов': '#8B5CF6', 'розов': '#EC4899',
    'златен': '#EAB308', 'бял': '#F8FAFC', 'сив': '#9CA3AF', 'мента': '#5EEAD4', 'корал': '#FB7185',
}


def parse_color(value):
    """'#8b5cf6', '8B5CF6', '#abc', 'violet' or 'лилав' -> '#8B5CF6' (None if not a colour)."""
    value = str(value).strip().lower()
    if value in NAMED:
        return NAMED[value]
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join(c * 2 for c in value)
    if len(value) == 6 and all(c in '0123456789abcdef' for c in value):
        return '#' + value.upper()
    return None


def _hsl(h, s, l):
    import colorsys
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))


def random_palette(seed=None):
    """Five bright accents that belong together (analogous, triadic or split-complementary)."""
    import random
    rng = random.Random(seed)
    base = rng.uniform(0, 360)
    offsets = rng.choice([[0, 30, 60, -30, 180], [0, 120, 240, 60, 180], [0, 150, 210, 30, -30], [0, 40, 180, 220, 90]])
    return [_hsl(base + o, rng.uniform(.7, .95), rng.uniform(.58, .7)) for o in offsets]


def resolve_colors(overrides):
    """Expand a config's "colors" block: background name, colour names, short accent lists."""
    out = dict(overrides or {})
    background = out.pop('background', None)
    if background:
        if background not in BACKGROUNDS:
            raise ValueError(f'unknown background {background!r}; choose one of {", ".join(BACKGROUNDS)}')
        out = {**BACKGROUNDS[background], **out}
    if 'accents' in out:
        accents = [parse_color(c) for c in out['accents']]
        if not accents or None in accents:
            raise ValueError(f'"accents" must be colours such as "#8B5CF6" or "violet": {out["accents"]}')
        count = len(accents)
        while len(accents) < 5:
            accents.append(accents[len(accents) % count])
        out['accents'] = accents[:5]
    for key in ('night', 'ink', 'mid', 'deep', 'glass', 'text', 'soft', 'muted'):
        if key in out:
            color = parse_color(out[key])
            if not color:
                raise ValueError(f'"{key}" must be a colour: {out[key]!r}')
            out[key] = color
    return out


class Theme:
    def __init__(self, name='aurora', overrides=None):
        if name not in THEMES:
            raise ValueError(f'unknown theme {name!r}; choose one of {", ".join(THEMES)}')
        values = {**THEMES[name], **resolve_colors(overrides)}
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
