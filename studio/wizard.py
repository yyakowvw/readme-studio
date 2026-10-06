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
from .style import THEMES

COLOR = sys.stdout.isatty() and not os.environ.get('NO_COLOR')


def paint(code, value):
    return f'\033[{code}m{value}\033[0m' if COLOR else value


T = {
    'en': {
        'welcome': 'readme-studio · set up your animated GitHub profile',
        'intro': 'Answer a few questions. Press Enter to accept the suggestion in [brackets].',
        'langs': 'Profile languages', 'langs_opts': '1 English · 2 English + Bulgarian · 3 Bulgarian + English',
        'user': 'GitHub username', 'name': 'Your name', 'role': 'What you do (e.g. full-stack developer)',
        'head1': 'Headline, line 1', 'head2': 'Headline, line 2 (optional)',
        'line': 'One line about your work (optional)',
        'about': 'A short "about me" paragraph (optional)',
        'projects': 'Projects — leave the name empty when you are done',
        'p_name': 'Project name', 'p_kind': 'Type (e.g. web app, Discord bot)', 'p_desc': 'One-sentence description',
        'p_tags': 'Technologies, comma separated', 'p_url': 'Link (optional)',
        'stack': 'Your technologies, comma separated', 'stack_hint': 'Known icons include: {sample} … ({n} in total)',
        'unknown': 'No icon for {names} — a monogram tile will be used.',
        'steps': 'Add a "how I work" timeline?', 'contact': 'Contacts — leave empty to skip',
        'email': 'Email', 'discord': 'Discord username', 'website': 'Website', 'linkedin': 'LinkedIn URL',
        'x': 'X (Twitter) handle', 'telegram': 'Telegram username', 'instagram': 'Instagram handle', 'youtube': 'YouTube channel URL',
        'theme': 'Theme', 'translate': 'In {lang}', 'same': 'Enter = same as above',
        'dir': 'Folder for your profile repository',
        'building': 'Building your profile…', 'built': 'Built {n} images and {readmes}.',
        'lint_ok': 'Every image passes the GitHub checks.', 'preview': 'Opening a preview in your browser…',
        'publish': 'Publish to github.com/{user}/{user} now?', 'published': 'Published! Open https://github.com/{user}',
        'no_gh': 'To publish, create the repository {user}/{user} on GitHub (public, empty), then run:',
        'later': 'Change anything later with:  python -m studio init  (your answers are remembered)',
        'yes': 'y', 'yn': '[Y/n]', 'ny': '[y/N]',
        'steps_default': [('Discover', 'Goals, users and constraints'), ('Design', 'Interface, architecture and scope'),
                          ('Build', 'Features, integrations and tests'), ('Launch', 'Deploy, document, improve')],
        'h_work': ('Selected work', "Things I've built"), 'h_stack': ('Technology', 'Tools I work with'),
        'h_process': ('Process', 'How a project moves'), 'h_contact': ('Contact', "Let's talk"),
        'stack_title': 'Daily drivers', 'hi': '### 👋 Hi, I\'m {name}',
    },
    'bg': {
        'welcome': 'readme-studio · настройка на анимиран GitHub профил',
        'intro': 'Отговорете на няколко въпроса. Enter приема предложението в [скоби].',
        'langs': 'Езици на профила', 'langs_opts': '1 английски · 2 английски + български · 3 български + английски',
        'user': 'GitHub потребителско име', 'name': 'Вашето име', 'role': 'С какво се занимавате (напр. full-stack разработчик)',
        'head1': 'Заглавие, ред 1', 'head2': 'Заглавие, ред 2 (по желание)',
        'line': 'Един ред за работата ви (по желание)',
        'about': 'Кратък текст „за мен“ (по желание)',
        'projects': 'Проекти — оставете името празно, когато приключите',
        'p_name': 'Име на проекта', 'p_kind': 'Вид (напр. уеб приложение, Discord бот)', 'p_desc': 'Описание в едно изречение',
        'p_tags': 'Технологии, разделени със запетая', 'p_url': 'Връзка (по желание)',
        'stack': 'Вашите технологии, разделени със запетая', 'stack_hint': 'Има икони за: {sample} … (общо {n})',
        'unknown': 'Няма икона за {names} — ще се покажат инициали.',
        'steps': 'Да добавя ли времева линия „как работя“?', 'contact': 'Контакти — оставете празно, за да пропуснете',
        'email': 'Имейл', 'discord': 'Discord потребител', 'website': 'Сайт', 'linkedin': 'LinkedIn адрес',
        'x': 'X (Twitter) профил', 'telegram': 'Telegram потребител', 'instagram': 'Instagram профил', 'youtube': 'YouTube канал (адрес)',
        'theme': 'Тема', 'translate': 'На {lang}', 'same': 'Enter = същото като горе',
        'dir': 'Папка за профилното хранилище',
        'building': 'Изграждам профила…', 'built': 'Готови са {n} изображения и {readmes}.',
        'lint_ok': 'Всички изображения минават проверките на GitHub.', 'preview': 'Отварям преглед в браузъра…',
        'publish': 'Да публикувам ли в github.com/{user}/{user} сега?', 'published': 'Публикувано! Отворете https://github.com/{user}',
        'no_gh': 'За публикуване създайте хранилище {user}/{user} в GitHub (публично, празно) и изпълнете:',
        'later': 'Промени по-късно:  python -m studio init  (отговорите се помнят)',
        'yes': 'д', 'yn': '[Д/н]', 'ny': '[д/Н]',
        'steps_default': [('Проучване', 'Цели, потребители и ограничения'), ('Дизайн', 'Интерфейс, архитектура и обхват'),
                          ('Разработка', 'Функции, интеграции и тестове'), ('Публикуване', 'Публикуване, документация, развитие')],
        'h_work': ('Избрана работа', 'Какво съм създал'), 'h_stack': ('Технологии', 'Инструменти, с които работя'),
        'h_process': ('Процес', 'Как се движи един проект'), 'h_contact': ('Контакт', 'Да поговорим'),
        'stack_title': 'Всекидневни инструменти', 'hi': '### 👋 Здравейте, аз съм {name}',
    },
}
LANG_NAMES = {'en': {'en': 'English', 'bg': 'Bulgarian'}, 'bg': {'en': 'английски', 'bg': 'български'}}
CONTACTS = [('email', 'mail'), ('discord', 'discord'), ('website', 'web'), ('linkedin', 'linkedin'),
            ('x', 'x'), ('telegram', 'telegram'), ('instagram', 'instagram'), ('youtube', 'youtube')]


class Wizard:
    def __init__(self, ui='en', previous=None):
        self.ui = ui
        self.t = T[ui]
        self.prev = previous or {}

    # ---------------------------------------------------------------- prompts
    def ask(self, key, default='', label=None):
        label = label or self.t[key]
        hint = f' {paint("2", "[" + default + "]")}' if default else ''
        try:
            value = input(f'{paint("1;35", "›")} {label}{hint}: ').strip()
        except EOFError:
            value = ''
        return value or default

    def yes(self, key, default=True, **fmt):
        mark = self.t['yn'] if default else self.t['ny']
        try:
            value = input(f'{paint("1;35", "?")} {self.t[key].format(**fmt)} {paint("2", mark)} ').strip().lower()
        except EOFError:
            value = ''
        if not value:
            return default
        return value[0] in ('y', 'д', self.t['yes'])

    def say(self, value, code='0'):
        print(paint(code, value))

    def both(self, key, langs, default=None, label=None):
        """Ask once per language; the second language defaults to the first answer."""
        if isinstance(default, str):
            default = {langs[0]: default}
        default = default or {}
        first = self.ask(key, default.get(langs[0], ''), label)
        if not first:
            return None
        out = {langs[0]: first}
        for lang in langs[1:]:
            name = LANG_NAMES[self.ui][lang]
            out[lang] = self.ask(key, default.get(lang, first), f'  ↳ {self.t["translate"].format(lang=name)} ({self.t["same"]})')
        return out if len(langs) > 1 else first

    # ---------------------------------------------------------------- flow
    def run(self):
        t, prev = self.t, self.prev
        self.say(f'\n  ✦ {t["welcome"]}', '1;36')
        self.say(f'    {t["intro"]}\n', '2')
        choice = self.ask('langs', prev.get('_langs', '2' if self.ui == 'bg' else '1'), f'{t["langs"]} ({t["langs_opts"]})')
        langs = {'1': ['en'], '2': ['en', 'bg'], '3': ['bg', 'en']}.get(choice, ['en'])
        user = self.ask('user', prev.get('_user') or detect_user())
        name = self.ask('name', prev.get('_name', ''))
        role = self.both('role', langs, prev.get('_role'))
        head1 = self.both('head1', langs, prev.get('_head1'))
        head2 = self.both('head2', langs, prev.get('_head2'))
        line = self.both('line', langs, prev.get('_line'))
        about = self.both('about', langs, prev.get('_about'))

        self.say(f'\n  {t["projects"]}', '1;36')
        projects = []
        for i in range(8):
            old = (prev.get('_projects') or [{}] * 8)[i] if i < len(prev.get('_projects') or []) else {}
            pname = self.ask('p_name', old.get('name', ''), f'{i + 1}. {t["p_name"]}')
            if not pname:
                break
            item = {'name': pname}
            for key, field in (('p_kind', 'kind'), ('p_desc', 'description')):
                value = self.both(key, langs, old.get(field) if isinstance(old.get(field), dict) else None)
                if value:
                    item[field] = value
            tags = self.ask('p_tags', ', '.join(old.get('tags', [])))
            if tags:
                item['tags'] = [x.strip() for x in tags.split(',') if x.strip()]
            url = self.ask('p_url', old.get('url', ''))
            if url:
                item['url'] = url if url.startswith('http') else f'https://{url}'
            projects.append(item)

        sample = ', '.join(v['title'] for v in list(ICONS.values())[:14])
        self.say(f'\n  {t["stack_hint"].format(sample=sample, n=len(ICONS))}', '2')
        stack_raw = self.ask('stack', ', '.join(prev.get('_stack', [])))
        stack = [x.strip() for x in stack_raw.split(',') if x.strip()]
        unknown = [x for x in stack if not resolve_tech(x)[1]]
        if unknown:
            self.say(f'  {t["unknown"].format(names=", ".join(unknown))}', '33')

        steps = self.yes('steps', prev.get('_steps', True))

        self.say(f'\n  {t["contact"]}', '1;36')
        contacts = {}
        for key, _kind in CONTACTS:
            value = self.ask(key, (prev.get('_contacts') or {}).get(key, ''))
            if value:
                contacts[key] = value

        names = list(THEMES)
        theme_label = f'{t["theme"]} (' + ' · '.join(f'{i + 1} {n}' for i, n in enumerate(names)) + ')'
        pick = self.ask('theme', str(names.index(prev.get('theme', 'aurora')) + 1), theme_label)
        theme = names[int(pick) - 1] if pick.isdigit() and 1 <= int(pick) <= len(names) else pick if pick in names else 'aurora'

        answers = dict(_langs=choice, _user=user, _name=name, _role=role, _head1=head1, _head2=head2, _line=line,
                       _about=about, _projects=projects, _stack=stack, _steps=steps, _contacts=contacts, theme=theme)
        return compose(answers, langs)


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


def per_lang(value, langs):
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    return {lang: value for lang in langs}


def pick(value, lang):
    return value.get(lang) if isinstance(value, dict) else value


def compose(a, langs):
    """Turn the answers into a profile config."""
    def head(key):
        return {'kicker': {lang: T.get(lang, T['en'])[key][0] for lang in langs},
                'title': {lang: T.get(lang, T['en'])[key][1] for lang in langs}}

    name = a['_name'] or a['_user']
    role = per_lang(a['_role'], langs) or {lang: '' for lang in langs}
    headline = {}
    for lang in langs:
        lines = [x for x in (pick(a['_head1'], lang), pick(a['_head2'], lang)) if x]
        headline[lang] = lines or [name]
    sections = [{
        'type': 'hero',
        'kicker': {lang: ' · '.join(x for x in (name, pick(role, lang)) if x) for lang in langs},
        'headline': headline,
        'lines': {lang: [pick(a['_line'], lang)] if a['_line'] else [] for lang in langs},
        'chips': [p['name'] for p in a['_projects'][:4]],
    }]
    hi = {lang: T.get(lang, T['en'])['hi'].format(name=name.split()[0] if name else a['_user']) for lang in langs}
    about = per_lang(a['_about'], langs)
    sections.append({'type': 'markdown', 'text': {lang: hi[lang] + (f'\n\n{about[lang]}' if about else '') for lang in langs}})
    if a['_projects']:
        sections += [{'type': 'divider'}, {'type': 'heading', 'anchor': 'work', **head('h_work')},
                     {'type': 'projects', 'items': a['_projects']}]
    if a['_stack']:
        sections += [{'type': 'divider'}, {'type': 'heading', 'anchor': 'stack', **head('h_stack')},
                     {'type': 'stack', 'title': {lang: T.get(lang, T['en'])['stack_title'] for lang in langs}, 'items': a['_stack']}]
    if a['_steps']:
        steps = []
        for i in range(4):
            steps.append({'title': {lang: T.get(lang, T['en'])['steps_default'][i][0] for lang in langs},
                          'text': {lang: T.get(lang, T['en'])['steps_default'][i][1] for lang in langs}})
        sections += [{'type': 'divider'}, {'type': 'heading', 'anchor': 'process', **head('h_process')},
                     {'type': 'timeline', 'steps': steps}]
    buttons = []
    for key, kind in CONTACTS:
        value = a['_contacts'].get(key)
        if not value:
            continue
        button = {'kind': kind, 'value': value}
        if key == 'email':
            button['href'] = f'mailto:{value}'
        elif key in ('website', 'linkedin', 'youtube'):
            button['href'] = value if value.startswith('http') else f'https://{value}'
            button['value'] = re.sub(r'^https?://(www\.)?', '', value).rstrip('/')
        elif key == 'x':
            button['href'] = f'https://x.com/{value.lstrip("@")}'
        elif key == 'telegram':
            button['href'] = f'https://t.me/{value.lstrip("@")}'
        elif key == 'instagram':
            button['href'] = f'https://instagram.com/{value.lstrip("@")}'
        buttons.append(button)
    if buttons:
        sections += [{'type': 'divider'}, {'type': 'heading', 'anchor': 'contact', **head('h_contact')},
                     {'type': 'contact', 'buttons': buttons}]
    words = [p['name'].upper() for p in a['_projects'][:4]] or [name.upper()]
    sections.append({'type': 'footer', 'words': words,
                     'tagline': {lang: headline[lang][-1] for lang in langs}})
    config = {'theme': a['theme'], 'languages': langs, 'assets': 'assets/studio', 'sections': sections, 'answers': a}
    if a['_user']:
        config['repository'] = f'{a["_user"]}/{a["_user"]}'
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
    user = config['answers']['_user'] or 'profile'
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
    if not args.no_publish and config['answers']['_user'] and wizard.yes('publish', True, user=user):
        if publish(root, user, t, wizard):
            wizard.say(f'\n  ★ {t["published"].format(user=user)}', '1;32')
    wizard.say(f'\n  {t["later"]}\n', '2')
    return 1 if problems else 0
