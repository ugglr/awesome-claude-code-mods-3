#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
mods=json.loads((ROOT/'catalog.json').read_text())
intro='''# Awesome Claude Code Mods

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

'''
out=intro
for category in dict.fromkeys(m['category'] for m in mods):
 group=[m for m in mods if m['category']==category]
 out+=f'### {category} · {len(group)} mods\n\n| Mod | Use case | Preview |\n| --- | --- | --- |\n'
 for m in group:
  out+=f"| [{m['title']}](mods/{m['id']}/README.md) | {m['description']} | [![{m['title']} preview](assets/screenshots/{m['id']}.png)](assets/screenshots/{m['id']}.png) |\n"
 out+='\n'
out+='''## How the collection behaves

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
'''
(ROOT/'README.md').write_text(out)
print('Built README with',len(mods),'screenshot-linked entries')
