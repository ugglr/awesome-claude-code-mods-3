# Contributing

A useful mod solves a specific problem, works on its own, and explains what it can access. This repository contains original implementations; research links are references, not bundled third-party code.

For community listings, edit `docs/COMMUNITY_MODS.md` and run `python3 scripts/build-readme.py`. That file is the source for the README's Community mods section. Verify use cases, install commands and prerequisites against the author's repository; include source links and the review date, and distinguish documentation review from runtime testing. Third-party listings do not change the bundled catalogue or its validation totals.

## Edit the source

`python3 scripts/build-mods.py` generates the independently installable folders in `mods/`, their README files, and `catalog.json`. The reviewed templates live in that script. Change the template, regenerate, and inspect the resulting diff. `hooks/ui.js` is deliberately copied into every plugin: mods may only import relative files inside their own directory.

`python3 scripts/build-desktop-mods.py` generates the 20 Desktop plugins and their tests; `build-mods.py` invokes it after the original 50. Run the Desktop generator directly for a Desktop-only change.

`python3 scripts/build-tests.py` generates each plugin's native tests and in-memory fixtures. Add assertions for user-visible behavior and failure cases, not just registration. Each test begins with a freshly loaded module. Register stubs before the first call on `$`.

## Check a change

```sh
python3 scripts/build-mods.py
python3 scripts/build-tests.py
python3 scripts/build-desktop-mods.py
python3 scripts/build-readme.py
python3 scripts/check.py --capture-previews
python3 scripts/render-previews.py
python3 scripts/screenshots.py --browser /path/to/chrome
python3 scripts/collection.py
python3 scripts/audit.py
```

Claude Code 2.1.288 is the tested baseline. Screenshot tooling additionally needs Python's `playwright` package and Chromium; these are development dependencies only. See [screenshot instructions](docs/SCREENSHOTS.md). Mod users need no Python, Node packages, bundler, or compilation.

For a focused change, start with `claude plugin validate mods/<name> --strict` and `claude plugin test mods/<name>`. Use `claude --plugin-dir ./mods/<name>` for a real interactive layout check. Try both terminal and Desktop Code tab before claiming native layout acceptance.

## Design rules

- Use literal hook names and explicit `$.namespace.method` calls so native validation can inventory access.
- Preserve `next(e)` for events you only observe. Draw only your own pane.
- Keep reads and output bounded. Use argv arrays for processes, with no shell.
- Never silently approve permission requests, submit prompts, start model calls, message agents, or run package scripts.
- Explain persistence, limits, prerequisites, and sensitive data access in the mod README.
- Add an accurate screenshot generated from its actual native-kit render tree. Keep fixture labels visible.
- Bump manifest and marketplace versions when publishing an update; installed plugins use cached versions.
- The collection contains 50 general mods and 20 Desktop additions. Keep catalogue, marketplace, gallery counts, screenshot provenance, and validation totals synchronized when adding plugins.

Contributions are licensed under this repository's MIT license. Do not include credentials, personal transcripts, or third-party assets without compatible permission.
