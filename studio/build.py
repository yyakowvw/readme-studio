"""Turn a profile config into animated SVGs and one README per language."""
import json
from pathlib import Path

from . import components as comp
from .components import loc
from .style import Theme

SECTION_TYPES = {'hero', 'heading', 'divider', 'projects', 'stack', 'timeline', 'highlights', 'contact', 'footer', 'markdown'}


def load(path):
    path = Path(path)
    config = json.loads(path.read_text(encoding='utf-8'))
    errors = validate(config)
    if errors:
        raise SystemExit('profile config is invalid:\n  - ' + '\n  - '.join(errors))
    return config


def validate(config):
    errors = []
    langs = config.get('languages') or ['en']
    if not isinstance(langs, list) or not all(isinstance(x, str) and x.isalpha() for x in langs):
        errors.append('"languages" must be a list of language codes such as ["en", "bg"]')
    for i, sec in enumerate(config.get('sections', [])):
        kind = sec.get('type')
        if kind not in SECTION_TYPES:
            errors.append(f'sections[{i}]: unknown type {kind!r} (use one of {", ".join(sorted(SECTION_TYPES))})')
        if kind == 'hero' and not sec.get('headline'):
            errors.append(f'sections[{i}]: hero needs a "headline"')
        if kind == 'heading' and not sec.get('title'):
            errors.append(f'sections[{i}]: heading needs a "title"')
        if kind == 'projects' and not sec.get('items'):
            errors.append(f'sections[{i}]: projects needs "items"')
        if kind == 'stack' and not sec.get('items'):
            errors.append(f'sections[{i}]: stack needs "items"')
        if kind == 'timeline' and not 2 <= len(sec.get('steps', [])) <= 6:
            errors.append(f'sections[{i}]: timeline needs 2–6 "steps"')
        if kind == 'highlights' and not 1 <= len(sec.get('items', [])) <= 4:
            errors.append(f'sections[{i}]: highlights needs 1–4 "items"')
        if kind == 'contact':
            for j, button in enumerate(sec.get('buttons', [])):
                if not button.get('kind') or not button.get('value'):
                    errors.append(f'sections[{i}].buttons[{j}]: needs "kind" and "value"')
    if not config.get('sections'):
        errors.append('add at least one entry to "sections"')
    return errors


def readme_name(config, lang):
    first = (config.get('languages') or ['en'])[0]
    return 'README.md' if lang == first else f'README.{lang}.md'


def readme_link(config, lang):
    repo = config.get('repository')
    name = readme_name(config, lang)
    if not repo:
        return name
    owner = repo.split('/')[0]
    if name == 'README.md' and repo == f'{owner}/{owner}':
        return f'https://github.com/{owner}'
    return f'https://github.com/{repo}/blob/{config.get("branch", "main")}/{name}'


def picture(base, alt, href=None):
    alt = alt.replace('"', '&quot;')
    tag = (f'<picture>\n  <source media="(max-width: 600px)" srcset="{base}-mobile.svg">\n'
           f'  <img src="{base}.svg" width="100%" alt="{alt}">\n</picture>')
    if href:
        tag = f'<a href="{href}">\n{tag}\n</a>'
    return tag


def build(config_path, root=None):
    config = load(config_path)
    root = Path(root or Path(config_path).resolve().parent)
    out_dir = config.get('assets', 'assets/studio')
    target = root / out_dir
    target.mkdir(parents=True, exist_ok=True)
    theme = Theme(config.get('theme', 'aurora'), config.get('colors'))
    langs = config.get('languages') or ['en']
    written = []

    def save(name, svg):
        (target / name).write_text(svg, encoding='utf-8')
        written.append(name)
        return f'{out_dir}/{name}'

    def pair(fn, stem, lang, *args):
        desktop, alt = fn(*args, lang, False)
        mobile, _ = fn(*args, lang, True)
        save(f'{stem}-{lang}-mobile.svg', mobile)
        return save(f'{stem}-{lang}.svg', desktop)[:-4], alt

    readmes = {}
    for lang in langs:
        md = []
        if len(langs) > 1:
            switch = []
            for code in langs:
                svg, _ = comp.language_pill(code, code == lang, theme)
                src = save(f'lang-{code}-{"on" if code == lang else "off"}.svg', svg)
                switch.append(f'<a href="{readme_link(config, code)}"><img src="{src}" height="34" alt="{code.upper()}"></a>')
            md.append('<p align="right">\n' + '\n'.join(switch) + '\n</p>')
        counters = {}
        for i, sec in enumerate(config['sections']):
            kind = sec['type']
            n = counters.get(kind, 0)
            counters[kind] = n + 1
            stem = f'{i:02d}-{kind}'
            anchor = sec.get('anchor')
            if anchor:
                md.append(f'<a name="{anchor}"></a>')
            if kind == 'markdown':
                md.append(loc(sec.get('text'), lang).strip())
            elif kind == 'hero':
                base, alt = pair(comp.hero, stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'heading':
                base, alt = pair(lambda s, t, l, m: comp.heading(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'divider':
                base, alt = pair(lambda s, t, l, m: comp.divider(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'projects':
                for j, item in enumerate(sec['items']):
                    base, alt = pair(lambda s, t, l, m: comp.project(s, t, l, m, j), f'{stem}-{j + 1}', lang, item, theme)
                    md.append(picture(base, alt, item.get('url')))
                    extra = loc(item.get('markdown'), lang)
                    if extra:
                        md.append(extra.strip())
            elif kind == 'stack':
                base, alt = pair(lambda s, t, l, m: comp.stack(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'timeline':
                base, alt = pair(lambda s, t, l, m: comp.timeline(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'highlights':
                base, alt = pair(lambda s, t, l, m: comp.highlights(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'footer':
                base, alt = pair(lambda s, t, l, m: comp.footer(s, t, l, m, n), stem, lang, sec, theme)
                md.append(picture(base, alt))
            elif kind == 'contact':
                buttons = []
                for j, button in enumerate(sec.get('buttons', [])):
                    svg, alt = comp.contact_button(button, theme, lang, j)
                    src = save(f'{stem}-{button["kind"]}-{j + 1}-{lang}.svg', svg)
                    img = f'<img src="{src}" height="64" alt="{alt}">'
                    buttons.append(f'<a href="{button["href"]}">{img}</a>' if button.get('href') else img)
                md.append('<p align="center">\n' + '\n'.join(buttons) + '\n</p>')
        name = readme_name(config, lang)
        readmes[name] = '\n\n'.join(md) + '\n'
        if config.get('write_readme', True):
            (root / name).write_text(readmes[name], encoding='utf-8')
    stale = [p for p in target.glob('*.svg') if p.name not in set(written)]
    for path in stale:
        path.unlink()
    return {'assets': sorted(set(written)), 'readmes': readmes, 'removed': [p.name for p in stale]}
