<p align="right">
<a href="README.md"><img src="docs/assets/lang-en-on.svg" height="34" alt="EN"></a>
<a href="README.bg.md"><img src="docs/assets/lang-bg-off.svg" height="34" alt="BG"></a>
</p>

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/00-hero-en-mobile.svg">
  <img src="docs/assets/00-hero-en.svg" width="100%" alt="readme-studio — your GitHub profile, in motion. One JSON file becomes an animated, bilingual README. Pure SVG, zero JavaScript, respects reduced motion.">
</picture>

**readme-studio** turns one JSON file into an animated, bilingual GitHub profile README: a hero with orbiting light,
project cards, technology grids, timelines, highlight numbers, contact buttons and section dividers. Every visual is
a self-contained SVG that works inside GitHub's image sanitiser. Nothing loads at view time and no JavaScript runs.

**[See the demo profile →](examples/README.md)** · **[Български →](README.bg.md)**

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/01-highlights-en-mobile.svg">
  <img src="docs/assets/01-highlights-en.svg" width="100%" alt="9 animated components, 4 built-in themes, 174 bundled brand icons, 0 external requests at view time.">
</picture>

## Why it looks the same everywhere

GitHub serves README images through a proxy that strips scripts, web fonts and remote resources. Most animated READMEs
break against that, or depend on a third-party server that eventually goes down. readme-studio is built around those limits:

| Problem | What readme-studio does |
| --- | --- |
| Web fonts are blocked | Headlines are **outlined into SVG paths** with [Unbounded](https://github.com/googlefonts/unbounded) (latin + cyrillic). The text is still in `<title>`/`<desc>` and the alt text. |
| Remote widgets go down | **Zero network requests.** Every icon, gradient and animation sits inside the file. |
| Motion can be uncomfortable | All animation lives inside `@media (prefers-reduced-motion: no-preference)`. Turn motion off in your OS and every image shows a complete static composition. |
| Phones get tiny text | Every component has a 600 px **mobile variant**, swapped in with `<picture>`. |
| One language is not enough | Any string can be `{"en": "...", "bg": "..."}`. You get `README.md` plus `README.<lang>.md` with a language switch. |
| Broken images look amateur | `python -m studio lint` checks for missing files, scripts, remote links, oversized SVGs and animation outside the reduced-motion query. |

## Quick start

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/02-timeline-en-mobile.svg">
  <img src="docs/assets/02-timeline-en.svg" width="100%" alt="Four steps: copy examples/profile.json, edit your text, projects, stack and theme, build with python -m studio build, push or let the GitHub Action rebuild it.">
</picture>

### Option A: GitHub Action (no local setup)

1. In your profile repository (`<username>/<username>`), add [`examples/profile.json`](examples/profile.json) as `profile.json` and edit it.
2. Add `.github/workflows/profile.yml`:

```yaml
name: Build profile
on:
  push:
    paths: [profile.json]
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: yyakowvw/readme-studio@main
        with:
          config: profile.json
```

Every push to `profile.json` rebuilds the SVGs and your README and commits them back.

### Option B: on your computer

```bash
git clone https://github.com/yyakowvw/readme-studio
cd readme-studio
pip install -r requirements.txt          # only fontTools
cp examples/profile.json ~/my-profile/profile.json
python -m studio build ~/my-profile/profile.json
```

Output: `assets/studio/*.svg`, `README.md` and one `README.<lang>.md` per extra language, next to your config.

## Themes

`"theme": "aurora" | "sunset" | "ocean" | "matrix"`. You can override any colour with `"colors": {"accents": [...]}`.

| aurora | sunset |
| --- | --- |
| <img src="docs/themes/aurora.svg" alt="Aurora theme hero"> | <img src="docs/themes/sunset.svg" alt="Sunset theme hero"> |
| <img src="docs/themes/aurora-project.svg" alt="Aurora theme project card"> | <img src="docs/themes/sunset-project.svg" alt="Sunset theme project card"> |
| **ocean** | **matrix** |
| <img src="docs/themes/ocean.svg" alt="Ocean theme hero"> | <img src="docs/themes/matrix.svg" alt="Matrix theme hero"> |
| <img src="docs/themes/ocean-project.svg" alt="Ocean theme project card"> | <img src="docs/themes/matrix-project.svg" alt="Matrix theme project card"> |

## Components

`sections` is an ordered list. The README follows the same order.

| `type` | What it draws | Main fields |
| --- | --- | --- |
| `hero` | Name, outlined headline, orbit system, perspective floor, chips | `kicker`, `headline` (1–2 lines), `lines`, `chips` (≤ 4) |
| `heading` | Section title with a gradient and a sweeping underline | `kicker`, `title`, `subtitle`, `anchor` |
| `projects` | One linked card per project with an animated motif | `items[]`: `name`, `kind`, `description`, `tags`, `motif` (`scan`, `network`, `tree`, `hex`, `page`), `url`, `markdown` |
| `stack` | Technology grid with brand-coloured icons | `title`, `items`: icon slugs (`"react"`), names (`"Node.js"`) or `{"name", "icon", "color"}` |
| `timeline` | 2–6 steps along a glowing path | `kicker`, `steps[]`: `title`, `text` |
| `highlights` | 1–4 big numbers | `items[]`: `value`, `label` |
| `divider` | Chapter break: `waves`, `beads`, `circuit`, `constellation`, `sunrise` | `motif` |
| `contact` | Pill buttons: `mail`, `web`, `linkedin`, or any bundled icon (`discord`, `github`, `telegram`, `instagram`, `x`, `youtube`…) | `buttons[]`: `kind`, `value`, `href`, `label`, `color` |
| `footer` | Shimmering word chips and a tagline | `words`, `tagline` |
| `markdown` | Your own Markdown between visuals | `text` |

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/03-stack-en-mobile.svg">
  <img src="docs/assets/03-stack-en.svg" width="100%" alt="A taste of the 174 bundled brand icons: TypeScript, Python, Rust, Go, Swift, Kotlin, React, Svelte, Next.js, Vue.js, Node.js, Deno, PostgreSQL, Supabase, Docker, Kubernetes, GitHub Actions, Cloudflare, Unity, Godot Engine, FiveM, discord.js, Figma, Anthropic.">
</picture>

Run `python -m studio themes` to list themes. The full icon list is in [`studio/data/icons.json`](studio/data/icons.json).
Unknown names fall back to a monogram tile.

## Keep it honest

A profile is a first impression, so make it a true one. Put real projects, real numbers and real skills in the config.
The demo profile is a fictional person, so replace every word of it before you publish.

## Development

```bash
python -m unittest discover tests     # 16 tests
python scripts/showcase.py            # rebuild docs/ and examples/
```

CI runs the tests on every push and fails if the committed SVGs are not reproducible from the configs.
Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/05-footer-en-mobile.svg">
  <img src="docs/assets/05-footer-en.svg" width="100%" alt="SVG · CSS motion · bilingual · accessible · MIT. Made to be forked.">
</picture>

<sub>Code: MIT © Yavor Yakow ([@yyakowvw](https://github.com/yyakowvw)). The Unbounded typeface is licensed under the SIL Open Font License 1.1 (`fonts/unbounded/OFL.txt`).
Brand icons come from [Simple Icons](https://simpleicons.org) (CC0 1.0) and remain trademarks of their owners.</sub>
