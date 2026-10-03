# Validation evidence

Baseline: **Claude Code 2.1.288**, macOS, Python 3.12.12. General collection and Desktop expansion verified October 3, 2026. [Full native check output](check-results.json).

| Check | Result | What it establishes |
| --- | --- | --- |
| Marketplace strict validation | Passed | The marketplace manifest is accepted by this Claude version |
| Plugin strict validation | 70 / 70 passed | Manifests and statically analyzed hooks/calls are accepted |
| Native plugin tests | 390 passed, 0 failed | Real engine hooks, commands, controls, timers, and element-tree validation work with fixtures |
| Terminal/Desktop render tests | 50 general mods on both surfaces + 20 Desktop mods at two widths | Element trees and control callbacks are accepted on both surfaces, including a narrow terminal width |
| Native CLI smoke | All 70 together passed | An actual `claude -p` process loaded all 70 workers/hooks, including 20 Desktop additions, with zero load failures or skipped hooks; `/desktop-usage-strip` returned the expected unsupported-surface explanation without a model turn |
| Browser screenshots | 70 / 70 captured | Local preview pages paint the captured native-kit trees without page errors |
| Gallery browser checks | Passed | Search, the 8-item Git filter, all 70 cards and the 20-item Desktop filter, and 390px layout work |
| Artifact audit | Passed | Mod count, MIT licenses, local imports, screenshot source/content hashes, and local documentation links are consistent |
| Interactive native layout acceptance | Open | Native terminal pixels, Desktop painting, and real keyboard focus for all 70 mods have not been verified |
| GitHub-hosted CI | Blocked before execution | GitHub did not start the job because of an account restriction; no hosted validation steps ran. [Workflow run](https://github.com/whyashthakker/awesome-claude-code-mods/actions/runs/37100619513). |

The original 50 mods each have five native tests: command registration/opening, another pane's isolation, Terminal behavior, Desktop behavior, and a preview capture. The 20 Desktop additions each have seven native tests: command opening, pane isolation, controls at 36 and 84 columns, Terminal/headless compatibility messages, and a Desktop preview capture. Tests use fresh modules and in-memory engine stubs. They do not execute real tools, read real user files, spend model tokens, or touch a real account.

Desktop cases additionally verify SVGs, composable AbovePrompt content and hide/show, missing cost/usage reports, quota countdowns, chosen file reads resolved against workspace cwd, invalid budgets/URLs/JSON, saved board transitions, prompt drafting, timers, and read-only diff argv.

Behavioral cases include missing/oversized files, a real env filename and an env-example symlink refused before reading, invalid input, clipboard and composer actions, persistent collection keys, task toggles/deletions, timer pause/reset behavior, refused calls avoiding downstream dispatch, and read-only argv inspection. Git/file-viewer tests use fixture output; they do not establish portability across every Git or filesystem version.

A CLI smoke run recorded these sanitized engine debug lines:

```text
hooks module context-meter@inline loaded (worker, environment 1, tier user); events: session.start,command.run,ui.render
plugin.register: context-meter (user, context-meter@inline), judged by core alone: admitted
$.command.register (context-meter): /context-meter listed
context-meter (user) answered command.run without next(); nothing beneath it ran for this dispatch
```

The initial release's second smoke run used `--plugin-dir ./mods` and admitted all 50 general plugins. The Desktop expansion repeated the smoke with all 70: 70 unique hooks modules loaded, including 20 Desktop modules, zero module load failures, zero skipped hooks, and the expected Code-tab explanation from `/desktop-usage-strip`. [Sanitized smoke evidence](desktop-smoke-results.json).

The `claude -p` run shows plugin loading and command dispatch; it does not show a pane on that surface.

## Re-run

```sh
claude plugin validate .claude-plugin/marketplace.json --strict
python3 scripts/check.py
python3 scripts/audit.py
```

To regenerate screenshot data after a source or fixture change, use `python3 scripts/check.py --capture-previews`, then the preview/screenshot steps in [SCREENSHOTS.md](SCREENSHOTS.md). Source digests include hooks, native test fixtures, and plugin manifests. The default check run leaves committed previews intact.

The GitHub workflow pins the tested Claude version and runs validation, tests, and the artifact audit. It makes no claims about future mods API versions. When updating the baseline, rerun the same checks and test native layouts on the target apps.
