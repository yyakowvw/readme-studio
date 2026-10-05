"""The visual components. Each one returns (svg, alt) for one language and one
width: 1200 px for desktop, 600 px for the mobile variant that README files
swap in through <picture>.
"""
import json
import math
import random
from pathlib import Path

from .style import document, esc, fit_text, linear, radial, text, text_width, wrap
from .typeset import fit, outline

ICONS = json.loads((Path(__file__).parent / 'data/icons.json').read_text())['icons']
_BY_TITLE = {v['title'].lower(): k for k, v in ICONS.items()}

UI = {
    'en': {'chapter': 'Chapter', 'divider': 'Decorative section transition.', 'decor': 'Motion is decorative.',
           'steps': 'steps', 'tech': 'technologies'},
    'bg': {'chapter': 'Глава', 'divider': 'Декоративен преход между секциите.', 'decor': 'Движението е декоративно.',
           'steps': 'стъпки', 'tech': 'технологии'},
}


def ui(lang, key):
    return UI.get(lang, UI['en'])[key]


def loc(value, lang, default=''):
    """Config strings are either plain text or {"en": ..., "bg": ...}."""
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(lang) or value.get('en') or next(iter(value.values()), default)
    if isinstance(value, list):
        return [loc(v, lang) for v in value]
    return value


# ---------------------------------------------------------------- helpers
def frame(w, h, radius=28, fill='url(#bg)'):
    return (f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>'
            f'<rect width="{w}" height="{h}" rx="{radius}" fill="{fill}"/>')


def stars(w, h, count, seed, top=0):
    rng = random.Random(seed)
    return ''.join(f'<circle cx="{rng.uniform(0, w):.0f}" cy="{rng.uniform(top, h):.0f}" r="{rng.choice([.8, 1, 1.2, 1.6])}" '
                   f'fill="#fff" opacity="{rng.uniform(.15, .55):.2f}"/>' for _ in range(count))


def icon(slug, x, y, size, fill):
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 24:.4f})"><path d="{ICONS[slug]["path"]}" fill="{fill}"/></g>'


def display(value, x, y, size, fill, anchor='start', weight=700, extra=''):
    """Headline drawn in Unbounded as paths, so it looks the same everywhere.
    Characters the typeface lacks fall back to bold system text."""
    try:
        return f'<path d="{outline(value, x, y, size, weight, anchor)}" fill="{fill}" {extra}/>'
    except ValueError:
        return text(x, y, value, size, fill, 800, anchor=anchor, extra=extra)


def display_fit(value, size, max_width):
    try:
        return fit(value, size, max_width)
    except ValueError:
        return fit_text(value, size, max_width, 800)


def luminance(color):
    color = color.lstrip('#')
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return .2126 * r + .7152 * g + .0722 * b


def resolve_tech(item):
    """'react', 'React' or {"name", "icon", "color"} -> (name, slug, color)."""
    if isinstance(item, dict):
        slug = item.get('icon')
        name = item.get('name') or (ICONS[slug]['title'] if slug in ICONS else slug)
        return name, slug if slug in ICONS else None, item.get('color') or (ICONS[slug]['hex'] if slug in ICONS else None)
    slug = item if item in ICONS else _BY_TITLE.get(str(item).lower())
    if slug:
        return ICONS[slug]['title'], slug, ICONS[slug]['hex']
    return str(item), None, None


def pills(labels, x, y, max_width, size, colors, t, height=38, gap=12, row_gap=12):
    """Flow-layout chips; returns (svg, bottom)."""
    out, cx, cy = '', x, y
    for i, label in enumerate(labels):
        pw = text_width(label, size, 700) + 52
        if cx > x and cx + pw > x + max_width:
            cx, cy = x, cy + height + row_gap
        col = colors[i % len(colors)]
        out += (f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{pw:.0f}" height="{height}" rx="{height / 2:.0f}" fill="#fff" fill-opacity=".06" '
                f'stroke="{col}" stroke-opacity=".75"/><circle cx="{cx + 21:.0f}" cy="{cy + height / 2:.0f}" r="6" fill="{col}"/>')
        out += text(cx + 36, cy + height / 2 + size * .36, label, size, t.text, 700)
        cx += pw + gap
    return out, cy + height


def ellipse_path(cx, cy, rx, ry):
    return f'M{cx - rx:.1f} {cy:.1f}a{rx:.1f} {ry:.1f} 0 1 0 {2 * rx:.1f} 0a{rx:.1f} {ry:.1f} 0 1 0 {-2 * rx:.1f} 0'


def on_ellipse(cx, cy, rx, ry, tilt, angle):
    a, tl = math.radians(angle), math.radians(tilt)
    x, y = rx * math.cos(a), ry * math.sin(a)
    return cx + x * math.cos(tl) - y * math.sin(tl), cy + x * math.sin(tl) + y * math.cos(tl)


# ---------------------------------------------------------------- hero
def hero(sec, t, lang, mobile):
    kicker = loc(sec.get('kicker'), lang)
    head = loc(sec.get('headline'), lang)
    head = head if isinstance(head, list) else [head]
    lines = loc(sec.get('lines', []), lang)
    chips = loc(sec.get('chips', []), lang)[:4]
    w = 600 if mobile else 1200
    x0 = 32 if mobile else 72
    tw = w - 2 * x0 if mobile else 640
    hs = min(display_fit(line, 46 if mobile else 56, tw) for line in head)
    y = 78 if mobile else 108
    kick = ''
    if kicker:
        ks = fit_text(kicker, 18 if mobile else 16, tw - 48, 700)
        kick = (f'<rect x="{x0}" y="{y - 9}" width="30" height="4" rx="2" fill="url(#acc)"/>'
                + text(x0 + 44, y, kicker.upper(), ks, t.soft, 700, spacing=2.6))
        y += 30
    body = kick
    y += hs * 1.15
    for i, line in enumerate(head):
        body += display(line, x0, y, hs, t.text if i == 0 else 'url(#hg)')
        y += hs * 1.3
    y += 4
    ls = 21
    for line in lines:
        for part in wrap(line, tw, ls):
            body += text(x0, y, part, ls, t.soft)
            y += 32
    if chips:
        chip_svg, bottom = pills(chips, x0, y + 10, tw, 20 if mobile else 17, t.accents, t, height=42 if mobile else 38)
        body += chip_svg
        y = bottom
    text_bottom = y
    if mobile:
        h = round(text_bottom + 420)
        cx, cy, k = 300, text_bottom + 190, .72
    else:
        h = max(560, round(text_bottom + 90))
        cx, cy, k = 918, h * .48, 1.0
    tilt = -16
    defs = (linear('bg', [(0, t.night), (.55, t.mid), (1, t.deep)], x2=1, y2=1)
            + ''.join(radial(f'r{i}', t.accent(i), [.55, .42, .32, .30][i]) for i in range(4))
            + linear('hg', [(0, t.accent(0)), (.5, t.accent(1)), (1, t.accent(4))])
            + linear('acc', [(0, t.accent(0)), (.5, t.accent(2)), (1, t.accent(3))])
            + ''.join(linear(f'o{i}', [(0, t.accent(i), .9), (1, t.accent(i + 2), .15)]) for i in range(3))
            + f'<radialGradient id="core"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".3" stop-color="{t.accent(1)}"/>'
              f'<stop offset=".62" stop-color="{t.accent(0)}" stop-opacity=".9"/><stop offset="1" stop-color="{t.accent(0)}" stop-opacity="0"/></radialGradient>'
            + linear('fy', [(0, '#000'), (.35, '#fff', .6), (1, '#fff')], x2=0, y2=1)
            + linear('beam', [(0, '#fff', 0), (.5, '#fff', .13), (1, '#fff', 0)])
            + '<mask id="fadeY"><rect width="100%" height="100%" fill="url(#fy)"/></mask>')
    horizon = cy + 140 * k
    motion = ('.b1{animation:d1 30s ease-in-out infinite}.b2{animation:d2 38s ease-in-out infinite}'
              '.b3{animation:d3 44s ease-in-out infinite}.b4{animation:d2 26s ease-in-out infinite reverse}'
              '.fl{animation:floor 8s cubic-bezier(.55,0,.9,.4) infinite}'
              '.halo{transform-box:fill-box;transform-origin:center;animation:breathe 9s ease-in-out infinite}'
              '.ring{transform-box:fill-box;transform-origin:center;animation:spin 60s linear infinite}'
              '.ring2{transform-box:fill-box;transform-origin:center;animation:spin 90s linear infinite reverse}'
              '.beam{animation:beam 16s ease-in-out infinite}.spark{animation:spark 11s cubic-bezier(.6,0,.3,1) infinite}'
              '@keyframes d1{50%{transform:translate(-60px,40px)}}@keyframes d2{50%{transform:translate(50px,-30px)}}'
              '@keyframes d3{50%{transform:translate(70px,-50px)}}'
              f'@keyframes floor{{0%{{transform:translateY(0);opacity:0}}12%{{opacity:.9}}100%{{transform:translateY({h - horizon:.0f}px);opacity:.9}}}}'
              '@keyframes breathe{50%{transform:scale(1.12);opacity:.75}}@keyframes spin{to{transform:rotate(360deg)}}'
              f'@keyframes beam{{0%,20%{{transform:translateX(-500px)}}70%,100%{{transform:translateX({w + 300}px)}}}}'
              f'@keyframes spark{{0%{{transform:translateX(0);opacity:0}}8%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateX({w - 2 * x0 - 140}px);opacity:0}}}}')
    b = frame(w, h) + '<g clip-path="url(#frame)">'
    b += (f'<g class="b1"><circle cx="{w * .8:.0f}" cy="{h * .2:.0f}" r="{380 * k:.0f}" fill="url(#r0)"/></g>'
          f'<g class="b2"><circle cx="{w * .92:.0f}" cy="{h * .85:.0f}" r="{320 * k:.0f}" fill="url(#r1)"/></g>'
          f'<g class="b3"><circle cx="{w * .2:.0f}" cy="{h * .98:.0f}" r="{340 * k:.0f}" fill="url(#r2)"/></g>'
          f'<g class="b4"><circle cx="{w * .52:.0f}" cy="{h * .05:.0f}" r="{220 * k:.0f}" fill="url(#r3)"/></g>')
    b += stars(w, h, 45 if mobile else 70, 7)
    floor = ''.join(f'<path d="M{cx + i * 16 * k:.0f} {horizon:.0f}L{cx + i * 120 * k:.0f} {h}" stroke="{t.accent(0)}" stroke-opacity=".28"/>'
                    for i in range(-14, 15))
    for i in range(1, 6):
        yy = horizon + (h - horizon) * (i / 6) ** 2
        floor += f'<path d="M0 {yy:.0f}H{w}" stroke="{t.accent(2)}" stroke-opacity=".18"/>'
    floor += '<g class="live">' + ''.join(
        f'<path class="fl" style="animation-delay:-{i * 1.6:.1f}s" d="M0 {horizon:.0f}H{w}" stroke="{t.accent(3)}" stroke-opacity=".55"/>'
        for i in range(5)) + '</g>'
    b += f'<g mask="url(#fadeY)">{floor}</g>'
    b += f'<g class="live"><rect class="beam" x="0" y="-200" width="160" height="{h + 400}" fill="url(#beam)" transform="rotate(18 {w / 2} {h / 2})"/></g>'
    orbits = [(255, 90, 24, 30), (190, 66, 17, 200), (126, 44, 12, 110), (255, 90, 34, 210)]
    b += f'<circle class="halo" cx="{cx}" cy="{cy:.0f}" r="{150 * k:.0f}" fill="url(#r1)"/>'
    b += f'<g transform="rotate({tilt} {cx} {cy:.0f})">' + ''.join(
        f'<path d="{ellipse_path(cx, cy, rx * k, ry * k)}" fill="none" stroke="url(#o{i})" stroke-width="1.6"/>'
        for i, (rx, ry, _d, _s) in enumerate(orbits[:3])) + '</g>'
    b += (f'<circle class="ring2" cx="{cx}" cy="{cy:.0f}" r="{80 * k:.0f}" fill="none" stroke="{t.soft}" stroke-opacity=".35" stroke-dasharray="2 9"/>'
          f'<circle class="ring" cx="{cx}" cy="{cy:.0f}" r="{62 * k:.0f}" fill="none" stroke="{t.accent(1)}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="60 30 8 30"/>'
          f'<circle cx="{cx}" cy="{cy:.0f}" r="{44 * k:.0f}" fill="url(#core)"/>')
    live, still = '', ''
    for i, (rx, ry, dur, start) in enumerate(orbits[:max(len(chips), 3)]):
        color = t.accent(i)
        dot = (f'<circle r="{15 * k:.0f}" fill="{color}" opacity=".22"/><circle r="{6.5 * k:.1f}" fill="{color}"/>'
               f'<circle r="{2.4 * k:.1f}" fill="#fff"/>')
        live += (f'<g transform="rotate({tilt} {cx} {cy:.0f})"><g>{dot}<animateMotion dur="{dur}s" repeatCount="indefinite" '
                 f'begin="-{dur * start / 360:.2f}s" path="{ellipse_path(cx, cy, rx * k, ry * k)}"/></g></g>')
        px, py = on_ellipse(cx, cy, rx * k, ry * k, tilt, 180 + start)
        still += f'<g transform="translate({px:.1f} {py:.1f})">{dot}</g>'
    b += f'<g class="live">{live}</g><g class="still">{still}</g>'
    b += body
    base = h - 34
    b += f'<rect x="{x0}" y="{base}" width="{w - 2 * x0}" height="3" rx="1.5" fill="url(#acc)" opacity=".85"/>'
    b += f'<g class="live"><rect class="spark" x="{x0}" y="{base - 2}" width="140" height="7" rx="3.5" fill="#fff" opacity=".85"/></g>'
    b += '</g>'
    title = ' '.join(head)
    alt = ' · '.join(x for x in [kicker, title] if x)
    desc = f'{alt}. {" ".join(lines)} {" · ".join(chips)}. {ui(lang, "decor")}'.strip()
    return document(w, h, alt, desc, b, defs, motion), alt


# ---------------------------------------------------------------- section heading
def heading(sec, t, lang, mobile, index=0):
    title = loc(sec.get('title'), lang)
    kicker = loc(sec.get('kicker'), lang)
    sub = loc(sec.get('subtitle'), lang)
    a1, a2 = t.pair(index)
    w = 600 if mobile else 1200
    x0 = 32 if mobile else 48
    size = 40 if mobile else 50
    max_w = w - 2 * x0
    lines = [title]
    if display_fit(title, size, max_w) < size * .72:
        words, lines, line = title.split(), [], ''
        for word in words:
            cand = f'{line} {word}'.strip()
            if line and display_fit(cand, size, max_w) < size:
                lines.append(line)
                line = word
            else:
                line = cand
        lines.append(line)
    fs = min(display_fit(line, size, max_w) for line in lines)
    y = 54 if kicker else 30
    defs = (linear('hg', [(0, a1), (.6, a2), (1, t.text)]) + linear('bar', [(0, a1), (1, a2)]) + radial('gl', a1, .45)
            + radial('gl2', a2, .3) + linear('bg', [(0, t.night), (.6, t.mid), (1, t.deep)], x2=1, y2=1))
    b = ''
    if kicker:
        b += text(x0, y, kicker.upper(), 18 if mobile else 14, a1, 800, spacing=2.6)
    y += fs * 1.2
    for line in lines:
        b += display(line, x0, y, fs, 'url(#hg)')
        y += fs * 1.25
    y -= fs * .25
    if sub:
        ss = 20 if mobile else 18
        for part in wrap(sub, max_w, ss):
            y += ss * 1.5
            b += text(x0, y, part, ss, t.soft)
    y += 24
    b += f'<rect x="{x0}" y="{y:.0f}" width="{max_w}" height="2" rx="1" fill="{t.text}" opacity=".1"/>'
    b += f'<rect x="{x0}" y="{y - 1:.0f}" width="120" height="4" rx="2" fill="url(#bar)"/>'
    b += f'<rect class="live sweep" x="{x0}" y="{y - 1:.0f}" width="60" height="4" rx="2" fill="#fff" opacity=".8"/>'
    h = round(y + 30)
    b = (frame(w, h, 24) + '<g clip-path="url(#frame)">'
         f'<g class="aur"><circle cx="{w * .86:.0f}" cy="{h * .2:.0f}" r="{w * .3:.0f}" fill="url(#gl)"/></g>'
         f'<circle cx="{w * .05:.0f}" cy="{h:.0f}" r="{w * .2:.0f}" fill="url(#gl2)"/>' + stars(w, h, 18 if mobile else 30, 11 + index)
         + f'<rect width="{w}" height="3" fill="url(#bar)"/>' + b + '</g>')
    motion = (f'.sweep{{animation:sweep 7s cubic-bezier(.6,0,.3,1) infinite}}@keyframes sweep{{0%{{transform:translateX(0);opacity:0}}'
              f'10%{{opacity:.8}}70%{{transform:translateX({max_w - 60}px);opacity:.8}}80%,100%{{transform:translateX({max_w - 60}px);opacity:0}}}}'
              '.aur{animation:aur 18s ease-in-out infinite}@keyframes aur{50%{transform:translate(-40px,10px)}}')
    alt = ' — '.join(x for x in [title, sub] if x)
    return document(w, h, title, alt, b, defs, motion), title


# ---------------------------------------------------------------- dividers
MOTIFS = ['waves', 'beads', 'circuit', 'constellation', 'sunrise']


def divider(sec, t, lang, mobile, index=0):
    motif = sec.get('motif') or MOTIFS[index % len(MOTIFS)]
    a1, a2 = t.pair(index)
    w, h = (600, 92) if mobile else (1200, 104)
    mid = h / 2
    r = 26 if mobile else 30
    bx = r + 6
    defs = (linear('g', [(0, a1), (1, a2)]) + linear('ge', [(0, a1, 0), (.12, a1, .9), (.88, a2, .9), (1, a2, 0)])
            + radial('glow', a1, .55) + linear('band', [(0, t.ink), (.5, t.mid), (1, t.ink)]))
    motion = '.ringd{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}'
    x0, x1 = bx + r + 24, w - 8
    span = x1 - x0
    m = ''
    if motif == 'waves':
        period = 150 if mobile else 240
        for j, (amp, op, sw) in enumerate([(14, .9, 2.2), (9, .55, 1.4), (20, .3, 1)]):
            d = f'M{x0 - period * 2} {mid}'
            for i in range(int((span + period * 4) / (period / 2)) + 2):
                xx = x0 - period * 2 + (i + 1) * period / 2
                cy_ = mid + (amp if (i + j) % 2 == 0 else -amp) * (.7 if mobile else 1)
                d += f'Q{xx - period / 4:.0f} {cy_:.0f} {xx:.0f} {mid}'
            m += f'<path class="wv" style="animation-duration:{10 + j * 4}s" d="{d}" fill="none" stroke="url(#g)" stroke-width="{sw}" opacity="{op}"/>'
        motion += f'.wv{{animation:wave 12s linear infinite}}@keyframes wave{{to{{transform:translateX({period}px)}}}}'
    elif motif == 'beads':
        n = 26 if mobile else 46
        for i in range(n):
            xx = x0 + span * i / (n - 1)
            yy = mid + math.sin(i / 2.6) * (h * .16)
            m += (f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{3.2 if i % 3 else 4.6}" fill="url(#g)" opacity=".75"/>'
                  f'<circle class="live bd" style="animation-delay:{i * .11:.2f}s" cx="{xx:.1f}" cy="{yy:.1f}" r="9" fill="{a2}" opacity="0"/>')
        motion += f'.bd{{animation:bead {n * .11 + 2:.1f}s ease-in-out infinite}}@keyframes bead{{0%,12%,100%{{opacity:0}}5%{{opacity:.55}}}}'
    elif motif == 'circuit':
        rng = random.Random(index * 11 + (1 if mobile else 0))
        lanes = [mid - h * .22, mid, mid + h * .22]
        for j, ly in enumerate(lanes):
            d, xx = f'M{x0} {ly:.0f}', x0
            while xx < x1 - 60:
                xx = min(xx + rng.randint(60, 140), x1)
                d += f'H{xx}'
                if rng.random() < .45 and xx < x1 - 40:
                    other = lanes[(j + rng.choice([1, 2])) % 3]
                    d += f'L{xx + 14} {other:.0f}L{xx + 28} {ly:.0f}'
                    xx += 28
                    m += f'<circle cx="{xx - 14}" cy="{other:.0f}" r="2.6" fill="{a2}"/>'
            m += f'<path d="{d}H{x1}" fill="none" stroke="url(#ge)" stroke-width="1.4" opacity=".55"/>'
            m += (f'<path class="live ct" style="animation-delay:-{j * 2.2}s" d="{d}H{x1}" fill="none" stroke="#fff" stroke-width="2.2" '
                  'pathLength="100" stroke-dasharray="4 96" stroke-linecap="round"/>')
        motion += '.ct{animation:trace 7s linear infinite}@keyframes trace{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}'
    elif motif == 'constellation':
        rng = random.Random(4 + index + (1 if mobile else 0))
        n = 8 if mobile else 14
        pts = [(x0 + span * (i + rng.uniform(.1, .9)) / n, rng.uniform(h * .2, h * .8)) for i in range(n)]
        for (ax, ay), (bx_, by) in zip(pts, pts[1:]):
            m += f'<path d="M{ax:.0f} {ay:.0f}L{bx_:.0f} {by:.0f}" stroke="url(#ge)" stroke-opacity=".6"/>'
        for i, (px, py) in enumerate(pts):
            m += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{2.5 + (i % 3)}" fill="{a1 if i % 2 else a2}"/>'
            m += f'<circle class="st" style="animation-delay:{i * .7:.1f}s" cx="{px:.0f}" cy="{py:.0f}" r="10" fill="url(#glow)" opacity=".15"/>'
        motion += f'.st{{animation:star {n * .7:.1f}s ease-in-out infinite}}@keyframes star{{0%,100%{{opacity:.15}}8%{{opacity:1}}20%{{opacity:.15}}}}'
    else:  # sunrise
        cxs = x0 + span / 2
        for i in range(6):
            rr = 24 + i * h * (.28 if mobile else .3)
            m += (f'<path class="{"sr" if i % 2 else "sr2"}" d="M{cxs - rr:.0f} {h}A{rr:.0f} {rr:.0f} 0 0 1 {cxs + rr:.0f} {h}" fill="none" '
                  f'stroke="url(#g)" stroke-width="1.6" opacity="{.85 - i * .12:.2f}" stroke-dasharray="{14 + i * 6} {10 + i * 4}"/>')
        m += f'<path d="M{x0} {h - 1}H{x1}" stroke="url(#ge)" stroke-width="2"/>'
        motion += '.sr{animation:dash 14s linear infinite}.sr2{animation:dash 20s linear infinite reverse}@keyframes dash{to{stroke-dashoffset:-240}}'
    num = f'{index + 1:02d}'
    b = (f'<rect width="{w}" height="{h}" rx="{h / 2:.0f}" fill="url(#band)"/>'
         f'<clipPath id="motif"><rect x="{x0}" y="0" width="{span}" height="{h}"/></clipPath><g clip-path="url(#motif)">{m}</g>')
    b += (f'<circle cx="{bx}" cy="{mid}" r="{r + 10}" fill="url(#glow)" opacity=".6"/>'
          f'<circle cx="{bx}" cy="{mid}" r="{r}" fill="{t.ink}" stroke="url(#g)" stroke-width="2"/>'
          f'<circle class="ringd" cx="{bx}" cy="{mid}" r="{r + 6}" fill="none" stroke="{a2}" stroke-opacity=".7" stroke-dasharray="3 7"/>')
    b += text(bx, mid + (8 if mobile else 9), num, 22 if mobile else 24, t.text, 800, anchor='middle')
    label = f'{ui(lang, "chapter")} {num}'
    return document(w, h, label, f'{label}. {ui(lang, "divider")}', b, defs, motion), label


# ---------------------------------------------------------------- project cards
def motif(kind, x, y, w, h, a1, a2, t):
    m, css = '', ''
    if kind == 'scan':
        rng = random.Random(3)
        for i in range(6):
            yy = y + 10 + i * (h - 20) / 5
            ln = rng.uniform(.35, .8) * (w - 60)
            m += (f'<rect x="{x}" y="{yy - 4:.0f}" width="{ln:.0f}" height="8" rx="4" fill="{a1}" opacity=".28"/>'
                  f'<rect x="{x}" y="{yy - 4:.0f}" width="{ln * .35:.0f}" height="8" rx="4" fill="{a1}" opacity=".55"/>'
                  f'<circle cx="{x + w - 22}" cy="{yy:.0f}" r="6" fill="{a2}" opacity=".35"/>'
                  f'<circle class="ok" style="animation-delay:{.6 + i * .55:.2f}s" cx="{x + w - 22}" cy="{yy:.0f}" r="6" fill="{a2}" opacity=".35"/>')
        m += f'<rect class="live scanb" x="{x - 10}" y="{y}" width="4" height="{h}" rx="2" fill="{a2}" opacity=".9"/>'
        css = (f'.scanb{{animation:scan 6s cubic-bezier(.5,0,.5,1) infinite}}@keyframes scan{{0%{{transform:translateX(0);opacity:0}}8%{{opacity:.9}}'
               f'60%{{transform:translateX({w - 30}px);opacity:.9}}70%,100%{{transform:translateX({w - 30}px);opacity:0}}}}'
               '.ok{animation:ok 6s ease-out infinite}@keyframes ok{0%,100%{opacity:.35}8%,60%{opacity:1}}')
    elif kind == 'tree':
        levels = [[.5], [.2, .5, .8], [.08, .26, .42, .58, .74, .92]]
        pts = [[(x + w * f, y + 12 + li * (h - 24) / 2) for f in level] for li, level in enumerate(levels)]
        for li in range(2):
            for i, (px, py) in enumerate(pts[li + 1]):
                parent = pts[li][min(len(pts[li]) - 1, i * len(pts[li]) // len(pts[li + 1]))]
                mid = (parent[1] + py) / 2
                m += f'<path d="M{parent[0]:.0f} {parent[1]:.0f}C{parent[0]:.0f} {mid:.0f} {px:.0f} {mid:.0f} {px:.0f} {py:.0f}" fill="none" stroke="{a1}" stroke-opacity=".4"/>'
        k = 0
        for li, level in enumerate(pts):
            for px, py in level:
                m += (f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{9 - li * 2}" fill="{t.ink}" stroke="{a1 if li < 2 else a2}" stroke-width="2"/>'
                      f'<circle class="nd" style="animation-delay:{li * .9 + k * .08:.2f}s" cx="{px:.0f}" cy="{py:.0f}" r="{9 - li * 2}" fill="{a2}" opacity="0"/>')
                k += 1
        css = '.nd{animation:node 7s ease-in-out infinite}@keyframes node{0%,100%{opacity:0}6%,22%{opacity:.85}36%{opacity:0}}'
    elif kind == 'network':
        hub = (x + w / 2, y + h / 2)
        for i in range(6):
            a = i * math.pi / 3 + .3
            px, py = hub[0] + math.cos(a) * w * .38, hub[1] + math.sin(a) * h * .42
            m += (f'<path d="M{hub[0]:.0f} {hub[1]:.0f}L{px:.0f} {py:.0f}" stroke="{a1}" stroke-opacity=".35"/>'
                  f'<path class="lk" style="animation-delay:-{i * .8:.1f}s" d="M{hub[0]:.0f} {hub[1]:.0f}L{px:.0f} {py:.0f}" stroke="{a2}" stroke-width="2" '
                  'pathLength="100" stroke-dasharray="10 90" stroke-dashoffset="100"/>'
                  f'<circle cx="{px:.0f}" cy="{py:.0f}" r="7" fill="{t.ink}" stroke="{a2}" stroke-width="2"/>')
        m += f'<circle cx="{hub[0]:.0f}" cy="{hub[1]:.0f}" r="16" fill="{a1}" opacity=".3"/><circle cx="{hub[0]:.0f}" cy="{hub[1]:.0f}" r="9" fill="{a1}"/>'
        css = '.lk{animation:link 4.8s linear infinite}@keyframes link{from{stroke-dashoffset:100}to{stroke-dashoffset:-10}}'
    elif kind == 'hex':
        size = 15
        for r_ in range(4):
            for c_ in range(int(w / (size * 1.8))):
                cx_ = x + 14 + c_ * size * 1.75 + (size * .87 if r_ % 2 else 0)
                cy_ = y + 16 + r_ * size * 1.5
                if cx_ > x + w - 10:
                    continue
                pts = ' '.join(f'{cx_ + size * math.cos(math.radians(60 * i + 30)):.1f},{cy_ + size * math.sin(math.radians(60 * i + 30)):.1f}' for i in range(6))
                m += (f'<polygon points="{pts}" fill="none" stroke="{a1}" stroke-opacity=".35"/>'
                      f'<polygon class="hx" style="animation-delay:{(c_ + r_) * .16:.2f}s" points="{pts}" fill="{a2}" opacity="0"/>')
        css = '.hx{animation:hex 6s ease-in-out infinite}@keyframes hex{0%,100%{opacity:0}10%{opacity:.5}24%{opacity:0}}'
    else:  # page
        blocks = [(0, 0, 1, .14, a1), (0, .22, .58, .3, a2), (.64, .22, .36, .3, a1), (0, .6, .31, .4, a2), (.345, .6, .31, .4, a1), (.69, .6, .31, .4, a2)]
        m += f'<rect x="{x - 6}" y="{y - 6}" width="{w + 12}" height="{h + 12}" rx="12" fill="none" stroke="{a1}" stroke-opacity=".35" stroke-dasharray="4 6"/>'
        for i, (bx_, by_, bw, bh, col) in enumerate(blocks):
            m += f'<rect class="pg" style="animation-delay:{i * .45:.2f}s" x="{x + bx_ * w:.0f}" y="{y + by_ * h:.0f}" width="{bw * w:.0f}" height="{bh * h:.0f}" rx="7" fill="{col}" opacity=".45"/>'
        css = '.pg{animation:pg 9s ease-in-out infinite}@keyframes pg{0%{opacity:.08}8%,70%{opacity:.6}85%,100%{opacity:.08}}'
    return m, css


PROJECT_MOTIFS = ['scan', 'network', 'tree', 'hex', 'page']


def project(item, t, lang, mobile, index=0):
    name = loc(item.get('name'), lang)
    kind = loc(item.get('kind'), lang)
    about = loc(item.get('description'), lang)
    tags = loc(item.get('tags', []), lang)
    a1, a2 = t.pair(index)
    n = f'{index + 1:02d}'
    w = 600 if mobile else 1200
    defs = (linear('bg', [(0, t.ink), (.6, t.mid), (1, t.deep)], x2=1, y2=1) + linear('g', [(0, a1), (1, a2)])
            + linear('name', [(0, '#FFFFFF'), (.55, '#FFFFFF'), (1, a2)]) + radial('gl', a1, .5) + radial('gl2', a2, .4))
    b = ''
    if mobile:
        x0, tw = 32, 536
        b += text(24, 92, n, 80, 'none', 800, extra='stroke="url(#g)" stroke-width="2"')
        y = 50
        for line in wrap(kind.upper(), 600 - 140 - 32, 18, 800):
            b += text(140, y, line, 18, a1, 800, spacing=1.6)
            y += 24
        y = max(y, 110) + 30
        ns = display_fit(name, 40, tw)
        b += display(name, x0, y, ns, 'url(#name)')
        y += 24
        for line in wrap(about, tw, 21):
            y += 30
            b += text(x0, y, line, 21, t.soft)
        if tags:
            tag_svg, y = pills(tags, x0, y + 22, tw, 19, [a1, a2], t, height=40, gap=10, row_gap=10)
            b += tag_svg
        mm, css = motif(item.get('motif') or PROJECT_MOTIFS[index % 5], 30, y + 30, w - 60, 66, a1, a2, t)
        h = round(y + 30 + 66 + 30)
    else:
        x0, tw = 232, 600
        y = 62
        b += text(x0, y, kind.upper(), 15, a1, 800, spacing=3) if kind else ''
        ns = display_fit(name, 44, tw)
        y += ns * 1.25
        b += display(name, x0, y, ns, 'url(#name)')
        y += 6
        for line in wrap(about, tw, 19)[:4]:
            y += 29
            b += text(x0, y, line, 19, t.soft)
        if tags:
            tag_svg, y = pills(tags, x0, y + 22, tw, 15, [a1, a2], t, height=32, gap=10, row_gap=10)
            b += tag_svg
        h = max(230, round(y + 38))
        b = (text(40, 150, n, 118, 'none', 800, extra='stroke="url(#g)" stroke-width="2"')
             + text(40, 150, n, 118, a1, 800, extra='opacity=".08"') + b)
        mm, css = motif(item.get('motif') or PROJECT_MOTIFS[index % 5], 900, h / 2 - 54, 260, 108, a1, a2, t)
    shell = frame(w, h, 22) + '<g clip-path="url(#frame)">'
    shell += (f'<g class="aur"><circle cx="{w * .82:.0f}" cy="{h * .3:.0f}" r="{h * 1.3:.0f}" fill="url(#gl)"/></g>'
              f'<circle cx="{w * .08:.0f}" cy="{h:.0f}" r="{h:.0f}" fill="url(#gl2)"/><rect x="0" y="0" width="{w}" height="3" fill="url(#g)"/>')
    shell += (f'<rect class="live edge" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="21" fill="none" stroke="#fff" stroke-width="2" '
              'pathLength="1000" stroke-dasharray="80 920" stroke-linecap="round"/>')
    b = shell + b + f'<g>{mm}</g></g>'
    motion = ('.aur{animation:aur 22s ease-in-out infinite}@keyframes aur{50%{transform:translate(-40px,14px)}}'
              '.edge{animation:edge 14s linear infinite}@keyframes edge{to{stroke-dashoffset:-1000}}' + css)
    alt = f'{n} · {name}'
    desc = '. '.join(x for x in [alt, kind, about, ', '.join(tags)] if x)
    return document(w, h, alt, desc, b, defs, motion), alt


# ---------------------------------------------------------------- technology grid
def stack(sec, t, lang, mobile, index=0):
    title = loc(sec.get('title'), lang)
    items = [resolve_tech(i) for i in sec.get('items', [])]
    n = len(items)
    a1, a2 = t.pair(index)
    w = 600 if mobile else 1200
    cell_w, cell_h, tile, gap = (134, 172, 92, 0) if mobile else (128, 150, 82, 12)
    cols = 4 if mobile else math.ceil(n / math.ceil(n / 8))
    rows = math.ceil(n / cols)
    x0 = 32 if mobile else 48
    title_lines = wrap(title, w - 2 * x0, 33 if mobile else 31, 800) if title else []
    head = 70 + len(title_lines) * 40 + 10
    h = head + rows * cell_h + 26
    step = .55
    defs = (linear('bg', [(0, t.ink), (.65, t.mid), (1, t.deep)], x2=1, y2=1) + linear('g', [(0, a1), (1, a2)])
            + radial('au1', a1, .42) + radial('au2', a2, .32))
    motion = ('.aur{animation:aur 26s ease-in-out infinite}.aur2{animation:aur 34s ease-in-out infinite reverse}@keyframes aur{50%{transform:translate(-80px,30px)}}'
              f'.seq{{opacity:0;animation:seq {max(n, 1) * step:.2f}s ease-in-out infinite}}'
              f'@keyframes seq{{0%{{opacity:0}}{100 / max(n, 1) * .6:.2f}%{{opacity:1}}{100 / max(n, 1) * 2.2:.2f}%,100%{{opacity:0}}}}'
              '.flt{animation:flt 6s ease-in-out infinite}@keyframes flt{50%{transform:translateY(-4px)}}')
    b = frame(w, h, 30) + '<g clip-path="url(#frame)">'
    b += (f'<g class="aur"><circle cx="{w * .85:.0f}" cy="{h * .15:.0f}" r="{max(w, h) * .45:.0f}" fill="url(#au1)"/></g>'
          f'<g class="aur2"><circle cx="{w * .12:.0f}" cy="{h * .9:.0f}" r="{max(w, h) * .38:.0f}" fill="url(#au2)"/></g>')
    b += f'<rect x="0" y="0" width="{w}" height="4" fill="url(#g)"/>'
    b += text(x0, 52, f'{n} {ui(lang, "tech")}'.upper(), 18 if mobile else 13, a1, 800, spacing=2.4)
    for i, line in enumerate(title_lines):
        b += text(x0, 96 + i * 40, line, 33 if mobile else 31, t.text, 800)
    colors = {}
    for idx, (name, slug, color) in enumerate(items):
        r_, c_ = divmod(idx, cols)
        in_row = min(cols, n - r_ * cols)
        row_w = in_row * cell_w + (in_row - 1) * gap
        grid_w = cols * cell_w + (cols - 1) * gap
        sx = (w - (grid_w if mobile else row_w)) / 2
        cx_ = sx + c_ * (cell_w + gap) + cell_w / 2
        ty = head + r_ * cell_h + 8
        tx = cx_ - tile / 2
        ink = color or a1
        if luminance(ink) < .22:
            ink = t.text
        gid = 'h' + ink.strip('#')
        if gid not in colors:
            colors[gid] = radial(gid, ink, .5)
        tile_svg = (f'<circle cx="{cx_:.1f}" cy="{ty + tile / 2:.1f}" r="{tile * .78:.0f}" fill="url(#{gid})" opacity=".55"/>'
                    f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="{tile * .28:.0f}" fill="{t.ink}" fill-opacity=".9" '
                    f'stroke="{ink}" stroke-opacity=".55" stroke-width="1.5"/>')
        if slug:
            tile_svg += icon(slug, tx + tile * .24, ty + tile * .24, tile * .52, ink)
        else:
            mono = ''.join(p[0] for p in name.split()[:3]).upper() if ' ' in name else name[:3]
            tile_svg += text(cx_, ty + tile / 2 + 7, mono, 21 if len(mono) <= 2 else 18, ink, 800, anchor='middle')
        b += f'<g class="flt" style="animation-delay:-{(idx * .37) % 6:.2f}s">{tile_svg}</g>'
        b += (f'<rect class="live seq" style="animation-delay:{idx * step:.2f}s" x="{tx - 4:.1f}" y="{ty - 4}" width="{tile + 8}" height="{tile + 8}" '
              f'rx="{tile * .3:.0f}" fill="{ink}" fill-opacity=".16" stroke="{ink}" stroke-width="2.5"/>')
        label_size = 18 if mobile else 14
        parts = [name]
        if text_width(name, label_size, 600) > cell_w - 8 and ' ' in name:
            parts = name.split(' ', 1)
        for j, part in enumerate(parts):
            b += text(cx_, ty + tile + 26 + j * (label_size + 4), part, fit_text(part, label_size, cell_w - 6, 600), t.soft, 600, anchor='middle')
    b += '</g>'
    defs += ''.join(colors.values())
    names = ', '.join(i[0] for i in items)
    alt = f'{title} — {n} {ui(lang, "tech")}' if title else f'{n} {ui(lang, "tech")}'
    return document(w, h, alt, f'{alt}: {names}.', b, defs, motion), alt


# ---------------------------------------------------------------- timeline
def timeline(sec, t, lang, mobile, index=0):
    steps = [(loc(s.get('title'), lang), loc(s.get('text'), lang)) for s in sec.get('steps', [])]
    kicker = loc(sec.get('kicker'), lang) or f'{len(steps)} {ui(lang, "steps")}'
    n = len(steps)
    period = 2.4 * n
    colors = [t.accent(i) for i in range(n)]
    defs = (linear('bg', [(0, t.ink), (.6, t.mid), (1, t.deep)], x2=1, y2=1)
            + linear('rib', [(i / max(n - 1, 1), c) for i, c in enumerate(colors)], x2=0 if mobile else 1, y2=1 if mobile else 0)
            + radial('au', t.accent(index), .35) + ''.join(radial(f's{i}', c, .6) for i, c in enumerate(colors)))
    if mobile:
        w = 600
        pts, y = [], 150
        for title, about in steps:
            pts.append((80, y))
            y += 70 + len(wrap(about, 420, 20)) * 26 + 30
        h = y - 20
        path = f'M80 150V{pts[-1][1]}'
    else:
        w, h = 1200, 440
        gapx = (w - 260) / max(n - 1, 1)
        pts = [(130 + i * gapx, 170 if i % 2 == 0 else 236) for i in range(n)]
        path = f'M{pts[0][0]:.0f} {pts[0][1]}' + ''.join(
            f'C{a[0] + gapx * .47:.0f} {a[1]} {b_[0] - gapx * .47:.0f} {b_[1]} {b_[0]:.0f} {b_[1]}' for a, b_ in zip(pts, pts[1:]))
    motion = (f'.st{{animation:st {period:.1f}s ease-out infinite}}@keyframes st{{0%{{opacity:.95;transform:scale(1.25)}}20%{{opacity:.35;transform:scale(1)}}100%{{opacity:.35;transform:scale(1)}}}}'
              '.aur{animation:aur 30s ease-in-out infinite}@keyframes aur{50%{transform:translate(60px,-30px)}}')
    b = frame(w, h, 28) + '<g clip-path="url(#frame)">'
    b += f'<g class="aur"><circle cx="{w * .5:.0f}" cy="{h * .5:.0f}" r="{max(w, h) * .45:.0f}" fill="url(#au)"/></g>'
    b += text(32 if mobile else 40, 52, kicker.upper(), 18 if mobile else 13, t.soft, 800, spacing=2.4)
    b += f'<path d="{path}" fill="none" stroke="url(#rib)" stroke-width="10" stroke-opacity=".18" stroke-linecap="round"/>'
    b += f'<path d="{path}" fill="none" stroke="url(#rib)" stroke-width="2.5" stroke-linecap="round"/>'
    cw = (w - 260) / max(n - 1, 1) - 16 if not mobile else 420
    for i, ((x, y), (title, about)) in enumerate(zip(pts, steps)):
        col = colors[i]
        b += (f'<circle class="live st" style="animation-delay:{i * period * .8 / max(n - 1, 1):.2f}s;transform-box:fill-box;transform-origin:center" cx="{x:.0f}" cy="{y}" r="58" fill="url(#s{i})"/>'
              f'<circle class="still" cx="{x:.0f}" cy="{y}" r="58" fill="url(#s{i})" opacity=".35"/>'
              f'<circle cx="{x:.0f}" cy="{y}" r="34" fill="{t.ink}" stroke="{col}" stroke-width="2.5"/>')
        b += text(x, y + 8, f'{i + 1:02d}', 21, col, 800, anchor='middle')
        if mobile:
            b += text(140, y - 8, title, fit_text(title, 28, 420, 800), t.text, 800)
            for j, line in enumerate(wrap(about, 420, 20)):
                b += text(140, y + 24 + j * 26, line, 20, t.soft)
        else:
            ty = y + 72
            b += text(x, ty, title, fit_text(title, 21, cw, 800), t.text, 800, anchor='middle')
            for j, line in enumerate(wrap(about, cw, 15)[:4]):
                b += text(x, ty + 26 + j * 21, line, 15, t.soft, anchor='middle')
    b += (f'<g class="live"><g><circle r="18" fill="#fff" opacity=".18"/><circle r="6" fill="#fff"/>'
          f'<animateMotion dur="{period:.1f}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.8;1" calcMode="linear" path="{path}"/></g></g>')
    b += '</g>'
    alt = loc(sec.get('title'), lang) or kicker
    desc = '; '.join(f'{i + 1:02d} {a}: {d}' for i, (a, d) in enumerate(steps))
    return document(w, h, alt, desc, b, defs, motion), alt


# ---------------------------------------------------------------- highlights
def highlights(sec, t, lang, mobile, index=0):
    items = [(loc(m.get('value'), lang), loc(m.get('label'), lang)) for m in sec.get('items', [])][:4]
    n = len(items)
    w = 600 if mobile else 1200
    cols = 2 if mobile else n
    rows = math.ceil(n / cols)
    pad, gap = (24, 16) if mobile else (32, 20)
    cw = (w - 2 * pad - (cols - 1) * gap) / cols
    ch = 200 if mobile else 190
    h = pad * 2 + rows * ch + (rows - 1) * gap
    defs = linear('bg', [(0, t.night), (.6, t.mid), (1, t.deep)], x2=1, y2=1)
    b = frame(w, h, 28) + '<g clip-path="url(#frame)">'
    motion = (f'.pulse{{opacity:0;animation:pulse {n * 2.2:.1f}s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:0}}8%,24%{{opacity:1}}36%{{opacity:0}}}}'
              '.shine{animation:shine 9s ease-in-out infinite}@keyframes shine{0%,30%{transform:translateX(-200px)}70%,100%{transform:translateX(1400px)}}')
    for i, (value, label) in enumerate(items):
        a1, a2 = t.pair(index + i)
        defs += linear(f'v{i}', [(0, a1), (1, a2)]) + radial(f'gl{i}', a1, .45)
        r_, c_ = divmod(i, cols)
        x, y = pad + c_ * (cw + gap), pad + r_ * (ch + gap)
        b += (f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{ch}" rx="22" fill="{t.glass}" fill-opacity=".55" stroke="url(#v{i})" stroke-opacity=".6"/>'
              f'<circle cx="{x + cw * .85:.0f}" cy="{y + 20}" r="{ch * .6:.0f}" fill="url(#gl{i})"/>'
              f'<rect class="live pulse" style="animation-delay:{i * 2.2:.1f}s" x="{x - 2:.0f}" y="{y - 2}" width="{cw + 4:.0f}" height="{ch + 4}" rx="24" '
              f'fill="none" stroke="{a1}" stroke-width="3"/>')
        vs = display_fit(value, 54 if mobile else 60, cw - 48)
        b += display(value, x + 24, y + 30 + vs, vs, f'url(#v{i})')
        for j, line in enumerate(wrap(label, cw - 48, 18 if mobile else 17)[:3]):
            b += text(x + 24, y + 30 + vs + 40 + j * 25, line, 18 if mobile else 17, t.soft)
    b += f'<rect class="live shine" x="0" y="0" width="120" height="{h}" fill="#fff" opacity=".04" transform="skewX(-20)"/>'
    b += '</g>'
    alt = loc(sec.get('title'), lang) or ' · '.join(f'{v} {l}' for v, l in items)
    desc = '; '.join(f'{v} — {l}' for v, l in items)
    return document(w, h, alt, desc, b, defs, motion), alt


# ---------------------------------------------------------------- contact buttons
BRANDS = {'discord': '#7C8BFF', 'telegram': '#26A5E4', 'instagram': '#FF4F93', 'x': '#E7E9EA', 'youtube': '#FF4E45',
          'github': '#E6EDF3', 'twitch': '#A970FF', 'bluesky': '#1185FE', 'mastodon': '#8C8DFF', 'reddit': '#FF5700',
          'devdotto': '#E6EDF3', 'medium': '#E6EDF3', 'tiktok': '#25F4EE', 'kofi': '#FF6433', 'buymeacoffee': '#FFDD00',
          'patreon': '#FF6B57', 'stackoverflow': '#F58025', 'leetcode': '#FFA116', 'kaggle': '#20BEFF', 'hashnode': '#2962FF'}
LABELS = {'mail': {'en': 'EMAIL', 'bg': 'ИМЕЙЛ'}, 'web': {'en': 'WEBSITE', 'bg': 'САЙТ'}, 'linkedin': {'en': 'LINKEDIN'}}


def contact_glyph(kind, x, y, size, color):
    s = size / 24
    if kind in ICONS:
        return icon(kind, x, y, size, color)
    shape = {
        'mail': '<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M3 6.5l9 6.5 9-6.5"/>',
        'web': '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19"/>',
        'linkedin': '<rect x="2.5" y="2.5" width="19" height="19" rx="4"/><path d="M7.5 10.5v6M7.5 7.3v.2M11 16.5v-6m0 2.6c0-1.6 1-2.8 2.6-2.8s2.4 1.1 2.4 2.8v3.4"/>',
    }.get(kind, '<circle cx="12" cy="12" r="9"/>')
    return (f'<g transform="translate({x} {y}) scale({s:.3f})" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{shape}</g>')


def contact_button(button, t, lang, index=0):
    kind = button['kind']
    value = loc(button['value'], lang)
    label = loc(button.get('label'), lang) or loc(LABELS.get(kind), lang) or (ICONS[kind]['title'].upper() if kind in ICONS else kind.upper())
    col = button.get('color') or BRANDS.get(kind) or t.accent(index)
    h = 64
    w = round(84 + max(text_width(value, 18, 700), text_width(label, 12, 800) + len(label) * 2) + 26)
    defs = linear('bg', [(0, t.ink), (1, t.mid)], x2=1, y2=1) + linear('edge', [(0, col), (1, col, .35)])
    b = (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{h / 2 - 1:.0f}" fill="url(#bg)" stroke="url(#edge)" stroke-width="2"/>'
         f'<circle cx="33" cy="{h / 2}" r="21" fill="{col}" fill-opacity=".18"/>' + contact_glyph(kind, 21, h / 2 - 12, 24, col))
    b += f'<circle class="live ping" cx="33" cy="{h / 2}" r="21" fill="none" stroke="{col}" stroke-width="2"/>'
    b += text(66, 27, label, 12, col, 800, spacing=2)
    b += text(66, 48, value, 18, t.text, 700)
    motion = ('.ping{transform-box:fill-box;transform-origin:center;animation:ping 3.2s ease-out infinite}'
              f'@keyframes ping{{0%{{transform:scale(1);opacity:.7}}60%,100%{{transform:scale(1.5);opacity:0}}}}')
    alt = f'{label}: {value}'
    return document(w, h, alt, alt, b, defs, motion), alt


# ---------------------------------------------------------------- footer
def footer(sec, t, lang, mobile, index=0):
    words = loc(sec.get('words', []), lang)
    tagline = loc(sec.get('tagline'), lang)
    w = 600 if mobile else 1200
    size = 17
    widths = [text_width(word, size, 800) + len(word) * 2 + 40 for word in words]
    rows, row, row_w = [], [], 0
    for i, pw in enumerate(widths):
        if row and row_w + pw + 14 > w - 48:
            rows.append(row)
            row, row_w = [], 0
        row.append(i)
        row_w += pw + 14
    if row:
        rows.append(row)
    tag = []
    if tagline:
        tag = [tagline]
        if display_fit(tagline, 30, w - 60) < 22:
            tag = wrap(tagline, w - 60, 22, 800)
    fs = min([display_fit(line, 30 if not mobile else 28, w - 60) for line in tag] or [30])
    h = round(26 + len(rows) * 56 + (30 + len(tag) * 40 if tag else 0) + 20)
    defs = (linear('fb', [(0, t.ink), (.5, t.mid), (1, t.ink)]) + linear('hg', [(0, t.accent(0)), (.5, t.accent(1)), (1, t.accent(4))])
            + linear('sh', [(0, '#fff', 0), (.5, '#fff', .55), (1, '#fff', 0)]))
    b, y = f'<rect width="{w}" height="{h}" rx="26" fill="url(#fb)"/>', 26
    n = max(len(words), 1)
    motion = (f'.shn{{animation:shn {n * 1.4:.1f}s ease-in-out infinite}}@keyframes shn{{0%{{transform:translateX(-80px);opacity:0}}4%{{opacity:1}}'
              f'{100 / n:.0f}%{{transform:translateX(var(--d));opacity:0}}100%{{opacity:0}}}}')
    for row in rows:
        total = sum(widths[i] for i in row) + 14 * (len(row) - 1)
        x = (w - total) / 2
        for i in row:
            pw = widths[i]
            col = t.accent(index + i)
            b += f'<clipPath id="c{i}"><rect x="{x:.0f}" y="{y}" width="{pw:.0f}" height="42" rx="8"/></clipPath>'
            b += f'<rect x="{x:.0f}" y="{y}" width="{pw:.0f}" height="42" rx="8" fill="{col}" fill-opacity=".9"/>'
            b += (f'<g clip-path="url(#c{i})" class="live"><rect class="shn" style="--d:{pw + 80:.0f}px;animation-delay:{i * 1.4:.1f}s" '
                  f'x="{x:.0f}" y="{y}" width="60" height="42" fill="url(#sh)" transform="skewX(-18)"/></g>')
            ink = '#0B0B14' if luminance(col) > .55 else '#FFFFFF'
            b += text(x + pw / 2, y + 28, words[i], size, ink, 800, anchor='middle', spacing=2)
            x += pw + 14
        y += 56
    if tag:
        y += 30
        for i, line in enumerate(tag):
            b += display(line, w / 2, y + i * 40, fs, 'url(#hg)', anchor='middle')
    alt = tagline or ' · '.join(words)
    return document(w, h, alt, f'{" · ".join(words)}. {tagline}'.strip(), b, defs, motion), alt


# ---------------------------------------------------------------- language switch
def language_pill(code, active, t):
    label = code.upper()
    w, h = 64, 34
    col = t.accent(0)
    fill = f'fill="{col}"' if active else f'fill="{t.ink}" stroke="{col}" stroke-opacity=".6"'
    b = f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" {fill}/>'
    b += text(w / 2, 22.5, label, 14, '#FFFFFF' if active else t.soft, 800, anchor='middle', spacing=1.5)
    return document(w, h, label, label, b), label
