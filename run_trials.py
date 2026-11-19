#!/usr/bin/env python3
"""
Run the five capstone criteria (criteria.md) three times and score them.

    python run_trials.py --label before

Each trial is independent: it starts its own `serve.py`, writing its own log,
drives it, scores it, and stops it. Nothing changes between trials.

One trial:
  1. Start `python serve.py` with TAKEMETER_LOG=runs/<label>/trial-N.jsonl and
     wait for /health.
  2. Send one warm-up post, so the server counts as "already running" for
     criterion 1. The warm-up is still a request, so criterion 3 counts it.
  3. Send the 30 posts in test_split.csv and the 14 bad inputs in client.py,
     ten times over, one request at a time: 300 valid + 140 bad = 440
     requests of continuous serving (criterion 4).
  4. Score every criterion from that trial's log and the client's outcomes.

How each criterion is measured (decided before the first trial was run):
  1. Valid requests, after the warm-up, whose client round-trip time (what
     the caller waits, measured in client.py) is under 100 ms. Target: at
     least 9 of 10, i.e. >= 90%. Server total_ms is reported beside it.
  2. The 14 bad inputs x 10. Target: every one gets a 400; none gets a 500.
  3. Every request sent, warm-up included, has a log record with its
     request_id. A request that got no response (no request_id) counts as
     missing. Target: 100%.
  4. Highest peak_rss_mb in the trial's log. Target: <= 750 MB.
  5. Of the 30 distinct test posts (first pass), how many the log marks
     truncated. Target: <= 40%.

Writes runs/<label>/trial-N.jsonl (the server's log), runs/<label>/trial-N.json
(every outcome) and runs/<label>/summary.json, and prints the run-log table.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

import client

URL = "http://127.0.0.1:8000"
REPEAT = 10

C1_MS, C1_RATE = 100.0, 0.90
C4_MB = 750.0
C5_RATE = 0.40


def wait_for_health(proc, timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            sys.exit(f"serve.py exited with code {proc.returncode} before it was ready")
        try:
            with urllib.request.urlopen(f"{URL}/health", timeout=2) as resp:
                return json.load(resp)
        except Exception:  # noqa: BLE001
            time.sleep(0.5)
    proc.kill()
    sys.exit("serve.py did not become ready in time")


def run_trial(label, n, posts):
    out_dir = Path("runs") / label
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"trial-{n}.jsonl"
    log_path.unlink(missing_ok=True)

    env = dict(os.environ, TAKEMETER_LOG=str(log_path), PYTHONIOENCODING="utf-8")
    server_out = open(out_dir / f"trial-{n}.server.txt", "w", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, "serve.py"], env=env, stdout=server_out, stderr=subprocess.STDOUT)
    try:
        health = wait_for_health(proc)

        warm_status, warm_id, _, warm_ms = client.post(
            f"{URL}/classify", json.dumps({"text": posts.iloc[0]["text"]}), 30
        )
        warmup = {"kind": "warmup", "name": "warmup", "status": warm_status,
                  "request_id": warm_id, "client_ms": warm_ms}

        outcomes = []
        for job in client.build_jobs(posts, REPEAT, include_bad=True):
            status, rid, body, client_ms = client.post(
                f"{URL}/classify", job["body"], 30, job["content_type"]
            )
            outcomes.append({
                "kind": job["kind"], "name": job["name"], "status": status, "request_id": rid,
                "expected_status": job["expected_status"], "expected_label": job["expected_label"],
                "label": (body or {}).get("label"),
                "error": (body or {}).get("error") or (body or {}).get("client_error"),
                "client_ms": client_ms,
            })
        time.sleep(0.3)  # let the last log lines land
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        server_out.close()

    sent = [warmup] + outcomes
    log = client.read_log(log_path, {o["request_id"] for o in sent if o["request_id"]})
    startup = [json.loads(l) for l in log_path.open(encoding="utf-8") if '"event": "startup"' in l]

    valid = [o for o in outcomes if o["kind"] == "post"]
    bad = [o for o in outcomes if o["kind"] == "bad"]

    # 1 — warm latency, client round-trip
    under = [o for o in valid if o["status"] == 200 and o["client_ms"] < C1_MS]
    server_ms = sorted(log[o["request_id"]]["total_ms"] for o in valid if o["request_id"] in log)
    c1 = {
        "under_100ms": len(under), "of": len(valid), "rate": round(len(under) / len(valid), 4),
        "client_ms_p50": client.pct([o["client_ms"] for o in valid], 0.5),
        "client_ms_p95": client.pct([o["client_ms"] for o in valid], 0.95),
        "client_ms_max": max(o["client_ms"] for o in valid),
        "server_ms_p50": client.pct(server_ms, 0.5),
        "server_ms_p95": client.pct(server_ms, 0.95),
        "slowest": sorted(
            ({"request_id": o["request_id"], "name": o["name"], "client_ms": o["client_ms"],
              "server_ms": log.get(o["request_id"], {}).get("total_ms"),
              "n_tokens": log.get(o["request_id"], {}).get("n_tokens")} for o in valid),
            key=lambda x: -x["client_ms"],
        )[:5],
        "met": len(under) / len(valid) >= C1_RATE,
    }

    # 2 — bad input gets a 400, never a 500
    by_name = {}
    for o in bad:
        by_name.setdefault(o["name"], []).append(o["status"])
    got_400 = sum(o["status"] == 400 for o in bad)
    got_500 = sum(o["status"] is not None and o["status"] >= 500 for o in bad)
    c2 = {
        "got_400": got_400, "of": len(bad), "got_500": got_500,
        "not_400": {name: s for name, s in by_name.items() if any(x != 400 for x in s)},
        "met": got_400 == len(bad) and got_500 == 0,
    }

    # 3 — every request is logged
    missing = [o.get("request_id") or o["name"] for o in sent if o["request_id"] not in log]
    c3 = {"logged": len(sent) - len(missing), "of": len(sent), "missing": missing, "met": not missing}

    # 4 — peak memory
    peaks = [r.get("peak_rss_mb") or r.get("rss_mb") for r in log.values()]
    c4 = {
        "peak_rss_mb": max(peaks),
        "startup_rss_mb": startup[0]["rss_mb"] if startup else None,
        "met": max(peaks) <= C4_MB,
    }

    # 5 — truncation on the 30 distinct posts (first pass)
    first_pass = valid[: len(posts)]
    trunc = [o for o in first_pass if log.get(o["request_id"], {}).get("truncated")]
    c5 = {
        "truncated": len(trunc), "of": len(first_pass),
        "rate": round(len(trunc) / len(first_pass), 4),
        "met": len(trunc) / len(first_pass) <= C5_RATE,
    }

    result = {
        "trial": n, "health": health, "warmup": warmup,
        "load_seconds": startup[0]["load_seconds"] if startup else None,
        "requests_sent": len(sent),
        "accuracy": round(sum(o["label"] == o["expected_label"] for o in valid if o["status"] == 200)
                          / max(1, sum(o["status"] == 200 for o in valid)), 4),
        "criteria": {"1": c1, "2": c2, "3": c3, "4": c4, "5": c5},
    }
    (out_dir / f"trial-{n}.json").write_text(
        json.dumps({**result, "outcomes": sent}, indent=2) + "\n", encoding="utf-8"
    )
    return result


def cell(n, c):
    return {
        "1": lambda: f"{c['under_100ms']}/{c['of']}",
        "2": lambda: f"{c['got_400']}/{c['of']}",
        "3": lambda: f"{c['logged']}/{c['of']}",
        "4": lambda: f"{c['peak_rss_mb']} MB",
        "5": lambda: f"{c['truncated']}/{c['of']}",
    }[n]()


ROWS = {
    "1": ("1. Fast responses once the server is running", "≥ 90% under 100 ms"),
    "2": ("2. Bad input gets a 400, never a 500", "all 400, zero 500"),
    "3": ("3. Every request is logged", "100%"),
    "4": ("4. Memory stays under 750 MB", "≤ 750 MB peak"),
    "5": ("5. Most posts fit in the 128-token limit", "≤ 40% truncated"),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="e.g. before / after — names runs/<label>/")
    ap.add_argument("--trials", type=int, default=3)
    args = ap.parse_args()

    try:
        urllib.request.urlopen(f"{URL}/health", timeout=1)
        sys.exit(f"Something is already answering on {URL}. Stop it first — each trial starts its own server.")
    except Exception:  # noqa: BLE001
        pass

    posts = pd.read_csv("test_split.csv")
    results = []
    for n in range(1, args.trials + 1):
        print(f"Trial {n} of {args.trials}…", flush=True)
        r = run_trial(args.label, n, posts)
        results.append(r)
        print("   " + "  ".join(f"C{k} {cell(k, v)} {'MET' if v['met'] else 'MISSED'}"
                                for k, v in r["criteria"].items()), flush=True)

    summary = {"label": args.label, "trials": [{k: v for k, v in r.items()} for r in results]}
    Path("runs", args.label, "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"\n| Criterion | Target | " + " | ".join(f"Run {r['trial']}" for r in results) + " | Verdict |")
    print("|---|---|" + "---|" * len(results) + "---|")
    for k, (name, target) in ROWS.items():
        cells = [cell(k, r["criteria"][k]) for r in results]
        verdict = "MET" if all(r["criteria"][k]["met"] for r in results) else "MISSED"
        print(f"| {name} | {target} | " + " | ".join(cells) + f" | {verdict} |")
    print(f"\nWrote runs/{args.label}/")


if __name__ == "__main__":
    main()
