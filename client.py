#!/usr/bin/env python3
"""
Drive the running TakeMeter service and summarise what it logged.

    python serve.py                      # in one terminal
    python client.py --label trial1      # in another

Sends every post in test_split.csv (30, with known labels) plus a fixed set of
bad inputs, one request at a time. Then it reads logs/requests.jsonl, keeps
only the records whose request_id came back to it, and summarises them —
so the numbers come from the server's own log, not from the client's clock.

Writes runs/<label>.json with the summary and every request's outcome.

    --repeat N         send the post set N times (default 1)
    --no-bad           skip the bad inputs
    --concurrency N    N requests in flight at once (default 1). cpu_ms in the
                       log is per process, so it is only a clean per-request
                       cost at concurrency 1.
    --rate R           at most R requests per second overall (default: as fast
                       as the server answers)

Only the standard library and pandas — nothing new to install.
"""

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

# Each is (name, raw body, status the service should answer with, content type).
# A body is str (sent as UTF-8) or bytes (sent as is). Content type None sends
# no Content-Type header at all.
JSON = "application/json"
BAD_INPUTS = [
    ("empty_text", '{"text": ""}', 400, JSON),
    ("whitespace_text", '{"text": "   \\n\\t  "}', 400, JSON),
    ("missing_field", "{}", 400, JSON),
    ("wrong_type", '{"text": 5}', 400, JSON),
    ("invalid_json", "{text", 400, JSON),
    ("not_an_object", '"just a string"', 400, JSON),
    ("too_long", json.dumps({"text": "word " * 2500}), 400, JSON),
    # Added for the capstone trials (criterion 2), from probing the service.
    ("null_text", '{"text": null}', 400, JSON),
    ("list_text", '{"text": ["a"]}', 400, JSON),
    ("no_content_type", '{"text": "my game crashes on startup"}', 400, None),
    ("text_plain", '{"text": "my game crashes on startup"}', 400, "text/plain"),
    ("empty_body", "", 400, JSON),
    ("non_utf8_body", b'{"text": "\xff\xfe broken bytes"}', 400, JSON),
    ("nul_only_text", '{"text": "\\u0000\\u0000"}', 400, JSON),
]


def post(url, body, timeout, content_type=JSON):
    """Send one request. Returns (status, request_id, parsed body or None, client_ms)."""
    data = body if isinstance(body, bytes) else body.encode("utf-8")
    headers = {"Content-Type": content_type} if content_type else {}
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, headers, raw = resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as err:
        status, headers, raw = err.code, err.headers, err.read()
    except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
        return None, None, {"client_error": str(err)}, round((time.perf_counter() - started) * 1000, 2)
    client_ms = round((time.perf_counter() - started) * 1000, 2)
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    return status, headers.get("X-Request-ID"), parsed, client_ms


def build_jobs(posts, repeat, include_bad):
    jobs = []
    for r in range(repeat):
        for i, row in posts.iterrows():
            jobs.append({
                "kind": "post", "name": f"post_{i}", "expected_label": row["label"],
                "expected_status": 200, "body": json.dumps({"text": row["text"]}),
                "content_type": JSON,
            })
        if include_bad:
            for name, body, expected, content_type in BAD_INPUTS:
                jobs.append({"kind": "bad", "name": name, "expected_label": None,
                             "expected_status": expected, "body": body,
                             "content_type": content_type})
    return jobs


def read_log(path, request_ids):
    records = {}
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("event") == "request" and rec.get("request_id") in request_ids:
                records[rec["request_id"]] = rec
    return records


def pct(values, q):
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return round(values[lo] + (values[hi] - values[lo]) * (k - lo), 2)


def summarise(outcomes, log):
    ok = [o for o in outcomes if o["kind"] == "post"]
    bad = [o for o in outcomes if o["kind"] == "bad"]
    logged = [log[o["request_id"]] for o in outcomes if o["request_id"] in log]
    ok_logged = [r for r in logged if r["status"] == 200]
    total_ms = [r["total_ms"] for r in ok_logged]
    cpu_ms = [r["cpu_ms"] for r in ok_logged]
    statuses = {}
    for o in outcomes:
        statuses[str(o["status"])] = statuses.get(str(o["status"]), 0) + 1
    answered = [o for o in ok if o["status"] == 200]
    return {
        "sent": len(outcomes),
        "status_counts": statuses,
        "logged": len(logged),
        "missing_from_log": [o["request_id"] or o["name"] for o in outcomes if o["request_id"] not in log],
        "posts_sent": len(ok),
        "posts_answered_200": len(answered),
        "accuracy": round(sum(o["label"] == o["expected_label"] for o in answered) / len(answered), 4) if answered else None,
        "bad_sent": len(bad),
        "bad_got_expected_status": sum(o["status"] == o["expected_status"] for o in bad),
        "bad_logged_with_error_code": sum(
            1 for o in bad if o["request_id"] in log and log[o["request_id"]].get("error")
        ),
        "server_total_ms": {
            "p50": pct(total_ms, 0.5), "p95": pct(total_ms, 0.95),
            "max": max(total_ms) if total_ms else None,
            "mean": round(statistics.mean(total_ms), 2) if total_ms else None,
        },
        "client_ms_p50": pct([o["client_ms"] for o in answered], 0.5),
        "cpu_ms_mean": round(statistics.mean(cpu_ms), 1) if cpu_ms else None,
        "cpu_ms_p95": pct(cpu_ms, 0.95),
        "truncated": sum(1 for r in ok_logged if r.get("truncated")),
        "peak_rss_mb": max((r["peak_rss_mb"] or r["rss_mb"] for r in logged), default=None),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="names the output file: runs/<label>.json")
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--csv", default="test_split.csv")
    ap.add_argument("--log", default="logs/requests.jsonl")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--no-bad", action="store_true")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--rate", type=float, default=None)
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    try:
        with urllib.request.urlopen(f"{args.url}/health", timeout=5) as resp:
            health = json.load(resp)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Service not reachable at {args.url} ({exc}). Start it with: python serve.py")

    posts = pd.read_csv(args.csv)
    jobs = build_jobs(posts, args.repeat, not args.no_bad)
    interval = 1.0 / args.rate if args.rate else 0.0
    print(f"Sending {len(jobs)} requests to {args.url} "
          f"(concurrency {args.concurrency}, rate {args.rate or 'unlimited'}/s)")

    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.perf_counter()

    def run(indexed):
        i, job = indexed
        if interval:
            delay = t0 + i * interval - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
        status, rid, body, client_ms = post(f"{args.url}/classify", job["body"], args.timeout, job["content_type"])
        return {
            "kind": job["kind"], "name": job["name"], "status": status, "request_id": rid,
            "expected_status": job["expected_status"], "expected_label": job["expected_label"],
            "label": (body or {}).get("label"), "error": (body or {}).get("error") or (body or {}).get("client_error"),
            "client_ms": client_ms,
        }

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        outcomes = list(pool.map(run, enumerate(jobs)))
    wall_s = round(time.perf_counter() - t0, 2)

    time.sleep(0.2)  # let the last log lines land
    log = read_log(Path(args.log), {o["request_id"] for o in outcomes if o["request_id"]})
    summary = summarise(outcomes, log)
    summary.update(wall_seconds=wall_s, achieved_rate_per_s=round(len(jobs) / wall_s, 2))

    out = Path("runs") / f"{args.label}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "label": args.label, "started_at": started_at, "health": health,
        "args": vars(args), "summary": summary, "outcomes": outcomes,
    }, indent=2) + "\n", encoding="utf-8")

    s = summary
    print(f"\nstatus counts       {s['status_counts']}")
    print(f"logged              {s['logged']} of {s['sent']}"
          + (f"   MISSING: {s['missing_from_log']}" if s["missing_from_log"] else ""))
    print(f"posts answered 200  {s['posts_answered_200']} of {s['posts_sent']}   accuracy {s['accuracy']}")
    if s["bad_sent"]:
        print(f"bad inputs          {s['bad_got_expected_status']} of {s['bad_sent']} got the expected status, "
              f"{s['bad_logged_with_error_code']} logged with an error code")
    print(f"server total_ms     p50 {s['server_total_ms']['p50']}  p95 {s['server_total_ms']['p95']}  "
          f"max {s['server_total_ms']['max']}")
    print(f"cpu_ms per request  mean {s['cpu_ms_mean']}  p95 {s['cpu_ms_p95']}")
    print(f"peak memory         {s['peak_rss_mb']} MB")
    print(f"wall                {s['wall_seconds']} s  ({s['achieved_rate_per_s']} req/s)")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
