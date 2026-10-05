# Contributing

Thanks for helping! A few rules keep every profile built with readme-studio safe to serve from GitHub:

1. **No runtime dependencies in the output.** SVGs must not reference scripts, remote URLs, web fonts or `<foreignObject>`.
2. **Static first.** The default render is a complete composition. Animation goes only inside
   `@media (prefers-reduced-motion: no-preference)`; motion-only elements use class `live`, static stand-ins use `still`.
3. **Desktop and mobile.** Every component draws a 1200 px and a 600 px version.
4. **Accessible.** Every SVG has a `<title>` and a `<desc>` that carry the visible text.
5. **Deterministic.** The same config must produce byte-identical files (seed any randomness).

Before opening a pull request:

```bash
python -m unittest discover tests
python scripts/showcase.py   # commit the regenerated docs/ and examples/
```

New components are very welcome: add the function to `studio/components.py`, wire it into `studio/build.py`,
document it in both READMEs and add it to `tests/test_studio.py`.
