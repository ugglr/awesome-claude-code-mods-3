# Screenshot provenance

Every mod has a PNG under `assets/screenshots/`, linked from its README. These are screenshots of local browser previews of **actual render trees produced by Claude Code's native test kit**. They use in-memory fixture data. The browser applies the preview styling; these images are not captures of the Claude Code Terminal or Desktop application.

The distinction appears inside every screenshot, in every mod README, in the gallery, and in the root README. A valid native-kit tree does not prove the app paints that layout correctly.

## Reproduce

1. Install Claude Code 2.1.288 and Python 3.10+.
2. Run `python3 scripts/check.py --capture-previews`. Each plugin's screenshot test drives its real hooks, mounts a terminal pane, uses relevant controls, and emits its full native-kit element tree. The runner saves it to `assets/previews/<name>.json`, removes ephemeral UI handle IDs, and records a source digest.
3. Run `python3 scripts/render-previews.py`. This paints that captured tree into a local HTML page, with escaped text, and builds `gallery.html`. It does not reimplement the mod's calculations or fabricate its output.
4. Install screenshot tooling with `python3 -m pip install -r scripts/requirements-screenshots.txt` in your own environment. Use an installed Chrome, or run `python3 -m playwright install chromium` and pass that binary's path.
5. Run `python3 scripts/screenshots.py --browser /path/to/chrome`. It opens each preview in isolated headless Chromium, captures its `#capture` element, and verifies gallery search, filtering, and a 390px mobile layout.
6. Run `python3 scripts/audit.py` to check that all 50 mod screenshots, snapshots, manifests, licenses, and links are present and current.

On macOS the screenshot script defaults to `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. Set `MODS_BROWSER` or use `--browser` elsewhere.

The fixture project is available in [examples/demo](../examples/demo). Tokens, quota windows, agent metadata, Git output, and command results in previews are fixture values, not live account or production measurements. UUID previews contain randomly generated values from the mod.

For native painting and keyboard acceptance, launch `claude --plugin-dir ./mods/<name>` in a trusted project, run the command, and verify it on your target app. Terminal and Desktop Code tab layouts may differ. Interactive native layout acceptance has not been completed for all 50 mods.
