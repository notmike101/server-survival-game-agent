# Server Survival operator contract

Goal: reach live score `S >= 500000` at
`https://pshenok.github.io/server-survival/`. Do not stop before that target.

## Mandatory first action

```powershell
cd D:\server-survival
python ledger.py h
```

`strategy.sqlite` is the source of truth. `h` prints compact JSON containing
the active run, next action, verified rules, and recent observations. `s` prints
only the current state. The old long AGENTS history is compressed in SQLite
archive key `AGENTS.md`; do not restore it into context.

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

If the sqlite file is in a git repository, commit your change after the work is recorded in the ledger.

## Browser/safety contract

- Do not play any mode other than SURVIVAL. Do not play sandbox or campaign.
- Use the agent-owned real browser tab only; never take over the user's other
  session. Use JavaScript + Playwright/CUA. `tab.playwright.evaluate()` is
  read-only observation only: never call game functions or mutate state there.
- Start through the visible `Start Survival` control (the required
  `startGame()` flow), then the visible `Skip Tutorial` control (the required
  `tutorial.skip()` flow). Fresh retries use the visible `Start Fresh` control.
- Pause before placing, linking, upgrading, or demolishing. Verify screenshots
  and HUD after edits. `#tool-delete` is the real demolish selector.
- Fast mode is legitimate and efficient: from paused state click visible
  `#btn-fast`, wait about 3 real seconds, click `#btn-pause`, wait 200-250ms,
  read HUD, and record `o`. Clicking Play after Fast resets normal speed.
  Use short batches (<=4 fast chunks) and verify Pause after each batch.
- Correctly dissmiss the game over screen and tutorial screens before you start a round. Failure to do this is considered cheating and you will be banned from playing the game. It is extremely important that you do this.

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

Run `python ledger.py h`; it currently owns the fresh retry state, topology,
cash, and next purchase. Continue the browser run, log state in SQLite, and
only use this file for durable operating rules.
