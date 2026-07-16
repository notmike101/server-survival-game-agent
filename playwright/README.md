# Deterministic Playwright driver

These files are for weak agents. They use only visible game controls and real
Playwright mouse clicks. They never call game functions, write `STATE`, alter
upkeep, hide modals, or write local storage.

## Exact Zcode usage

Navigate to the game once, then run files through Playwright's
`browser_run_code_unsafe` `filename` argument. Use absolute Windows paths:

If `python ledger.py h` reports a finished run, first run
`python ledger.py fresh` exactly once. Do not call it when a run is active.

```json
{"filename":"D:\\server-survival\\playwright\\00_start_survival.js"}
{"filename":"D:\\server-survival\\playwright\\01_build_starter.js"}
{"filename":"D:\\server-survival\\playwright\\02_prove_starter.js"}
```

After the build file, call `browser_take_screenshot` and inspect the nine green
edges. After the proof, repeat `03_fast_chunk.js`, record every returned HUD
with `ledger.py o`, and commit `strategy.sqlite`. Never run more than four Fast
chunks without a screenshot/HUD audit.

When cash is at least `$105`, run `04_add_serverless_cache.js` exactly once.
Then screenshot and continue Fast chunks. If the result says `GAME_OVER`, run
`05_start_fresh.js`; this visibly dismisses the result screen. Never navigate or
reload around a game-over screen.

`read_hud.js` is a read-only observation helper. Do not compose new inline
`browser_evaluate` code. In particular, do not click elements, dispatch events,
hide overlays, call game functions, or touch `STATE` from evaluation.

## Stop conditions

- Any file error: stop and inspect a screenshot. Do not improvise coordinates.
- Placement money does not match: the click missed; start fresh normally.
- Proof has any failure or reputation below 100%: an edge is missing; screenshot.
- Game-over modal: visibly run `05_start_fresh.js` before any retry.
- Score at least 500000: record HUD, `ledger.py finish --out SCORE500K`, commit.
