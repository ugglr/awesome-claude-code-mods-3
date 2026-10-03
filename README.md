# Awesome Claude Code Mods

**50 useful mods. Pick one. Install it. Keep working.**

This repository was inspired by the [Claude Code Mods guide on ExplainX.ai](https://www.explainx.ai/blog/claude-code-mods-typescript-plugins-guide-2026).

Independent, MIT-licensed plugins for Git inspection, session diagnostics, local file viewers, workspace notes, text utilities, and workflow controls. Each comes with working source, native Claude Code tests, install instructions, an access description, and a screenshot.

![Six mod previews](assets/screenshots/collection.png)

*Screenshots show actual mod render trees captured by Claude Code's test kit with fixture data, painted in a browser preview. They are not native Claude Code app captures. [Screenshot provenance](docs/SCREENSHOTS.md).*

[Searchable gallery (open locally)](gallery.html) · [Research and existing mods](docs/RESEARCH.md) · [Validation](docs/VALIDATION.md) · [Contribute](CONTRIBUTING.md)

## Start in under a minute

Requires Claude Code **2.1.287+**. Tested with **2.1.288**. Mods are enabled by default; no early-access environment flag is needed. Works in the CLI and the Desktop **Code** tab. The VS Code chat panel and `claude -p` run hooks but do not show mod panes. [Official overview](https://code.claude.com/docs/en/plugins/mods/overview).

```sh
claude plugin marketplace add whyashthakker/awesome-claude-code-mods
claude plugin install task-board@awesome-claude-code-mods
```

In Claude Code, run `/reload-plugins` if your session is already open, then `/task-board`. Type a task, press Enter to save, and use the task button to mark it done. Tab moves between controls; Esc closes a pane. Ctrl+X then Tab returns keyboard focus to a pane.

Try a mod directly from source:

```sh
git clone https://github.com/whyashthakker/awesome-claude-code-mods.git
cd awesome-claude-code-mods
claude --plugin-dir ./mods/context-meter
```

Then run `/context-meter`. Replace `context-meter` with any folder below. You can install several independently; each command uses its mod's name. No runtime dependencies or build step. Git tools require Git on PATH; package viewers expect a package.json in your project or a path you choose.

These are executable mods, not a list of prompts or skills. Research links document the ecosystem; the 50 implementations here are original, and some use cases overlap with existing mods.

## Choose a mod

The screenshot in every row opens at full resolution. Each name links to its README, usage, access details, and source.

### Session · 8 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [Context Meter](mods/context-meter/README.md) | See the current context window fill and remaining tokens. | [![Context Meter preview](assets/screenshots/context-meter.png)](assets/screenshots/context-meter.png) |
| [Quota Watch](mods/quota-watch/README.md) | Inspect reported plan windows and their reset times. | [![Quota Watch preview](assets/screenshots/quota-watch.png)](assets/screenshots/quota-watch.png) |
| [Cache Inspector](mods/cache-inspector/README.md) | Track API cache reads, writes, and uncached input by request. | [![Cache Inspector preview](assets/screenshots/cache-inspector.png)](assets/screenshots/cache-inspector.png) |
| [Tool Timing](mods/tool-timing/README.md) | Measure observed tool latency, call counts, and failures. | [![Tool Timing preview](assets/screenshots/tool-timing.png)](assets/screenshots/tool-timing.png) |
| [Error Inbox](mods/error-inbox/README.md) | Keep the last 30 failed or refused tool calls in one pane. | [![Error Inbox preview](assets/screenshots/error-inbox.png)](assets/screenshots/error-inbox.png) |
| [Edit Heatmap](mods/edit-heatmap/README.md) | Count successful Edit and Write calls by path. | [![Edit Heatmap preview](assets/screenshots/edit-heatmap.png)](assets/screenshots/edit-heatmap.png) |
| [Turn Timeline](mods/turn-timeline/README.md) | Show duration, token totals, and interruption state per turn. | [![Turn Timeline preview](assets/screenshots/turn-timeline.png)](assets/screenshots/turn-timeline.png) |
| [Agent Board](mods/agent-board/README.md) | Inspect the subagents reported by the session. | [![Agent Board preview](assets/screenshots/agent-board.png)](assets/screenshots/agent-board.png) |

### Git · 8 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [Branch Board](mods/branch-board/README.md) | Inspect local branches, upstreams, and dirty files. | [![Branch Board preview](assets/screenshots/branch-board.png)](assets/screenshots/branch-board.png) |
| [Staged Review](mods/staged-review/README.md) | Review the staged diff before committing. | [![Staged Review preview](assets/screenshots/staged-review.png)](assets/screenshots/staged-review.png) |
| [Commit Browser](mods/commit-browser/README.md) | Browse the latest 20 commits with author and subject. | [![Commit Browser preview](assets/screenshots/commit-browser.png)](assets/screenshots/commit-browser.png) |
| [Stash Browser](mods/stash-browser/README.md) | List stashes and inspect a selected stash diff. | [![Stash Browser preview](assets/screenshots/stash-browser.png)](assets/screenshots/stash-browser.png) |
| [Worktree Map](mods/worktree-map/README.md) | List worktree paths, branches, and locked states. | [![Worktree Map preview](assets/screenshots/worktree-map.png)](assets/screenshots/worktree-map.png) |
| [Conflict Radar](mods/conflict-radar/README.md) | List unresolved paths and count conflict markers in tracked files. | [![Conflict Radar preview](assets/screenshots/conflict-radar.png)](assets/screenshots/conflict-radar.png) |
| [Blame View](mods/blame-view/README.md) | Read authorship for the first 80 lines of a chosen tracked file. | [![Blame View preview](assets/screenshots/blame-view.png)](assets/screenshots/blame-view.png) |
| [Ignore Check](mods/ignore-check/README.md) | Explain which Git ignore rule matches a path. | [![Ignore Check preview](assets/screenshots/ignore-check.png)](assets/screenshots/ignore-check.png) |

### Repository · 10 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [File Tree](mods/file-tree/README.md) | Browse one directory at a time with clickable folders. | [![File Tree preview](assets/screenshots/file-tree.png)](assets/screenshots/file-tree.png) |
| [Package Scripts](mods/package-scripts/README.md) | List npm scripts and package identity without running them. | [![Package Scripts preview](assets/screenshots/package-scripts.png)](assets/screenshots/package-scripts.png) |
| [Dependency Table](mods/dependency-table/README.md) | Inspect dependency groups from a package manifest. | [![Dependency Table preview](assets/screenshots/dependency-table.png)](assets/screenshots/dependency-table.png) |
| [TODO Finder](mods/todo-finder/README.md) | Find TODO, FIXME, and HACK notes in tracked files. | [![TODO Finder preview](assets/screenshots/todo-finder.png)](assets/screenshots/todo-finder.png) |
| [Markdown Map](mods/markdown-map/README.md) | Build a heading outline with source line numbers. | [![Markdown Map preview](assets/screenshots/markdown-map.png)](assets/screenshots/markdown-map.png) |
| [JSON Browser](mods/json-browser/README.md) | Summarize top-level JSON keys with types and a formatted preview. | [![JSON Browser preview](assets/screenshots/json-browser.png)](assets/screenshots/json-browser.png) |
| [CSV Table](mods/csv-table/README.md) | Preview quoted CSV fields, row counts, and column headers. | [![CSV Table preview](assets/screenshots/csv-table.png)](assets/screenshots/csv-table.png) |
| [Log Viewer](mods/log-viewer/README.md) | Show the last 60 lines of a small local log with an optional filter. | [![Log Viewer preview](assets/screenshots/log-viewer.png)](assets/screenshots/log-viewer.png) |
| [Env Example](mods/env-example/README.md) | List variable names and missing placeholders in an example env file. | [![Env Example preview](assets/screenshots/env-example.png)](assets/screenshots/env-example.png) |
| [File Compare](mods/file-compare/README.md) | Compare two small text files by line without editing either. | [![File Compare preview](assets/screenshots/file-compare.png)](assets/screenshots/file-compare.png) |

### Workspace · 8 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [Scratchpad](mods/scratchpad/README.md) | Save short notes beside your conversation. | [![Scratchpad preview](assets/screenshots/scratchpad.png)](assets/screenshots/scratchpad.png) |
| [Task Board](mods/task-board/README.md) | Add tasks and toggle done status. | [![Task Board preview](assets/screenshots/task-board.png)](assets/screenshots/task-board.png) |
| [Decision Log](mods/decision-log/README.md) | Record dated engineering decisions. | [![Decision Log preview](assets/screenshots/decision-log.png)](assets/screenshots/decision-log.png) |
| [Snippet Shelf](mods/snippet-shelf/README.md) | Save and copy short code or command snippets. | [![Snippet Shelf preview](assets/screenshots/snippet-shelf.png)](assets/screenshots/snippet-shelf.png) |
| [Link Shelf](mods/link-shelf/README.md) | Save labeled HTTP and HTTPS reference links. | [![Link Shelf preview](assets/screenshots/link-shelf.png)](assets/screenshots/link-shelf.png) |
| [Prompt Shelf](mods/prompt-shelf/README.md) | Save reusable prompts and put one into the composer as a draft. | [![Prompt Shelf preview](assets/screenshots/prompt-shelf.png)](assets/screenshots/prompt-shelf.png) |
| [Release Checklist](mods/release-checklist/README.md) | Keep a persistent checklist for a release. | [![Release Checklist preview](assets/screenshots/release-checklist.png)](assets/screenshots/release-checklist.png) |
| [Handoff Notes](mods/handoff-notes/README.md) | Keep a dated list of progress and next steps, then copy it. | [![Handoff Notes preview](assets/screenshots/handoff-notes.png)](assets/screenshots/handoff-notes.png) |

### Utilities · 10 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [Regex Lab](mods/regex-lab/README.md) | Test a regular expression against text and see matched ranges. | [![Regex Lab preview](assets/screenshots/regex-lab.png)](assets/screenshots/regex-lab.png) |
| [JSON Format](mods/json-format/README.md) | Validate and pretty-print JSON without touching a file. | [![JSON Format preview](assets/screenshots/json-format.png)](assets/screenshots/json-format.png) |
| [URL Lab](mods/url-lab/README.md) | Inspect URL components and decoded query parameters locally. | [![URL Lab preview](assets/screenshots/url-lab.png)](assets/screenshots/url-lab.png) |
| [Base64 Lab](mods/base64-lab/README.md) | Encode UTF-8 text or decode strict Base64. | [![Base64 Lab preview](assets/screenshots/base64-lab.png)](assets/screenshots/base64-lab.png) |
| [Time Lab](mods/time-lab/README.md) | Convert Unix seconds, milliseconds, or an ISO date to UTC. | [![Time Lab preview](assets/screenshots/time-lab.png)](assets/screenshots/time-lab.png) |
| [Hash Lab](mods/hash-lab/README.md) | Calculate SHA-256, SHA-384, or SHA-512 for UTF-8 text. | [![Hash Lab preview](assets/screenshots/hash-lab.png)](assets/screenshots/hash-lab.png) |
| [Color Lab](mods/color-lab/README.md) | Convert hex colors and measure contrast against a background. | [![Color Lab preview](assets/screenshots/color-lab.png)](assets/screenshots/color-lab.png) |
| [UUID Lab](mods/uuid-lab/README.md) | Generate up to 20 random UUID v4 values locally. | [![UUID Lab preview](assets/screenshots/uuid-lab.png)](assets/screenshots/uuid-lab.png) |
| [Text Counter](mods/text-counter/README.md) | Count words, lines, Unicode code points, and UTF-8 bytes. | [![Text Counter preview](assets/screenshots/text-counter.png)](assets/screenshots/text-counter.png) |
| [ASCII Flipbook](mods/ascii-flipbook/README.md) | Play a local text animation whose frames are separated by a form feed. | [![ASCII Flipbook preview](assets/screenshots/ascii-flipbook.png)](assets/screenshots/ascii-flipbook.png) |

### Workflow · 6 mods

| Mod | Use case | Preview |
| --- | --- | --- |
| [Focus Clock](mods/focus-clock/README.md) | Run a 25-minute focus countdown with pause, reset, and a toast. | [![Focus Clock preview](assets/screenshots/focus-clock.png)](assets/screenshots/focus-clock.png) |
| [Stopwatch](mods/stopwatch/README.md) | Time a task with start, pause, and lap markers. | [![Stopwatch preview](assets/screenshots/stopwatch.png)](assets/screenshots/stopwatch.png) |
| [Test Ledger](mods/test-ledger/README.md) | Record likely test, lint, and build commands and their tool status. | [![Test Ledger preview](assets/screenshots/test-ledger.png)](assets/screenshots/test-ledger.png) |
| [Command History](mods/command-history/README.md) | Keep the last 40 Bash command strings and copy one for reuse. | [![Command History preview](assets/screenshots/command-history.png)](assets/screenshots/command-history.png) |
| [Scope Watch](mods/scope-watch/README.md) | Warn when observed file edits leave a chosen path prefix. | [![Scope Watch preview](assets/screenshots/scope-watch.png)](assets/screenshots/scope-watch.png) |
| [Read-only Mode](mods/read-only-mode/README.md) | Toggle a reminder guard that refuses built-in mutating tools and Bash. | [![Read-only Mode preview](assets/screenshots/read-only-mode.png)](assets/screenshots/read-only-mode.png) |

## How the collection behaves

- Panes open when you run a command. Refresh and input controls act on your request.
- Git inspectors run read-only argv commands. File viewers read bounded, user-chosen paths. They do not edit your repository.
- Workspace tools save user-entered items in each plugin's local store, partitioned by working directory. Clipboard and composer-draft actions require a button press.
- Session diagnostics observe activity from the moment they load. They do not reconstruct earlier turns, and their history resets on reload.
- No mod makes network requests, calls a model, auto-submits a prompt, messages a session, or approves permission prompts. No paid service is needed.

Mods run with your user permissions. Tool error text, command arguments, and notes may be sensitive; inspect what you share. `read-only-mode` and `scope-watch` are convenience guards with explicit limits, not security boundaries. [Access and security](SECURITY.md).

## Verify and develop

```sh
claude plugin validate mods/task-board --strict
claude plugin test mods/task-board
python3 scripts/check.py
python3 scripts/audit.py
```

The collection passed **50 strict plugin validations and 250 native tests** on Claude Code 2.1.288, including controls on both Terminal and Desktop surfaces. The marketplace also passed strict validation. Browser checks cover the gallery's search, filtering, and mobile width. [Check output and limits](docs/VALIDATION.md).

The test kit verifies behavior and valid element trees. Interactive native pixel/layout acceptance for all 50 mods remains open. Screenshot regeneration uses development-only Python tooling; see [Contributing](CONTRIBUTING.md).

Disable or uninstall an installed mod in `/plugin` → **Installed**. Develop against `--plugin-dir`, since installed plugin versions are cached. When publishing a change, bump its version and the marketplace entry together.

## License

[MIT](LICENSE), including a copy in every plugin folder. This is a community project and is not affiliated with Anthropic.
