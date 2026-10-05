#!/usr/bin/env python3
"""Rebuild everything this repository shows about itself.

  docs/assets/      visuals for README.md / README.bg.md (from docs/showcase.json)
  docs/themes/      one hero and one project card per built-in theme
  examples/         the demo profile, built exactly as a user would build theirs
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from studio import components as comp  # noqa: E402
from studio.build import build  # noqa: E402
from studio.style import THEMES, Theme  # noqa: E402

HERO = {'kicker': 'theme · {name}', 'headline': ['Your GitHub profile,', 'in motion.'],
        'lines': ['Pure SVG · zero JavaScript · respects reduced motion'], 'chips': ['Hero', 'Projects', 'Stack']}
CARD = {'name': 'Orbit CLI', 'kind': 'Developer tool', 'motif': 'scan', 'tags': ['TypeScript', 'Node.js'],
        'description': 'A command line that checks a project before it ships: tests, types, secrets and broken links in one pass.'}


def themes():
    out = ROOT / 'docs/themes'
    out.mkdir(parents=True, exist_ok=True)
    for name in THEMES:
        theme = Theme(name)
        hero = {**HERO, 'kicker': HERO['kicker'].format(name=name)}
        (out / f'{name}.svg').write_text(comp.hero(hero, theme, 'en', False)[0])
        (out / f'{name}-project.svg').write_text(comp.project(CARD, theme, 'en', False)[0])
    return len(THEMES)


if __name__ == '__main__':
    docs = build(ROOT / 'docs/showcase.json')
    example = build(ROOT / 'examples/profile.json')
    print(f'docs: {len(docs["assets"])} SVGs · examples: {len(example["assets"])} SVGs · themes: {themes()}')
