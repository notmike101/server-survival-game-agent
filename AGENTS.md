# Server Survival operator contract

Goal: reach live score `S >= 500000` at
`https://pshenok.github.io/server-survival/`. Do not stop before that target.

## Mandatory first action

```powershell
cd D:\server-survival
python ledger.py h
python ledger.py audit
```

`strategy.sqlite` is the source of truth. `h` prints compact JSON containing
the active run, next action, verified rules, and recent observations. `s` prints
only the current state. The old long AGENTS history is compressed in SQLite
archive key `AGENTS.md`; do not restore it into context.

If `audit` fails, do not play. Remove the unsafe active rule with
`python ledger.py qdel KEY`, record the correction, and commit the SQLite file.

## Mandatory driver

Do not invent browser JavaScript or canvas coordinates. Read
`playwright/README.md`, then use Playwright `browser_run_code_unsafe` with the
checked-in `filename` scripts in numeric order. The scripts use visible controls
and real mouse input. If `h` says the current run is finished, run
`python ledger.py fresh` once.
Do not rely on screenshots for context, you MUST use the browser where possible for any validation. If you do take any screenshots, delete them once you're done processing them.

Start:

```json
{"filename":"D:\\server-survival\\playwright\\00_start_survival.js"}
{"filename":"D:\\server-survival\\playwright\\01_build_starter.js"}
{"filename":"D:\\server-survival\\playwright\\02_prove_starter.js"}
```

Record work with the ledger, not prose dumps:

```powershell
python ledger.py o --t T --s S --b B --rep R --l L --f F --ev EVENT --act ACTION --out RESULT
python ledger.py a --t T --x ACTION --why REASON --res RESULT
python ledger.py next "NEXT ACTION"
python ledger.py q --k KEY --x "RULE" --c CATEGORY --p 100
python ledger.py topo "SHORT GRAPH"
python ledger.py finish --out SCORE500K
```

Use `o` for every meaningful chunk/edit and `q` only for reusable rules.
Keep the active `next` string current. A successor should need one `h` call,
not a history scan.

If the sqlite file is in a git repository, commit your change to the sqlite after the work is recorded in the ledger. This is important to do for auditability and a backup of the history. Failure to do this will result in a failure and you will be banned from playing the game if you do not do this.

## Browser/safety contract

- Do not play any mode other than SURVIVAL. Do not play sandbox or campaign.
- Use the agent-owned real browser tab only; never take over the user's other
  session. Use Playwright locators and real Playwright mouse clicks.
  `browser_evaluate`/`tab.playwright.evaluate()` is read-only observation only:
  never click, dispatch events, hide overlays, write storage, call game
  functions, or mutate `STATE` there.
- Never use `STATE`, `setTimeScale`, `createService`, `createConnection`, direct
  money/upkeep changes, synthetic DOM events, or timer callbacks to play. A
  ledger rule that recommends any of these is corrupt even if marked verified.
- Start through the visible `Start Survival` control (the required
  `startGame()` flow), then the visible `Skip Tutorial` control (the required
  `tutorial.skip()` flow). Fresh retries use the visible `Start Fresh` control.
- Pause before placing, linking, upgrading, or demolishing. Verify screenshots
  and HUD after edits. `#tool-delete` is the real demolish selector.
- Fast mode is legitimate and efficient: from paused state click visible
  `#btn-fast`, wait about 3 real seconds, click `#btn-pause`, wait 200-250ms,
  read HUD, and record `o`. Clicking Play after Fast resets normal speed.
  Use short batches (<=4 fast chunks) and verify Pause after each batch.
- Correctly dissmiss the game over screen at the end of an attempt. This is the equivalent to clicking the "Start Fresh" button on the game. Failure to do this is considered cheating and you will be banned from playing the game. It is extremely important that you do this.
- Correctly dismiss the tutorial screen before you start a round if it is showing. Failure to do this is considered cheating and you will be banned from playing the game. It is extremely important that you do this.

## Verified game strategy

- Valid core: `Internet->WAF->API->ALB->{Serverless,Compute}`;
  `Internet->CDN->Storage`; every handler -> `Cache,NoSQL,Storage,Search`;
  Cache -> every NoSQL. WAF is functional in deployed v2.1 and blocks DDoS.
- Cheapest complete starter is `$490`: WAF40 + API70 + ALB50 + Serverless45
  + CDN60 + Storage25 + NoSQL80 + Search120. Prove it for 8 seconds before
  buying anything. Then add Serverless2, Cache, Compute, and upgrades.
- `NoSQL` handles READ/WRITE; `Search` handles SEARCH; Storage handles
  STATIC/UPLOAD; CDN handles STATIC. Keep green edges and direct handler
  destinations as well as cache edges.
- A live max-load failure at `52.2 RPS` killed a graph with two T2 NoSQL,
  T3 Cache, T3 Compute, and two Serverless: 48 READ, 25 WRITE, 21 SEARCH,
  4 UPLOAD, and 4 fraud leaks. Health was still 100%. Therefore buy/link
  **3-4 T2 NoSQL** and add/upgrade Search before the 10-minute maximum.
- A second NoSQL visibly stopped a SERVICE OUTAGE's RD/WR failure stream.
  Redundancy is required; do not assume health100 means capacity is safe.
- Cache T3 is cap80/hit65 and improves score. Keep it after handlers and
  before all DBs. Keep auto-repair enabled through normal UI.
- Do not use SQS by default. Prior live evidence showed a hidden WAF->SQS path
  and a fixed `50/50` queue saturation; if testing SQS normally, delete it
  immediately when saturation/failures appear.
- Events include COST_SPIKE, CAPACITY_DROP, TRAFFIC_BURST, and SERVICE_OUTAGE.
  Visible event banners plus failure deltas outrank green health indicators.
  DDoS banners with WAF and zero failure delta are safe; continue monitoring.

## Current continuation

Run `python ledger.py h` and `python ledger.py audit`. Continue with the numeric
scripts in `playwright/`, log returned HUD state in SQLite, and use only this
file plus `PLAYBOOK.compact.md` for durable operating rules.
