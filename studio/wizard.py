"""Interactive setup: answer questions in the terminal, get a finished profile.

  python -m studio init            ask everything, build, preview, publish
  python -m studio init --dir DIR  where the profile repository lives

Nothing here needs editing code: the answers are saved to profile.json, the
visuals and README files are built, a local preview opens in the browser, and
the result can be pushed to github.com/<username>/<username> in one step.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from .build import build
from .components import ICONS, resolve_tech
from .lint import lint
from .style import BACKGROUNDS, PRESETS, THEMES, parse_color, random_palette

COLOR = sys.stdout.isatty() and not os.environ.get('NO_COLOR')


def paint(code, value):
    return f'\033[{code}m{value}\033[0m' if COLOR else value


def swatch(color):
    if not COLOR:
        return color
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return f'\033[48;2;{r};{g};{b}m   \033[0m'


T = {
    'en': {
        'welcome': 'readme-studio · design your animated GitHub profile',
        'intro': 'Enter = keep the suggestion in [brackets] · "-" = leave it out · or type your own text.',
        'langs': 'Profile languages (1 English · 2 English + Bulgarian · 3 Bulgarian + English)',
        'sections': 'What should your profile contain?', 'toggle': 'Type numbers to switch items on/off (e.g. "3 5"), Enter to continue',
        'sec': {'hero': 'Intro banner', 'about': 'About me', 'work': 'Projects', 'stack': 'Technologies', 'numbers': 'Numbers',
                'process': 'How I work', 'contact': 'Contact buttons', 'footer': 'Closing banner', 'dividers': 'Dividers between sections',
                'switch': 'Language switch'},
        'decor': 'Intro banner decorations',
        'dec': {'orbit': 'Orbiting planets', 'floor': 'Glowing grid floor', 'stars': 'Stars', 'beam': 'Light sweep',
                'glow': 'Colour glow', 'bar': 'Bottom light bar'},
        'user': 'GitHub username', 'name': 'Your name', 'role': 'What you do (e.g. full-stack developer)',
        'part': '── {name} ──', 'kicker': 'Small label above the title', 'title': 'Section title',
        'h_kicker': 'Small label at the top', 'head1': 'Headline, line 1', 'head2': 'Headline, line 2',
        'line': 'One line under the headline', 'chips': 'Labels in the banner, comma separated',
        'about_head': 'Greeting heading', 'about_text': 'A short paragraph about you',
        'projects': 'Projects — leave the name empty when you are done',
        'p_name': 'Project name', 'p_kind': 'Type (e.g. web app, Discord bot)', 'p_desc': 'One-sentence description',
        'p_tags': 'Technologies, comma separated', 'p_url': 'Link',
        'panel': 'Title of the technology panel', 'count': 'Small label on the panel (e.g. "16 technologies")',
        'stack': 'Your technologies, comma separated', 'stack_hint': 'Icons exist for: {sample} … ({n} in total)',
        'unknown': 'No icon for {names} — initials will be shown.',
        'numbers': 'Up to 4 numbers — leave the number empty when you are done', 'n_value': 'Number (e.g. 120+)', 'n_label': 'What it counts',
        'steps': 'Steps — Enter keeps a step, "-" removes it', 'step_title': 'Step {i} title', 'step_text': 'Step {i} text',
        'more': 'Add another step (title, empty = no)', 'few_steps': 'A timeline needs at least 2 steps — it was left out.',
        'contact': 'Contacts — leave empty to skip', 'label': 'Button label',
        'email': 'Email', 'discord': 'Discord username', 'website': 'Website', 'linkedin': 'LinkedIn URL',
        'x': 'X (Twitter) handle', 'telegram': 'Telegram username', 'instagram': 'Instagram handle', 'youtube': 'YouTube channel URL',
        'github': 'GitHub link button (your username)',
        'words': 'Word badges in the closing banner, comma separated', 'tagline': 'Closing sentence',
        'colors': 'Colours', 'themes_help': 'Pick a number or name · r = random palette · c = your own colours',
        'theme': 'Theme', 'random_ok': 'Keep this palette?', 'custom': 'Your colours: 1–5 names or #hex, comma separated (e.g. pink, cyan, #FACC15)',
        'bad_color': 'Not a colour: {v}', 'background': 'Background (Enter = the theme\'s own)',
        'translate': 'In {lang}', 'same': 'Enter = same as above',
        'dir': 'Folder for your profile repository',
        'building': 'Building your profile…', 'built': 'Built {n} images and {readmes}.',
        'lint_ok': 'Every image passes the GitHub checks.', 'preview': 'Opening a preview in your browser…',
        'publish': 'Publish to github.com/{user}/{user} now?', 'published': 'Published! Open https://github.com/{user}',
        'no_gh': 'To publish, create the repository {user}/{user} on GitHub (public, empty), then run:',
        'later': 'Change anything later with the same command — your answers are remembered.',
        'yn': '[Y/n]', 'ny': '[y/N]',
        'steps_default': [('Discover', 'Goals, users and constraints'), ('Design', 'Interface, architecture and scope'),
                          ('Build', 'Features, integrations and tests'), ('Launch', 'Deploy, document, improve')],
        'heads': {'work': ('Selected work', "Things I've built"), 'stack': ('Technology', 'Tools I work with'),
                  'numbers': ('In numbers', 'What I bring'), 'process': ('Process', 'How a project moves'),
                  'contact': ('Contact', "Let's talk")},
        'stack_title': 'Daily drivers', 'hi': '👋 Hi, I\'m {name}', 'tech_count': '{n} technologies',
    },
    'bg': {
        'welcome': 'readme-studio · създайте анимиран GitHub профил',
        'intro': 'Enter = запазва предложението в [скоби] · „-“ = премахва го · или напишете свой текст.',
        'langs': 'Езици на профила (1 английски · 2 английски + български · 3 български + английски)',
        'sections': 'Какво да съдържа профилът?', 'toggle': 'Напишете номера, за да включите/изключите (напр. „3 5“), Enter за продължаване',
        'sec': {'hero': 'Въвеждащ банер', 'about': 'За мен', 'work': 'Проекти', 'stack': 'Технологии', 'numbers': 'Числа',
                'process': 'Как работя', 'contact': 'Бутони за контакт', 'footer': 'Финален банер', 'dividers': 'Разделители между секциите',
                'switch': 'Превключвател на езика'},
        'decor': 'Украси на въвеждащия банер',
        'dec': {'orbit': 'Планети в орбита', 'floor': 'Светеща мрежа отдолу', 'stars': 'Звезди', 'beam': 'Светлинен лъч',
                'glow': 'Цветно сияние', 'bar': 'Светеща линия отдолу'},
        'user': 'GitHub потребителско име', 'name': 'Вашето име', 'role': 'С какво се занимавате (напр. full-stack разработчик)',
        'part': '── {name} ──', 'kicker': 'Малък надпис над заглавието', 'title': 'Заглавие на секцията',
        'h_kicker': 'Малък надпис най-горе', 'head1': 'Заглавие, ред 1', 'head2': 'Заглавие, ред 2',
        'line': 'Един ред под заглавието', 'chips': 'Етикети в банера, разделени със запетая',
        'about_head': 'Заглавие-поздрав', 'about_text': 'Кратък текст за вас',
        'projects': 'Проекти — оставете името празно, когато приключите',
        'p_name': 'Име на проекта', 'p_kind': 'Вид (напр. уеб приложение, Discord бот)', 'p_desc': 'Описание в едно изречение',
        'p_tags': 'Технологии, разделени със запетая', 'p_url': 'Връзка',
        'panel': 'Заглавие на панела с технологии', 'count': 'Малък надпис на панела (напр. „16 технологии“)',
        'stack': 'Вашите технологии, разделени със запетая', 'stack_hint': 'Има икони за: {sample} … (общо {n})',
        'unknown': 'Няма икона за {names} — ще се покажат инициали.',
        'numbers': 'До 4 числа — оставете числото празно, когато приключите', 'n_value': 'Число (напр. 120+)', 'n_label': 'Какво брои',
        'steps': 'Стъпки — Enter запазва стъпката, „-“ я премахва', 'step_title': 'Стъпка {i}, заглавие', 'step_text': 'Стъпка {i}, текст',
        'more': 'Още една стъпка (заглавие, празно = не)', 'few_steps': 'Времевата линия иска поне 2 стъпки — пропусната е.',
        'contact': 'Контакти — оставете празно, за да пропуснете', 'label': 'Надпис на бутона',
        'email': 'Имейл', 'discord': 'Discord потребител', 'website': 'Сайт', 'linkedin': 'LinkedIn адрес',
        'x': 'X (Twitter) профил', 'telegram': 'Telegram потребител', 'instagram': 'Instagram профил', 'youtube': 'YouTube канал (адрес)',
        'github': 'Бутон към GitHub (потребителско име)',
        'words': 'Думи-етикети във финалния банер, разделени със запетая', 'tagline': 'Финално изречение',
        'colors': 'Цветове', 'themes_help': 'Номер или име · r = случайна палитра · c = ваши цветове',
        'theme': 'Тема', 'random_ok': 'Да запазя ли тази палитра?', 'custom': 'Вашите цветове: 1–5 имена или #hex, със запетая (напр. розов, тюркоаз, #FACC15)',
        'bad_color': 'Не е цвят: {v}', 'background': 'Фон (Enter = фонът на темата)',
        'translate': 'На {lang}', 'same': 'Enter = същото като горе',
        'dir': 'Папка за профилното хранилище',
        'building': 'Изграждам профила…', 'built': 'Готови са {n} изображения и {readmes}.',
        'lint_ok': 'Всички изображения минават проверките на GitHub.', 'preview': 'Отварям преглед в браузъра…',
        'publish': 'Да публикувам ли в github.com/{user}/{user} сега?', 'published': 'Публикувано! Отворете https://github.com/{user}',
        'no_gh': 'За публикуване създайте хранилище {user}/{user} в GitHub (публично, празно) и изпълнете:',
        'later': 'Промени по-късно със същата команда — отговорите се помнят.',
        'yn': '[Д/н]', 'ny': '[д/Н]',
        'steps_default': [('Проучване', 'Цели, потребители и ограничения'), ('Дизайн', 'Интерфейс, архитектура и обхват'),
                          ('Разработка', 'Функции, интеграции и тестове'), ('Публикуване', 'Публикуване, документация, развитие')],
        'heads': {'work': ('Избрана работа', 'Какво съм създал'), 'stack': ('Технологии', 'Инструменти, с които работя'),
                  'numbers': ('В числа', 'Какво нося'), 'process': ('Процес', 'Как се движи един проект'),
                  'contact': ('Контакт', 'Да поговорим')},
        'stack_title': 'Всекидневни инструменти', 'hi': '👋 Здравейте, аз съм {name}', 'tech_count': '{n} технологии',
    },
}
LANG_NAMES = {'en': {'en': 'English', 'bg': 'Bulgarian'}, 'bg': {'en': 'английски', 'bg': 'български'}}
SECTIONS = ['hero', 'about', 'work', 'stack', 'numbers', 'process', 'contact', 'footer', 'dividers', 'switch']
DEFAULT_ON = ['hero', 'about', 'work', 'stack', 'process', 'contact', 'footer', 'dividers', 'switch']
DECOR = ['orbit', 'floor', 'stars', 'beam', 'glow', 'bar']
CONTACTS = [('email', 'mail'), ('discord', 'discord'), ('github', 'github'), ('website', 'web'), ('linkedin', 'linkedin'),
            ('x', 'x'), ('telegram', 'telegram'), ('instagram', 'instagram'), ('youtube', 'youtube')]
LABELS = {'mail': {'en': 'EMAIL', 'bg': 'ИМЕЙЛ'}, 'web': {'en': 'WEBSITE', 'bg': 'САЙТ'}}


def text_for(lang, key):
    return T.get(lang, T['en'])[key]


class Wizard:
    def __init__(self, ui='en', previous=None):
        self.ui = ui
        self.t = T[ui]
        self.prev = previous if previous.get('version') == 2 else {}
        self.langs = ['en']

    # ---------------------------------------------------------------- prompts
    def raw(self, label):
        try:
            return input(label).strip()
        except EOFError:
            return ''

    def ask(self, key, default='', label=None):
        """Enter keeps the default, "-" clears it, anything else replaces it."""
        label = label or self.t[key]
        hint = f' {paint("2", "[" + default + "]")}' if default else ''
        value = self.raw(f'{paint("1;35", "›")} {label}{hint}: ')
        if value == '-':
            return ''
        return value or default

    def yes(self, key, default=True, **fmt):
        mark = self.t['yn'] if default else self.t['ny']
        value = self.raw(f'{paint("1;35", "?")} {self.t[key].format(**fmt)} {paint("2", mark)} ').lower()
        if not value:
            return default
        return value[0] in ('y', 'д')

    def say(self, value, code='0'):
        print(paint(code, value))

    def part(self, name):
        self.say(f'\n  {self.t["part"].format(name=name)}', '1;36')

    def text(self, key, default=None, label=None):
        """One text per profile language; the second language defaults to the first answer."""
        langs = self.langs
        if isinstance(default, str):
            default = {lang: default for lang in langs}
        default = default or {}
        first = self.ask(key, default.get(langs[0], ''), label)
        if not first:
            return None
        out = {langs[0]: first}
        for lang in langs[1:]:
            name = LANG_NAMES[self.ui][lang]
            suggestion = default.get(lang) if default.get(lang) and first == default.get(langs[0]) else first
            out[lang] = self.ask(key, suggestion, f'  ↳ {self.t["translate"].format(lang=name)} ({self.t["same"]})') or first
        return out

    def listing(self, key, default):
        value = self.ask(key, ', '.join(default or []))
        return [x.strip() for x in value.split(',') if x.strip()]

    def toggles(self, title, keys, names, enabled):
        enabled = list(enabled)
        while True:
            self.say(f'\n  {title}', '1;36')
            for i, key in enumerate(keys):
                mark = paint('32', '✓') if key in enabled else paint('2', '·')
                self.say(f'   [{mark}] {i + 1:>2}  {names[key]}')
            value = self.raw(f'{paint("1;35", "›")} {self.t["toggle"]}: ')
            if not value:
                return [k for k in keys if k in enabled]
            for token in value.replace(',', ' ').split():
                if token.isdigit() and 1 <= int(token) <= len(keys):
                    key = keys[int(token) - 1]
                    enabled.remove(key) if key in enabled else enabled.append(key)

    def defaults(self, key):
        return {lang: text_for(lang, 'heads')[key] for lang in self.langs}

    def heading(self, key, prev):
        d = self.defaults(key)
        kicker = self.text('kicker', prev.get('kicker', {lang: d[lang][0] for lang in self.langs}))
        title = self.text('title', prev.get('title', {lang: d[lang][1] for lang in self.langs}))
        return {'kicker': kicker, 'title': title}

    # ---------------------------------------------------------------- colours
    def colors(self, prev):
        t = self.t
        self.part(t['colors'])
        names = list(THEMES)
        for i, name in enumerate(names):
            accents = ''.join(swatch(c) for c in THEMES[name]['accents'])
            self.say(f'   {i + 1:>2}  {name:<9} {accents}  {paint("2", BG_OF.get(name, ""))}')
        self.say(f'   {paint("2", t["themes_help"])}')
        current = prev.get('theme', 'aurora')
        while True:
            pick = self.ask('theme', current).strip().lower()
            if pick.isdigit() and 1 <= int(pick) <= len(names):
                result = {'theme': names[int(pick) - 1], 'colors': {}}
                break
            if pick in names:
                result = {'theme': pick, 'colors': prev.get('colors', {}) if pick == current else {}}
                break
            if pick == 'r':
                seed = 0
                while True:
                    seed += 1
                    accents = random_palette(f'{self.prev.get("user", "")}-{os.getpid()}-{seed}')
                    self.say('   ' + ''.join(swatch(c) for c in accents) + '  ' + ' '.join(accents))
                    if self.yes('random_ok', True):
                        break
                result = {'theme': current if current in names else 'aurora', 'colors': {'accents': accents}}
                break
            if pick == 'c':
                while True:
                    raw = self.ask('custom', ', '.join(prev.get('colors', {}).get('accents', [])))
                    colors = [x.strip() for x in raw.split(',') if x.strip()]
                    bad = [x for x in colors if not parse_color(x)]
                    if colors and not bad:
                        break
                    self.say(f'  {t["bad_color"].format(v=", ".join(bad) or "—")}', '33')
                accents = [parse_color(x) for x in colors]
                self.say('   ' + ''.join(swatch(c) for c in accents))
                result = {'theme': current if current in names else 'aurora', 'colors': {'accents': accents}}
                break
        bgs = list(BACKGROUNDS)
        self.say('   ' + '  '.join(f'{i + 1} {name} {swatch(BACKGROUNDS[name]["mid"])}' for i, name in enumerate(bgs)))
        bg = self.ask('background', prev.get('colors', {}).get('background', '')).strip().lower()
        if bg.isdigit() and 1 <= int(bg) <= len(bgs):
            bg = bgs[int(bg) - 1]
        if bg in bgs:
            result['colors']['background'] = bg
        return result

    # ---------------------------------------------------------------- flow
    def run(self):
        t, prev = self.t, self.prev
        self.say(f'\n  ✦ {t["welcome"]}', '1;36')
        self.say(f'    {t["intro"]}\n', '2')
        choice = self.ask('langs', prev.get('langs_choice', '2' if self.ui == 'bg' else '1'))
        self.langs = {'1': ['en'], '2': ['en', 'bg'], '3': ['bg', 'en']}.get(choice, ['en'])
        keys = [k for k in SECTIONS if k != 'switch' or len(self.langs) > 1]
        sections = self.toggles(t['sections'], keys, t['sec'], prev.get('sections', DEFAULT_ON))
        a = {'version': 2, 'langs_choice': choice, 'sections': sections}
        a['user'] = self.ask('user', prev.get('user') or detect_user())
        a['name'] = self.ask('name', prev.get('name', ''))
        a['role'] = self.text('role', prev.get('role'))
        name = a['name'] or a['user']

        if 'hero' in sections:
            self.part(t['sec']['hero'])
            ph = prev.get('hero', {})
            kicker_default = {lang: ' · '.join(x for x in (name, (a['role'] or {}).get(lang, '')) if x) for lang in self.langs}
            a['hero'] = {'kicker': self.text('h_kicker', ph.get('kicker', kicker_default)),
                         'head1': self.text('head1', ph.get('head1')), 'head2': self.text('head2', ph.get('head2')),
                         'line': self.text('line', ph.get('line'))}
            a['decor'] = self.toggles(t['decor'], DECOR, t['dec'], prev.get('decor', DECOR))
        if 'about' in sections:
            self.part(t['sec']['about'])
            pa = prev.get('about', {})
            hi = {lang: text_for(lang, 'hi').format(name=name.split()[0] if name else '') for lang in self.langs}
            a['about'] = {'heading': self.text('about_head', pa.get('heading', hi)), 'text': self.text('about_text', pa.get('text'))}
        if 'work' in sections:
            self.part(t['sec']['work'])
            pw = prev.get('work', {})
            work = self.heading('work', pw)
            self.say(f'  {t["projects"]}', '2')
            items, old_items = [], pw.get('items', [])
            for i in range(8):
                old = old_items[i] if i < len(old_items) else {}
                pname = self.ask('p_name', old.get('name', ''), f'{i + 1}. {t["p_name"]}')
                if not pname:
                    break
                item = {'name': pname}
                for key, field in (('p_kind', 'kind'), ('p_desc', 'description')):
                    value = self.text(key, old.get(field))
                    if value:
                        item[field] = value
                tags = self.listing('p_tags', old.get('tags'))
                if tags:
                    item['tags'] = tags
                url = self.ask('p_url', old.get('url', ''))
                if url:
                    item['url'] = url if url.startswith('http') else f'https://{url}'
                items.append(item)
            work['items'] = items
            a['work'] = work
        if 'hero' in sections:
            default_chips = prev.get('hero', {}).get('chips', [p['name'] for p in a.get('work', {}).get('items', [])][:4])
            a['hero']['chips'] = self.listing('chips', default_chips)[:4]
        if 'stack' in sections:
            self.part(t['sec']['stack'])
            ps = prev.get('stack', {})
            stack = self.heading('stack', ps)
            stack['panel'] = self.text('panel', ps.get('panel', {lang: text_for(lang, 'stack_title') for lang in self.langs}))
            sample = ', '.join(v['title'] for v in list(ICONS.values())[:14])
            self.say(f'  {t["stack_hint"].format(sample=sample, n=len(ICONS))}', '2')
            stack['items'] = self.listing('stack', ps.get('items'))
            unknown = [x for x in stack['items'] if not resolve_tech(x)[1]]
            if unknown:
                self.say(f'  {t["unknown"].format(names=", ".join(unknown))}', '33')
            n = len(stack['items'])
            stack['count'] = self.text('count', ps.get('count', {lang: text_for(lang, 'tech_count').format(n=n) for lang in self.langs}))
            a['stack'] = stack
        if 'numbers' in sections:
            self.part(t['sec']['numbers'])
            pn = prev.get('numbers', {})
            numbers = self.heading('numbers', pn)
            self.say(f'  {t["numbers"]}', '2')
            items, old_items = [], pn.get('items', [])
            for i in range(4):
                old = old_items[i] if i < len(old_items) else {}
                value = self.ask('n_value', old.get('value', ''), f'{i + 1}. {t["n_value"]}')
                if not value:
                    break
                items.append({'value': value, 'label': self.text('n_label', old.get('label')) or ''})
            numbers['items'] = items
            a['numbers'] = numbers
        if 'process' in sections:
            self.part(t['sec']['process'])
            pp = prev.get('process', {})
            process = self.heading('process', pp)
            self.say(f'  {t["steps"]}', '2')
            defaults = pp.get('steps') or [{'title': {lang: text_for(lang, 'steps_default')[i][0] for lang in self.langs},
                                            'text': {lang: text_for(lang, 'steps_default')[i][1] for lang in self.langs}} for i in range(4)]
            steps = []
            for i, old in enumerate(defaults):
                title = self.text('step_title', old.get('title'), t['step_title'].format(i=i + 1))
                if not title:
                    continue
                steps.append({'title': title, 'text': self.text('step_text', old.get('text'), t['step_text'].format(i=len(steps) + 1)) or ''})
            while len(steps) < 6:
                title = self.text('more')
                if not title:
                    break
                steps.append({'title': title, 'text': self.text('step_text', None, t['step_text'].format(i=len(steps) + 1)) or ''})
            if len(steps) < 2:
                self.say(f'  {t["few_steps"]}', '33')
            process['steps'] = steps
            a['process'] = process
        if 'contact' in sections:
            self.part(t['sec']['contact'])
            pc = prev.get('contact', {})
            contact = self.heading('contact', pc)
            self.say(f'  {t["contact"]}', '2')
            items = {}
            for key, kind in CONTACTS:
                old = pc.get('items', {}).get(key, {})
                default = old.get('value', a['user'] if key == 'github' and 'github' not in pc.get('items', {}) and not pc else '')
                value = self.ask(key, default)
                if value:
                    label_default = old.get('label') or {lang: LABELS.get(kind, {}).get(lang, LABELS.get(kind, {}).get('en', ''))
                                                         or (ICONS[kind]['title'].upper() if kind in ICONS else kind.upper())
                                                         for lang in self.langs}
                    items[key] = {'value': value, 'label': self.text('label', label_default)}
            contact['items'] = items
            a['contact'] = contact
        if 'footer' in sections:
            self.part(t['sec']['footer'])
            pf = prev.get('footer', {})
            words_default = pf.get('words') or [p['name'].upper() for p in a.get('work', {}).get('items', [])][:4]
            last = a.get('hero', {}).get('head2') or a.get('hero', {}).get('head1')
            a['footer'] = {'words': self.listing('words', words_default), 'tagline': self.text('tagline', pf.get('tagline', last))}
        a['colors'] = self.colors(prev.get('colors', {}))
        return compose(a, self.langs)


BG_OF = {name: bg for name, (bg, _a) in PRESETS.items()}


def detect_user():
    for cmd in (['gh', 'api', 'user', '--jq', '.login'], ['git', 'config', '--get', 'github.user']):
        if shutil.which(cmd[0]):
            try:
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=8).stdout.strip()
                if out:
                    return out
            except (OSError, subprocess.SubprocessError):
                pass
    return ''


def compose(a, langs):
    """Turn the answers into a profile config. Anything left out is simply not drawn."""
    sec = a['sections']
    name = a.get('name') or a.get('user') or ''
    sections = []

    def add_heading(block, anchor):
        if block.get('title'):
            sections.append({'type': 'heading', 'anchor': anchor, 'kicker': block.get('kicker') or '', 'title': block['title']})

    def divider():
        if 'dividers' in sec and sections:
            sections.append({'type': 'divider'})

    hero = a.get('hero')
    if 'hero' in sec and hero:
        headline = {}
        for lang in langs:
            lines = [x.get(lang) for x in (hero.get('head1'), hero.get('head2')) if x]
            headline[lang] = lines or ([name] if name else [])
        if any(headline.values()):
            sections.append({'type': 'hero', 'kicker': hero.get('kicker') or '', 'headline': headline,
                             'lines': {lang: [hero['line'][lang]] if hero.get('line') else [] for lang in langs},
                             'chips': hero.get('chips', []), 'decor': {k: k in a.get('decor', DECOR) for k in DECOR}})
    about = a.get('about')
    if 'about' in sec and about and (about.get('heading') or about.get('text')):
        text = {}
        for lang in langs:
            parts = []
            if about.get('heading'):
                parts.append(f'### {about["heading"][lang]}')
            if about.get('text'):
                parts.append(about['text'][lang])
            text[lang] = '\n\n'.join(parts)
        sections.append({'type': 'markdown', 'text': text})
    work = a.get('work')
    if 'work' in sec and work and work.get('items'):
        divider()
        add_heading(work, 'work')
        sections.append({'type': 'projects', 'items': work['items']})
    stack = a.get('stack')
    if 'stack' in sec and stack and stack.get('items'):
        divider()
        add_heading(stack, 'stack')
        block = {'type': 'stack', 'items': stack['items'], 'kicker': stack.get('count') or ''}
        if stack.get('panel'):
            block['title'] = stack['panel']
        sections.append(block)
    numbers = a.get('numbers')
    if 'numbers' in sec and numbers and numbers.get('items'):
        divider()
        add_heading(numbers, 'numbers')
        sections.append({'type': 'highlights', 'items': numbers['items']})
    process = a.get('process')
    if 'process' in sec and process and len(process.get('steps', [])) >= 2:
        divider()
        add_heading(process, 'process')
        sections.append({'type': 'timeline', 'steps': process['steps'][:6], 'kicker': ''})
    contact = a.get('contact')
    if 'contact' in sec and contact and contact.get('items'):
        divider()
        add_heading(contact, 'contact')
        buttons = []
        for key, kind in CONTACTS:
            entry = contact['items'].get(key)
            if not entry:
                continue
            value = entry['value']
            button = {'kind': kind, 'value': value}
            if entry.get('label'):
                button['label'] = entry['label']
            if key == 'email':
                button['href'] = f'mailto:{value}'
            elif key in ('website', 'linkedin', 'youtube'):
                button['href'] = value if value.startswith('http') else f'https://{value}'
                button['value'] = re.sub(r'^https?://(www\.)?', '', value).rstrip('/')
            elif key == 'github':
                button['value'] = '@' + value.lstrip('@')
                button['href'] = f'https://github.com/{value.lstrip("@")}'
            elif key == 'x':
                button['href'] = f'https://x.com/{value.lstrip("@")}'
            elif key == 'telegram':
                button['href'] = f'https://t.me/{value.lstrip("@")}'
            elif key == 'instagram':
                button['href'] = f'https://instagram.com/{value.lstrip("@")}'
            buttons.append(button)
        sections.append({'type': 'contact', 'buttons': buttons})
    footer = a.get('footer')
    if 'footer' in sec and footer and (footer.get('words') or footer.get('tagline')):
        sections.append({'type': 'footer', 'words': footer.get('words', []), 'tagline': footer.get('tagline') or ''})
    if not sections:
        sections.append({'type': 'markdown', 'text': f'### {name}' if name else '###'})
    colors = a.get('colors', {})
    config = {'theme': colors.get('theme', 'aurora'), 'languages': langs, 'assets': 'assets/studio', 'sections': sections,
              'answers': a}
    if colors.get('colors'):
        config['colors'] = colors['colors']
    if 'switch' not in sec:
        config['language_switch'] = False
    if a.get('user'):
        config['repository'] = f'{a["user"]}/{a["user"]}'
    return config


WORKFLOW = """name: Build profile
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
"""


def preview(root, readme):
    """A local page that shows the README the way GitHub's dark theme does."""
    html_body = []
    for block in (root / readme).read_text(encoding='utf-8').split('\n\n'):
        block = block.strip()
        if block.startswith('### '):
            html_body.append(f'<h3>{block[4:]}</h3>')
        elif block.startswith('<'):
            html_body.append(block)
        elif block:
            html_body.append(f'<p>{block}</p>')
    page = root / '.preview.html'
    page.write_text('<!doctype html><meta charset="utf-8"><title>Profile preview</title><style>'
                    'body{margin:0;background:#0d1117;color:#e6edf3;font:16px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}'
                    'main{max-width:1012px;margin:32px auto;padding:24px;border:1px solid #30363d;border-radius:6px}'
                    'img{max-width:100%}p{margin:0 0 16px}a{color:#4493f8}</style><main>'
                    + '\n'.join(html_body) + '</main>', encoding='utf-8')
    return page


def publish(root, user, t, wizard):
    if not shutil.which('git'):
        return False
    run = lambda *cmd: subprocess.run(cmd, cwd=root, capture_output=True, text=True)  # noqa: E731
    if not (root / '.git').exists():
        run('git', 'init', '-b', 'main')
    run('git', 'add', '-A')
    run('git', 'commit', '-m', 'Profile built with readme-studio')
    remote = run('git', 'remote', 'get-url', 'origin').stdout.strip()
    if not remote and shutil.which('gh'):
        made = run('gh', 'repo', 'create', f'{user}/{user}', '--public', '--source', '.', '--push')
        if made.returncode == 0:
            return True
    if not remote:
        run('git', 'remote', 'add', 'origin', f'https://github.com/{user}/{user}.git')
    pushed = run('git', 'push', '-u', 'origin', 'main')
    if pushed.returncode == 0:
        return True
    wizard.say(f'\n  {t["no_gh"].format(user=user)}', '33')
    wizard.say(f'    cd "{root}" && git push -u origin main', '1')
    return False


def main(argv):
    import argparse
    parser = argparse.ArgumentParser(prog='python -m studio init')
    parser.add_argument('--dir', help='profile repository folder')
    parser.add_argument('--ui', choices=['en', 'bg'], help='language of the questions')
    parser.add_argument('--no-open', action='store_true', help='do not open the browser preview')
    parser.add_argument('--no-publish', action='store_true', help='never push to GitHub')
    args = parser.parse_args(argv)
    ui = args.ui or ('bg' if os.environ.get('LANG', '').startswith('bg') else None)
    if not ui:
        try:
            ui = 'bg' if input(paint('1;35', '› ') + 'Language / Език (1 English · 2 Български) [1]: ').strip() == '2' else 'en'
        except EOFError:
            ui = 'en'
    if os.name == 'nt':
        os.system('')  # turn on ANSI colours in the Windows console
    t = T[ui]
    if not args.dir and (Path.cwd() / 'profile.json').is_file() and not (Path.cwd() / 'studio').is_dir():
        args.dir = str(Path.cwd())
    existing = Path(args.dir).expanduser() / 'profile.json' if args.dir else None
    previous = json.loads(existing.read_text()).get('answers', {}) if existing and existing.is_file() else {}
    wizard = Wizard(ui, previous)
    config = wizard.run()
    user = config['answers'].get('user') or 'profile'
    root = Path(args.dir or wizard.ask('dir', str(Path.home() / user))).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    (root / 'profile.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    workflow = root / '.github/workflows/profile.yml'
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(WORKFLOW, encoding='utf-8')
    ignore = root / '.gitignore'
    if '.preview.html' not in (ignore.read_text() if ignore.exists() else ''):
        with ignore.open('a', encoding='utf-8') as handle:
            handle.write('.preview.html\n')

    wizard.say(f'\n  {t["building"]}', '1;36')
    result = build(root / 'profile.json')
    wizard.say(f'  ✓ {t["built"].format(n=len(result["assets"]), readmes=", ".join(result["readmes"]))}', '32')
    problems = lint(root, 'assets/studio')
    if problems:
        for problem in problems:
            wizard.say(f'  ✗ {problem}', '31')
    else:
        wizard.say(f'  ✓ {t["lint_ok"]}', '32')
    if not args.no_open:
        wizard.say(f'  {t["preview"]}', '2')
        webbrowser.open(preview(root, 'README.md').as_uri())
    if not args.no_publish and config['answers'].get('user') and wizard.yes('publish', True, user=user):
        if publish(root, user, t, wizard):
            wizard.say(f'\n  ★ {t["published"].format(user=user)}', '1;32')
    wizard.say(f'\n  {t["later"]}\n', '2')
    return 1 if problems else 0
