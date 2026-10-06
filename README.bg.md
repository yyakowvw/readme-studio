<p align="right">
<a href="README.md"><img src="docs/assets/lang-en-off.svg" height="34" alt="EN"></a>
<a href="README.bg.md"><img src="docs/assets/lang-bg-on.svg" height="34" alt="BG"></a>
</p>

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/00-hero-bg-mobile.svg">
  <img src="docs/assets/00-hero-bg.svg" width="100%" alt="readme-studio — вашият GitHub профил, в движение. Един JSON файл става анимиран двуезичен README. Чист SVG, нула JavaScript, уважава намаленото движение.">
</picture>

**readme-studio** превръща един JSON файл в анимиран двуезичен README за GitHub профил. Включва въвеждащ блок с
орбитираща светлина, карти на проекти, решетки с технологии, времеви линии, акцентни числа, бутони за контакт и
разделители. Всяко изображение е самостоятелен SVG, който работи в защитения преглед на GitHub. При разглеждане не се
зарежда нищо външно и не се изпълнява JavaScript.

**[Вижте демо профила →](examples/README.bg.md)** · **[English →](README.md)**

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/01-highlights-bg-mobile.svg">
  <img src="docs/assets/01-highlights-bg.svg" width="100%" alt="9 анимирани компонента, 18 вградени теми, 174 вградени икони на марки, 0 външни заявки при разглеждане.">
</picture>

<img src="docs/video/demo-bg.webp" width="100%" alt="60-секундно демо: една команда в терминала, няколко отговора и готов анимиран GitHub профил.">

<p align="center"><sub>▶ <b>60-секундно демо</b>: една команда, няколко отговора и готов анимиран профил.</sub></p>

## Бърз старт

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/02-timeline-bg-mobile.svg">
  <img src="docs/assets/02-timeline-bg.svg" width="100%" alt="Четири стъпки: копирайте examples/profile.json, редактирайте текста, проектите, технологиите и темата, изградете с python -m studio build, публикувайте или оставете GitHub Action да го направи.">
</picture>

### ⚡ Най-бързо: една команда, без код

**macOS / Linux**: поставете това в Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/yyakowvw/readme-studio/main/install.sh | bash
```

**Windows**: [изтеглете ZIP файла](https://github.com/yyakowvw/readme-studio/archive/refs/heads/main.zip), разархивирайте го и щракнете два пъти върху **`setup.bat`**.
**macOS без Terminal**: изтеглете ZIP файла и щракнете два пъти върху **`Setup Profile.command`**.

Настройката ви задава няколко въпроса (на български или английски): име, заглавие, проекти, технологии, контакти и тема. След това:

1. създава всички анимирани изображения и вашия `README.md` (и `README.bg.md`, ако искате два езика);
2. отваря преглед в браузъра;
3. публикува в `github.com/<вие>/<вие>`, ако потвърдите (с GitHub CLI, ако е инсталиран, иначе с `git`);
4. добавя GitHub Action, така че по-късните промени в `profile.json` обновяват профила сами.

За промени по-късно пуснете същата команда отново. Предишните отговори са попълнени.

### Вариант А: GitHub Action (без нищо на компютъра)

1. В профилното си хранилище (`<потребител>/<потребител>`) добавете [`examples/profile.json`](examples/profile.json) като `profile.json` и го редактирайте.
2. Добавете `.github/workflows/profile.yml`:

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

При всяка промяна на `profile.json` изображенията и README се обновяват автоматично и се записват обратно в хранилището.

### Вариант Б: на вашия компютър

```bash
git clone https://github.com/yyakowvw/readme-studio
cd readme-studio
pip install -r requirements.txt          # само fontTools
cp examples/profile.json ~/my-profile/profile.json
python -m studio build ~/my-profile/profile.json
```

Резултат: `assets/studio/*.svg`, `README.md` и по един `README.<език>.md` за всеки допълнителен език, до вашия конфигурационен файл.

## 🎨 Направете го ваш

Настройката не ви налага нищо:

- **Всеки текст се редактира.** Всеки въпрос показва предложение: Enter го запазва, можете да напишете свой текст, а `-` премахва елемента напълно.
- **Изберете какво да има.** Включвате и изключвате секции: въвеждащ банер, за мен, проекти, технологии, числа, как работя, бутони за контакт, финален банер, разделители и превключвател на езика. Украсите на въвеждащия банер (планети, светеща мрежа, звезди, светлинен лъч, сияние, светеща линия) се махат поотделно.
- **Всякакви цветове.** Изберете една от 18 теми, съчетайте я с един от 8 фона, напишете свои цветове с име (`розов, тюркоаз, златен`) или hex (`#FACC15`), или пускайте случайни палитри, докато ви хареса.

Пуснете същата команда отново, когато искате промяна. Всички предишни отговори са попълнени.

## Теми

18 теми, 8 фона (`midnight`, `black`, `navy`, `forest`, `wine`, `plum`, `slate`, `espresso`) и всякакви цветове по ваш избор:

```json
"theme": "neon",
"colors": {"background": "navy", "accents": ["розов", "тюркоаз", "#FACC15"]}
```

| **aurora** | **sunset** | **ocean** |
| --- | --- | --- |
| <img src="docs/themes/aurora.svg" alt="Тема aurora"> | <img src="docs/themes/sunset.svg" alt="Тема sunset"> | <img src="docs/themes/ocean.svg" alt="Тема ocean"> |
| **matrix** | **neon** | **candy** |
| <img src="docs/themes/matrix.svg" alt="Тема matrix"> | <img src="docs/themes/neon.svg" alt="Тема neon"> | <img src="docs/themes/candy.svg" alt="Тема candy"> |
| **rose** | **forest** | **ice** |
| <img src="docs/themes/rose.svg" alt="Тема rose"> | <img src="docs/themes/forest.svg" alt="Тема forest"> | <img src="docs/themes/ice.svg" alt="Тема ice"> |
| **ember** | **gold** | **mono** |
| <img src="docs/themes/ember.svg" alt="Тема ember"> | <img src="docs/themes/gold.svg" alt="Тема gold"> | <img src="docs/themes/mono.svg" alt="Тема mono"> |
| **cyber** | **lavender** | **coral** |
| <img src="docs/themes/cyber.svg" alt="Тема cyber"> | <img src="docs/themes/lavender.svg" alt="Тема lavender"> | <img src="docs/themes/coral.svg" alt="Тема coral"> |
| **galaxy** | **mint** | **retro** |
| <img src="docs/themes/galaxy.svg" alt="Тема galaxy"> | <img src="docs/themes/mint.svg" alt="Тема mint"> | <img src="docs/themes/retro.svg" alt="Тема retro"> |

## Компоненти

`sections` е подреден списък. README следва същия ред.

| `type` | Какво рисува | Основни полета |
| --- | --- | --- |
| `hero` | Име, заглавие в контури, орбити, перспективен под, етикети | `kicker`, `headline` (1–2 реда), `lines`, `chips` (≤ 4) |
| `heading` | Заглавие на секция с градиент и движеща се линия | `kicker`, `title`, `subtitle`, `anchor` |
| `projects` | По една карта с връзка за всеки проект, с анимиран мотив | `items[]`: `name`, `kind`, `description`, `tags`, `motif` (`scan`, `network`, `tree`, `hex`, `page`), `url`, `markdown` |
| `stack` | Решетка с технологии и икони в цветовете на марката | `title`, `items`: имена на икони (`"react"`), заглавия (`"Node.js"`) или `{"name", "icon", "color"}` |
| `timeline` | 2–6 стъпки по светеща пътека | `kicker`, `steps[]`: `title`, `text` |
| `highlights` | 1–4 големи числа | `items[]`: `value`, `label` |
| `divider` | Разделител: `waves`, `beads`, `circuit`, `constellation`, `sunrise` | `motif` |
| `contact` | Бутони: `mail`, `web`, `linkedin` или всяка вградена икона (`discord`, `github`, `telegram`, `instagram`, `x`, `youtube`…) | `buttons[]`: `kind`, `value`, `href`, `label`, `color` |
| `footer` | Блестящи думи и мото | `words`, `tagline` |
| `markdown` | Ваш Markdown между изображенията | `text` |

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/03-stack-bg-mobile.svg">
  <img src="docs/assets/03-stack-bg.svg" width="100%" alt="Част от 174-те вградени икони: TypeScript, Python, Rust, Go, Swift, Kotlin, React, Svelte, Next.js, Vue.js, Node.js, Deno, PostgreSQL, Supabase, Docker, Kubernetes, GitHub Actions, Cloudflare, Unity, Godot Engine, FiveM, discord.js, Figma, Anthropic.">
</picture>

`python -m studio themes` показва темите. Пълният списък с икони е в [`studio/data/icons.json`](studio/data/icons.json).
Непознатите имена получават плочка с инициали.

## Само истина

Профилът е първото впечатление, затова нека е вярно. В конфигурацията слагайте само реални проекти, числа и умения.
Демо профилът е измислен човек: сменете всяка дума, преди да публикувате.

## Разработка

```bash
python -m unittest discover tests     # 20 теста
python scripts/showcase.py            # обновява docs/ и examples/
```

CI пуска тестовете при всяка промяна и спира, ако записаните SVG файлове не могат да се получат отново от конфигурациите.
Приносът е добре дошъл, вижте [CONTRIBUTING.md](CONTRIBUTING.md).

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/05-footer-bg-mobile.svg">
  <img src="docs/assets/05-footer-bg.svg" width="100%" alt="SVG · CSS движение · двуезично · достъпно · MIT. Направено, за да се копира.">
</picture>

<sub>Код: MIT © Yavor Yakow ([@yyakowvw](https://github.com/yyakowvw)). Шрифтът Unbounded е под лиценза SIL Open Font License 1.1 (`fonts/unbounded/OFL.txt`).
Иконите на марки са от [Simple Icons](https://simpleicons.org) (CC0 1.0) и остават търговски марки на собствениците си.</sub>
