import argparse
import json
import sqlite3
import zlib
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).with_name("strategy.sqlite")
FORBIDDEN_RULE_TEXT = (
    "state.",
    "settimescale",
    "upkeepenabled",
    "createservice",
    "createconnection",
    "localstorage",
)
SQL = """
CREATE TABLE IF NOT EXISTS r(id INTEGER PRIMARY KEY,lab TEXT UNIQUE,st TEXT,t REAL,s REAL,b REAL,rep REAL,l REAL,f INTEGER,fb TEXT,topo TEXT,out TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS o(id INTEGER PRIMARY KEY,rid INTEGER,t REAL,s REAL,b REAL,rep REAL,l REAL,f INTEGER,ev TEXT,act TEXT,out TEXT,proof TEXT,ts TEXT);
CREATE TABLE IF NOT EXISTS a(id INTEGER PRIMARY KEY,rid INTEGER,t REAL,x TEXT,why TEXT,res TEXT,ts TEXT);
CREATE TABLE IF NOT EXISTS k(k TEXT PRIMARY KEY,v TEXT,ts TEXT);
CREATE TABLE IF NOT EXISTS q(k TEXT PRIMARY KEY,c TEXT,x TEXT,e TEXT,p INTEGER,ts TEXT);
CREATE TABLE IF NOT EXISTS z(k TEXT PRIMARY KEY,v BLOB,n INTEGER,ts TEXT);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def C():
    x = sqlite3.connect(DB)
    x.row_factory = sqlite3.Row
    x.executescript(SQL)
    return x


def K(x, key, value=None):
    if value is None:
        z = x.execute("SELECT v FROM k WHERE k=?", (key,)).fetchone()
        return z[0] if z else None
    x.execute("INSERT INTO k(k,v,ts) VALUES(?,?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v,ts=excluded.ts", (key, value, now()))


def run_id(x, supplied=None):
    return supplied or int(K(x, "run"))


def flags(p):
    for n, typ in (("t", float), ("s", float), ("b", float), ("rep", float), ("l", float), ("f", int)):
        p.add_argument("--" + n, type=typ)
    p.add_argument("--fb")
    p.add_argument("--id", type=int)


def state(a):
    return {k: v for k, v in (("t", a.t), ("s", a.s), ("b", a.b), ("rep", a.rep), ("l", a.l), ("f", a.f), ("fb", a.fb)) if v is not None}


def sync(x, rid, d):
    names = {"t": "t", "s": "s", "b": "b", "rep": "rep", "l": "l", "f": "f", "fb": "fb"}
    u = {names[k]: v for k, v in d.items() if k in names}
    if u:
        x.execute("UPDATE r SET " + ",".join(k + "=?" for k in u) + " WHERE id=?", [*u.values(), rid])
    K(x, "state", json.dumps(d, separators=(",", ":")))


def seed(_):
    x = C()
    if x.execute("SELECT 1 FROM r LIMIT 1").fetchone():
        print("exists")
        return
    t = now()
    x.execute("INSERT INTO r(lab,st,t,s,b,rep,l,f,fb,topo,out,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", ("max-fail-1", "F", 606, 95152.5, 2930, 0, 52.2, 102, "FL4/RD48/WR25/UP4/SR21", "WAF/API/ALB/CompT3/Srv2/CacheT3/NoSQLT2x2/SearchT1", "rep0", "max-load READ capacity/missing paths"))
    x.execute("INSERT INTO r(lab,st,t,s,b,rep,l,f,topo,note) VALUES(?,?,?,?,?,?,?,?,?,?)", ("retry-2", "A", 0, 0, 10, 100, 1.0, 0, "starter placed/unlinked", "fresh visible restart; scale DB before max"))
    rid = x.execute("SELECT id FROM r WHERE lab='retry-2'").fetchone()[0]
    rules = [("route", "WAF->API->ALB; CDN->S3; handler->Cache/DB/Search/S3", "verified", 100), ("starter", "$490: W40 A70 L50 Srv45 CDN60 S325 NoSQL80 Search120", "verified", 100), ("max", "52.2 RPS killed 2x NoSQLT2: RD48; target 3-4 NoSQLT2 + Search", "verified", 100), ("redundancy", "link every handler to every NoSQL; second DB stopped outage RD/WR", "verified", 98), ("cache", "CacheT3 cap80 hit65; handler->Cache->all DBs", "verified", 90), ("fast", "paused: Fast->wait~3s->Pause; Play resets normal", "verified", 95), ("events", "health100 can coexist with outage/capacity failure; trust banner+failure delta", "verified", 95), ("sqs", "avoid SQS; WAF->SQS hidden path saturated 50/50", "verified", 90), ("search", "SearchT1 had SR21 at max; upgrade/add before 10m", "verified", 88)]
    for k, v, e, p in rules:
        x.execute("INSERT INTO q(k,c,x,e,p,ts) VALUES(?,?,?,?,?,?)", (k, "rule", v, e, p, t))
    K(x, "run", str(rid))
    K(x, "next", "link starter; 8s proof; add Srv2/Cache/Compute; buy 3-4 NoSQLT2 + Search before 10m")
    d = {"t": 0, "s": 0, "b": 10, "rep": 100, "l": 1.0, "f": 0}
    K(x, "state", json.dumps(d, separators=(",", ":")))
    x.execute("INSERT INTO o(rid,t,s,b,rep,l,f,act,proof,ts) VALUES(?,?,?,?,?,?,?,?,?,?)", (rid, 0, 0, 10, 100, 1.0, 0, "placed starter; paused", "8 services visible; unlinked", t))
    x.commit()
    print(json.dumps({"db": str(DB), "run": rid}, separators=(",", ":")))


def observe(a):
    x = C(); rid = run_id(x, a.id); d = state(a)
    x.execute("INSERT INTO o(rid,t,s,b,rep,l,f,ev,act,out,proof,ts) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (rid, d.get("t"), d.get("s"), d.get("b"), d.get("rep"), d.get("l"), d.get("f"), a.ev, a.act, a.out, a.proof, now()))
    sync(x, rid, d); x.commit()
    print(json.dumps({"o": x.execute("SELECT last_insert_rowid()").fetchone()[0], "run": rid}, separators=(",", ":")))


def action(a):
    x = C(); rid = run_id(x, a.id)
    x.execute("INSERT INTO a(rid,t,x,why,res,ts) VALUES(?,?,?,?,?,?)", (rid, a.t, a.x, a.why, a.res, now())); x.commit()
    print(json.dumps({"a": x.execute("SELECT last_insert_rowid()").fetchone()[0], "run": rid}, separators=(",", ":")))


def rule(a):
    x = C(); x.execute("INSERT INTO q(k,c,x,e,p,ts) VALUES(?,?,?,?,?,?) ON CONFLICT(k) DO UPDATE SET c=excluded.c,x=excluded.x,e=excluded.e,p=excluded.p,ts=excluded.ts", (a.k, a.c, a.x, a.e, a.p, now())); x.commit(); print(a.k)


def delete_rule(a):
    x = C(); cur = x.execute("DELETE FROM q WHERE k=?", (a.k,)); x.commit()
    print(json.dumps({"deleted": cur.rowcount, "key": a.k}, separators=(",", ":")))


def audit(_):
    x = C(); bad = []
    for row in x.execute("SELECT k,x FROM q ORDER BY k"):
        lowered = row["x"].lower()
        hits = [token for token in FORBIDDEN_RULE_TEXT if token in lowered]
        if hits:
            bad.append({"key": row["k"], "tokens": hits})
    result = {
        "ok": not bad,
        "unsafe_rules": bad,
        "driver": str(Path(__file__).with_name("playwright") / "README.md"),
    }
    print(json.dumps(result, separators=(",", ":")))
    if bad:
        raise SystemExit(2)


def handoff(_):
    x = C(); rid = int(K(x, "run")); r = x.execute("SELECT id,lab,st,t,s,b,rep,l,f,fb,topo FROM r WHERE id=?", (rid,)).fetchone()
    rules = [f"{z['k']}:{z['x']}" for z in x.execute("SELECT k,x FROM q ORDER BY p DESC,ts DESC LIMIT 9")]
    obs = [dict(z) for z in x.execute("SELECT t,s,b,rep,l,f,ev,act FROM o ORDER BY id DESC LIMIT 4")]
    print(json.dumps({
        "run": dict(r),
        "next": K(x, "next") or "",
        "safety": "run audit; UI only; never mutate STATE/game functions",
        "driver": str(Path(__file__).with_name("playwright") / "README.md"),
        "rules": rules,
        "obs": obs,
    }, separators=(",", ":")))


def newrun(a):
    x = C(); x.execute("INSERT INTO r(lab,st,t,s,b,rep,l,f,topo,note) VALUES(?,?,?,?,?,?,?,?,?,?)", (a.lab, "A", 0, 0, 500, 100, 1, 0, a.topo, a.note)); rid = x.execute("SELECT last_insert_rowid()").fetchone()[0]; K(x, "run", str(rid)); x.commit(); print(rid)


def fresh_run(_):
    x = C(); current = x.execute("SELECT id,st FROM r WHERE id=?", (int(K(x, "run")),)).fetchone()
    if current and current["st"] == "A":
        print(json.dumps({"ok": False, "error": "active run already exists", "run": current["id"]}, separators=(",", ":")))
        raise SystemExit(2)
    label = "ui-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    x.execute("INSERT INTO r(lab,st,t,s,b,rep,l,f,topo,note) VALUES(?,?,?,?,?,?,?,?,?,?)", (label, "A", 0, 0, 500, 100, 1, 0, "fresh UI run", "created by ledger fresh"))
    rid = x.execute("SELECT last_insert_rowid()").fetchone()[0]
    K(x, "run", str(rid)); K(x, "next", "run playwright/00_start_survival.js")
    sync(x, rid, {"t": 0, "s": 0, "b": 500, "rep": 100, "l": 1, "f": 0})
    x.commit(); print(json.dumps({"ok": True, "run": rid, "lab": label}, separators=(",", ":")))


def finish(a):
    x = C(); rid = run_id(x, a.id); x.execute("UPDATE r SET st='F',out=? WHERE id=?", (a.out, rid)); x.commit(); print(rid)


def next_action(a):
    x = C(); K(x, "next", a.text); x.commit(); print("ok")


def topology(a):
    x = C(); rid = run_id(x, a.id); x.execute("UPDATE r SET topo=? WHERE id=?", (a.text, rid)); x.commit(); print("ok")


def archive(a):
    data = Path(a.path).read_bytes(); x = C(); x.execute("INSERT OR REPLACE INTO z(k,v,n,ts) VALUES(?,?,?,?)", (a.key, sqlite3.Binary(zlib.compress(data, 9)), len(data), now())); x.commit(); print(json.dumps({"key": a.key, "bytes": len(data)}, separators=(",", ":")))


p = argparse.ArgumentParser(add_help=False); sp = p.add_subparsers(dest="cmd", required=True)
sp.add_parser("seed"); sp.add_parser("h"); sp.add_parser("s"); sp.add_parser("fresh")
o = sp.add_parser("o"); flags(o); o.add_argument("--ev"); o.add_argument("--act"); o.add_argument("--out"); o.add_argument("--proof")
a = sp.add_parser("a"); a.add_argument("--id", type=int); a.add_argument("--t", type=float); a.add_argument("--x", required=True); a.add_argument("--why", default=""); a.add_argument("--res", default="")
q = sp.add_parser("q"); q.add_argument("--k", required=True); q.add_argument("--c", default="rule"); q.add_argument("--x", required=True); q.add_argument("--e", default=""); q.add_argument("--p", type=int, default=50)
qd = sp.add_parser("qdel"); qd.add_argument("k")
sp.add_parser("audit")
n = sp.add_parser("new"); n.add_argument("--lab", required=True); n.add_argument("--topo", default=""); n.add_argument("--note", default="")
f = sp.add_parser("finish"); f.add_argument("--id", type=int); f.add_argument("--out", required=True)
n = sp.add_parser("next"); n.add_argument("text")
t = sp.add_parser("topo"); t.add_argument("text"); t.add_argument("--id", type=int)
z = sp.add_parser("arch"); z.add_argument("path"); z.add_argument("--key", default="AGENTS.md")
args = p.parse_args()
if args.cmd == "seed": seed(args)
elif args.cmd == "h": handoff(args)
elif args.cmd == "s": print(K(C(), "state") or "{}")
elif args.cmd == "o": observe(args)
elif args.cmd == "a": action(args)
elif args.cmd == "q": rule(args)
elif args.cmd == "qdel": delete_rule(args)
elif args.cmd == "audit": audit(args)
elif args.cmd == "new": newrun(args)
elif args.cmd == "fresh": fresh_run(args)
elif args.cmd == "finish": finish(args)
elif args.cmd == "next": next_action(args)
elif args.cmd == "topo": topology(args)
elif args.cmd == "arch": archive(args)
