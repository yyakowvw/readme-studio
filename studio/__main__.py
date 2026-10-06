"""readme-studio command line.

  python -m studio init                   answer questions, get a finished profile
  python -m studio build [profile.json]   generate SVGs + README files
  python -m studio lint  [profile.json]   check the generated files
  python -m studio themes                 list the built-in themes
"""
import argparse
import sys
from pathlib import Path

from .build import build, load
from .lint import lint
from .style import THEMES


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ['init']:
        from .wizard import main as wizard
        return wizard(argv[1:])
    parser = argparse.ArgumentParser(prog='python -m studio', description='Animated, bilingual GitHub profile READMEs from one JSON file.')
    parser.add_argument('command', choices=['init', 'build', 'lint', 'themes'])
    parser.add_argument('config', nargs='?', default='profile.json')
    args = parser.parse_args(argv)
    if args.command == 'themes':
        for name, theme in THEMES.items():
            print(f'{name:8} {" ".join(theme["accents"])}')
        return 0
    config_path = Path(args.config)
    if not config_path.is_file():
        print(f'no config at {config_path} — copy examples/profile.json to get started', file=sys.stderr)
        return 2
    root = config_path.resolve().parent
    if args.command == 'build':
        result = build(config_path)
        print(f'wrote {len(result["assets"])} SVGs and {", ".join(result["readmes"])}')
        if result['removed']:
            print(f'removed {len(result["removed"])} stale SVGs')
    config = load(config_path)
    problems = lint(root, config.get('assets', 'assets/studio'))
    for problem in problems:
        print(f'  ✗ {problem}', file=sys.stderr)
    if problems:
        return 1
    print('lint: all clear')
    return 0


if __name__ == '__main__':
    sys.exit(main())
