"""Run from the repository root: python -m unittest discover tests"""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from studio import components as comp  # noqa: E402
from studio.build import build, validate  # noqa: E402
from studio.lint import check_svg, lint  # noqa: E402
from studio.style import THEMES, Theme, text_width  # noqa: E402
from studio.typeset import measure  # noqa: E402

EXAMPLE = json.loads((ROOT / 'examples/profile.json').read_text())


def neutral(path):
    return re.sub(r'-(en|bg)(?=[-.])', '-XX', path)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        shutil.copy(ROOT / 'examples/profile.json', cls.tmp / 'profile.json')
        cls.result = build(cls.tmp / 'profile.json')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_example_builds_clean(self):
        self.assertEqual(lint(self.tmp), [])

    def test_one_readme_per_language(self):
        self.assertEqual(sorted(self.result['readmes']), ['README.bg.md', 'README.md'])

    def test_languages_share_the_same_visual_scope(self):
        en, bg = (self.result['readmes'][n] for n in ('README.md', 'README.bg.md'))
        assets = re.compile(r'(?:src|srcset)="([^"]+)"')
        strip = lambda md: [neutral(a) for a in assets.findall(md) if 'lang-' not in a]  # noqa: E731
        self.assertEqual(strip(en), strip(bg))

    def test_every_picture_has_a_mobile_variant(self):
        for md in self.result['readmes'].values():
            self.assertEqual(md.count('<picture>'), md.count('-mobile.svg"'))

    def test_stale_assets_are_removed(self):
        stale = self.tmp / 'assets/studio/99-old-en.svg'
        stale.write_text('<svg/>')
        build(self.tmp / 'profile.json')
        self.assertFalse(stale.exists())


class ComponentTests(unittest.TestCase):
    def test_every_theme_renders_every_component(self):
        sections = {s['type']: s for s in EXAMPLE['sections']}
        for name in THEMES:
            theme = Theme(name)
            for lang in ('en', 'bg'):
                for mobile in (False, True):
                    svgs = [comp.hero(sections['hero'], theme, lang, mobile),
                            comp.heading(sections['heading'], theme, lang, mobile),
                            comp.divider({}, theme, lang, mobile, 2),
                            comp.project(sections['projects']['items'][0], theme, lang, mobile),
                            comp.stack(sections['stack'], theme, lang, mobile),
                            comp.timeline(sections['timeline'], theme, lang, mobile),
                            comp.highlights(sections['highlights'], theme, lang, mobile),
                            comp.footer(sections['footer'], theme, lang, mobile)]
                    for svg, alt in svgs:
                        self.assertTrue(alt)
                        self.assertTrue(svg.startswith('<svg'))
                        self.assertEqual(self._problems(svg), [], (name, lang, mobile, alt))

    def _problems(self, svg):
        with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as handle:
            handle.write(svg)
        try:
            return check_svg(handle.name)
        finally:
            Path(handle.name).unlink()

    def test_widths_match_the_declared_canvas(self):
        hero = next(s for s in EXAMPLE['sections'] if s['type'] == 'hero')
        for mobile, width in ((False, 1200), (True, 600)):
            svg, _ = comp.hero(hero, Theme(), 'en', mobile)
            self.assertIn(f'width="{width}"', svg[:200])

    def test_long_headlines_shrink_to_fit(self):
        long = 'An extraordinarily long headline that would never fit'
        size = comp.display_fit(long, 56, 640)
        self.assertLessEqual(measure(long, size), 640)

    def test_cyrillic_is_outlined(self):
        self.assertGreater(measure('Здравейте', 40), 100)

    def test_unknown_glyphs_fall_back_to_text(self):
        self.assertIn('<text', comp.display('漢字', 0, 0, 20, '#fff'))

    def test_tech_resolution(self):
        self.assertEqual(comp.resolve_tech('react')[1], 'react')
        self.assertEqual(comp.resolve_tech('Node.js')[1], 'nodedotjs')
        self.assertEqual(comp.resolve_tech('My Engine'), ('My Engine', None, None))
        self.assertEqual(comp.resolve_tech({'name': 'Lab', 'color': '#123456'})[2], '#123456')

    def test_localised_values(self):
        self.assertEqual(comp.loc({'en': 'Hi', 'bg': 'Здрасти'}, 'bg'), 'Здрасти')
        self.assertEqual(comp.loc({'en': 'Hi'}, 'de'), 'Hi')
        self.assertEqual(comp.loc('Same', 'bg'), 'Same')

    def test_text_estimate_is_generous(self):
        self.assertGreater(text_width('Hello world', 20), 100)


class ConfigTests(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validate(EXAMPLE), [])

    def test_reports_helpful_errors(self):
        errors = validate({'sections': [{'type': 'banner'}, {'type': 'hero'}, {'type': 'timeline', 'steps': [{}]}]})
        self.assertEqual(len(errors), 3)
        self.assertIn('unknown type', errors[0])

    def test_unknown_theme(self):
        with self.assertRaises(ValueError):
            Theme('neon-pink')


if __name__ == '__main__':
    unittest.main()


class WizardTests(unittest.TestCase):
    ANSWERS = ['1', 'demo-user', 'Demo Person', 'web developer', 'I build things', 'that work.', 'Web · bots', '',
               'Shop', 'Online store', 'A fast store.', 'React, Stripe', 'shop.example.com', '',
               'react, python, UnknownTool', 'n', 'demo@example.com', 'demo.dev', '', '', '', '', '', '', '2']

    def test_answers_become_a_valid_profile(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            run = subprocess.run([sys.executable, '-m', 'studio', 'init', '--ui', 'en', '--dir', tmp, '--no-open', '--no-publish'],
                                 input='\n'.join(self.ANSWERS) + '\n', capture_output=True, text=True, cwd=ROOT, timeout=120)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            config = json.loads((Path(tmp) / 'profile.json').read_text())
            self.assertEqual(validate(config), [])
            self.assertEqual(config['theme'], 'sunset')
            self.assertEqual(config['repository'], 'demo-user/demo-user')
            kinds = [s['type'] for s in config['sections']]
            self.assertIn('projects', kinds)
            self.assertNotIn('timeline', kinds)
            project = next(s for s in config['sections'] if s['type'] == 'projects')['items'][0]
            self.assertEqual(project['url'], 'https://shop.example.com')
            self.assertTrue((Path(tmp) / 'README.md').is_file())
            self.assertTrue((Path(tmp) / '.github/workflows/profile.yml').is_file())
            self.assertEqual(lint(tmp), [])
