# Validation evidence

Baseline: **Claude Code 2.1.288**, macOS, Python 3.12.12. Initial release verified October 3, 2026. [Full native check output](check-results.json).

| Check | Result | What it establishes |
| --- | --- | --- |
| Marketplace strict validation | Passed | The marketplace manifest is accepted by this Claude version |
| Plugin strict validation | 50 / 50 passed | Manifests and statically analyzed hooks/calls are accepted |
| Native plugin tests | 250 passed, 0 failed | Real engine hooks, commands, controls, timers, and element-tree validation work with fixtures |
| Terminal/Desktop render tests | 50 mods on both surfaces | Element trees and control callbacks are accepted on both surfaces, including a narrow terminal width |
| Native CLI smoke | Single plugin and all 50 together passed | An actual `claude -p` process loaded all 50 workers/hooks without failures and dispatched `/context-meter` without model work |
| Browser screenshots | 50 / 50 captured | Local preview pages paint the captured native-kit trees without page errors |
| Gallery browser checks | Passed | Search, the 8-item Git filter, all 50 cards, and 390px layout work |
| Artifact audit | Passed | Mod count, MIT licenses, local imports, screenshot source/content hashes, and local documentation links are consistent |
| Interactive native layout acceptance | Open | Native terminal pixels, Desktop painting, and real keyboard focus for all 50 mods have not been verified |
| GitHub-hosted CI | Not yet observed at publication | Workflow is configured; local checks are separate from the eventual GitHub result |

Every mod has five native tests: command registration/opening, another pane's isolation, Terminal behavior, Desktop behavior, and a preview capture. Tests use fresh modules and in-memory engine stubs. They do not execute real tools, read real user files, spend model tokens, or touch a real account.

Behavioral cases include missing/oversized files, a real env filename and an env-example symlink refused before reading, invalid input, clipboard and composer actions, persistent collection keys, task toggles/deletions, timer pause/reset behavior, refused calls avoiding downstream dispatch, and read-only argv inspection. Git/file-viewer tests use fixture output; they do not establish portability across every Git or filesystem version.

A CLI smoke run recorded these sanitized engine debug lines:

```text
hooks module context-meter@inline loaded (worker, environment 1, tier user); events: session.start,command.run,ui.render
plugin.register: context-meter (user, context-meter@inline), judged by core alone: admitted
$.command.register (context-meter): /context-meter listed
context-meter (user) answered command.run without next(); nothing beneath it ran for this dispatch
```

A second smoke run used `--plugin-dir ./mods`, admitted all 50 plugins, and reported no skipped hooks or module load failures.

The `claude -p` run shows plugin loading and command dispatch; it does not show a pane on that surface.

## Re-run

```sh
claude plugin validate .claude-plugin/marketplace.json --strict
python3 scripts/check.py
python3 scripts/audit.py
```

To regenerate screenshot data after a source or fixture change, use `python3 scripts/check.py --capture-previews`, then the preview/screenshot steps in [SCREENSHOTS.md](SCREENSHOTS.md). Source digests include hooks, native test fixtures, and plugin manifests. The default check run leaves committed previews intact.

The GitHub workflow pins the tested Claude version and runs validation, tests, and the artifact audit. It makes no claims about future mods API versions. When updating the baseline, rerun the same checks and test native layouts on the target apps.
