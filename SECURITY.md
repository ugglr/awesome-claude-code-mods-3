# Security and data access

Claude Code mods run with the permissions of the user. Review the source and `claude plugin validate mods/<name> --strict` output before loading one. Validation lists events and engine calls; it does not establish that a mod is safe.

The 50 bundled mods make no network requests, call no models, and approve no permission prompts. Git inspection mods start read-only Git processes through argv arrays when requested. Viewers read user-selected paths with explicit size limits. Workspace tools store user-entered notes in Claude Code's local plugin store. Clipboard operations and composer drafts are explicit button actions.

The [community listings](docs/COMMUNITY_MODS.md) describe external projects reviewed through their authors' documentation. Their access differs: some make network or model calls, start processes, or automatically submit queued prompts. They are not covered by this collection's bundled-plugin tests or access claims. Each listing names relevant behavior and prerequisites; we have not run or security-audited those projects.

Tool errors, Bash command arguments, filenames, Git metadata, and user-entered notes can contain private information. Avoid entering secrets into a mod, and review a screenshot before sharing it. The committed screenshots contain only test fixtures.

`read-only-mode` is a reminder guard over selected built-in tools, not a sandbox or access-control boundary. MCP tools, other mods, and alternate tools may still write. `scope-watch` checks a string prefix and observes only Edit/Write calls; it is advisory. `env-example` checks the selected filename, refuses symlink example files, and displays names rather than values. It is not a general secret scanner.

`regex-lab` accepts a limited pattern subset: character classes, anchors, escapes, and at most one repetition operator. Groups, alternation, and backreferences are refused. This keeps arbitrary backtracking patterns out of the shared worker. It is not a replacement for testing the full regex engine in your application.

For a security report, contact the repository owner through GitHub's private vulnerability reporting if available, or open an issue containing a minimal reproduction without secrets. The MIT warranty disclaimer applies.
