"""Checks that keep a profile safe to serve from GitHub.

GitHub renders README images through a sanitising proxy: scripts, remote
resources and web fonts are dropped, and a broken image looks unprofessional.
These checks catch that before a push.
"""
import re
from pathlib import Path

BANNED = ('<script', 'foreignObject', '@import', 'href="http', "href='http", 'url(http', '<iframe')
ASSET = re.compile(r'(?:src|srcset)="([^"]+)"')
MAX_BYTES = 1_000_000


def check_svg(path):
    problems = []
    content = Path(path).read_text(encoding='utf-8')
    name = Path(path).name
    for banned in BANNED:
        if banned in content:
            problems.append(f'{name}: contains {banned!r}, which GitHub strips or blocks')
    for href in re.findall(r'<image[^>]*\shref="([^"]{0,16})', content):
        if not href.startswith('data:image/'):
            problems.append(f'{name}: <image> must embed a data: URI')
    animated = '@keyframes' in content or '<animate' in content
    if animated and 'prefers-reduced-motion:no-preference' not in content:
        problems.append(f'{name}: animation must sit inside @media (prefers-reduced-motion: no-preference)')
    if '@keyframes' in content:
        outside = content.split('@media (prefers-reduced-motion:no-preference)')[0]
        if '@keyframes' in outside or re.search(r'animation:\s*[a-z]', outside):
            problems.append(f'{name}: animation declared outside the reduced-motion query')
    if '<title' not in content or '<desc' not in content:
        problems.append(f'{name}: needs <title> and <desc> for screen readers')
    if len(content.encode()) > MAX_BYTES:
        problems.append(f'{name}: {len(content.encode()) // 1024} KB is too heavy for a README image')
    return problems


def check_readme(path, root):
    problems = []
    text = Path(path).read_text(encoding='utf-8')
    for asset in ASSET.findall(text):
        if asset.startswith('http'):
            continue
        if not (Path(root) / asset).is_file():
            problems.append(f'{Path(path).name}: missing image {asset}')
    return problems


def lint(root, assets='assets/studio'):
    root = Path(root)
    problems = []
    for svg in sorted((root / assets).glob('*.svg')):
        problems += check_svg(svg)
    for readme in sorted(root.glob('README*.md')):
        problems += check_readme(readme, root)
    return problems
