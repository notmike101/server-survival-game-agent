# SERVER SURVIVAL — COMPACT PLAYBOOK

Run `python ledger.py h` first; SQLite is the compact source of truth. Goal: live score `S >= 500000`.

## Rules / controls

- Browser is agent-owned. Use Playwright locators + CUA clicks/screenshots only.
  `tab.playwright.evaluate()` is read-only; never call/mutate game functions there.
- Fresh run: visible `Start Survival` = `startGame()`; visible `Skip Tutorial` =
  `tutorial.skip()`. Pause before canvas edits. `#tool-delete` is the real
  Demolish selector (not `#tool-demolish`).
- Fast is legitimate: from paused state click `#btn-fast` once (this starts
  about 3x simulation immediately), wait about 3 sec, click `#btn-pause`, wait
  200-250 ms, then read HUD. Clicking `#btn-play` after Fast resets to normal
  speed. Log `S,$,R,L,F` and visible event text each chunk.

## Winning graph (green edges required)

```
I -> WAF -> API(T3) -> ALB -> {Comp*,Srv*}
I -> CDN -> S3
{Comp,Srv} -> {Cache -> NoSQL, NoSQL, S3, Search}
```

- WAF works; keep it as Internet entry. API must be behind WAF (entry routing
  prefers WAF). Never put active traffic through SQS: fixed processing cap `50`
  and hidden WAF->SQS bypass caused saturation/failures. Delete unused SQS.
- Search is required for SEARCH; NoSQL is READ/WRITE only. Keep direct handler
  edges as well as Cache->NoSQL. CDN/S3 handles STATIC; handler/S3 handles UPLOAD.

## Cost-efficient build order

Starter fits `$500`: `WAF40 + API70 + ALB50 + Srv45 + CDN60 + S325 + NoSQL80 + Search120 = $490` (`$10` left).

1. Link/verify starter; normal 8-sec proof; then Fast chunks.
2. Add Srv2 `$45` when affordable; same ALB + NoSQL/S3/Search fan-out.
3. Add Cache `$60`; link both handler types -> Cache and Cache -> NoSQL.
4. Add Comp1/Comp2 `$60` each; link ALB + Cache/NoSQL/S3/Search. Upgrade each
   via visible hover arrow: T1->T2 `$100` (cap `4->10`), T2->T3 `$160` (cap18).
5. Upgrade API via visible arrows: T2 `$120` (rate80), T3 `$200` (cap160/rate200).
   Upgrade Cache/NoSQL/Search only after handler capacity and budget are safe.

## Fast diagnosis

- Normal capacities: Srv cap30, Comp T1/T2/T3=`4/10/18`, API T1/T3=`60/160`
  with rate `30/200`, Cache T1/T3=`30/80` (hit `35/65%`), NoSQL T1=`15`,
  Search T1=`12`.
- If health is 100% but failures jump, inspect `#active-event-text` and
  `#active-event-timer`: events include CAPACITY_DROP (-60% caps), TRAFFIC_BURST
  (4x RPS), SERVICE_OUTAGE, COST_SPIKE. Pause immediately; do not assume
  healthy services means no global event.
- If SQS tooltip shows `50/50` while API/ALB are light, remove SQS with
  `#tool-delete`; stale tooltip text may remain, so verify screenshot + health list.
- Repair damaged nodes with normal click UI; keep auto-repair ON. Recalibrate
  coordinates after every reflow using screenshot + Select tooltip probes.

## Current live handoff (update this line after each major chunk)

Run 1 max-load failure is stored as rule/run data in `strategy.sqlite`; do not
reload the narrative. Run `python ledger.py h` for current run/state/rules/next.
Current run2 is fresh at `t=0`, `$10`, `R=100%`, starter placed/unlinked; next
action and all new telemetry must be written with `ledger.py`.

## Last known viewport coordinates (reprobe if changed; CSS/viewport, scrollY=0)

`I(582,424) WAF(405,270) API(798,410) ALB(439,580) Srv1(655,650)`
`Srv2(655,820) Comp1(405,800) Comp2(264,849) Cache(905,810)`
`NoSQL(905,680) Search(1190,680) S3(1190,269)`.
