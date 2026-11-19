#!/usr/bin/env python3
"""
TakeMeter as a local HTTP service.

    python serve.py

Loads the fine-tuned classifier once, then answers:

    GET  /health     is it up, and which model is loaded
    POST /classify   {"text": "..."}  ->  label, confidence, per-label scores
    GET  /docs       FastAPI's built-in page for trying it by hand

Bad input gets a 400 with a JSON body naming what was wrong, never a crash or
a guess. A failure during inference gets a JSON 500 and the server keeps going.

Every /classify call — answered, rejected or crashed — appends one JSON line to
logs/requests.jsonl, and startup appends one too. See LOG FIELDS below.

The model comes from the Hugging Face Hub (v1assets/takemeter-distilbert) and
is cached after the first download. Point TAKEMETER_MODEL at a local folder
(e.g. models/takemeter) to serve a model you just trained instead.
"""

import json
import os
import platform
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import psutil
import torch
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = os.environ.get("TAKEMETER_MODEL", "v1assets/takemeter-distilbert")
HOST = os.environ.get("TAKEMETER_HOST", "127.0.0.1")
PORT = int(os.environ.get("TAKEMETER_PORT", "8000"))
LOG_PATH = Path(os.environ.get("TAKEMETER_LOG", "logs/requests.jsonl"))
MAX_LENGTH = 128  # what the model was trained with — see served_model.json
# Longest post accepted, in characters. The model only reads the first 128
# tokens (~500 characters), so anything past this is almost certainly not a
# post — a pasted log file or a mistake — and is refused rather than truncated.
MAX_CHARS = 10_000
PREVIEW_CHARS = 120  # how much of each input the log keeps

# ── LOG FIELDS ───────────────────────────────────────────────────────────────
# Every line has:   ts (UTC, ISO 8601), event ("startup" | "request"), model
#
# event=startup:    load_seconds   wall time to load tokenizer + model
#                   rss_mb         process memory once loaded
#                   torch_threads, torch_version, python_version, device
#
# event=request:    request_id     8 hex chars, also returned as X-Request-ID
#                   status         HTTP status sent back
#                   error          null, or the error code in the response body
#                                  (empty_text, no_content, text_too_long,
#                                  invalid_request, invalid_json, inference_error)
#                   input_preview  first 120 chars of the text (or raw body, if
#                                  it wasn't valid JSON)
#                   input_chars    length of the text (or raw body)
#                   n_tokens       tokens the model saw (≤ 128); null if rejected
#                   truncated      the post ran past 128 tokens
#                   label, confidence, scores    null unless status is 200
#                   tokenize_ms    tokenizer only
#                   inference_ms   model forward pass + softmax
#                   total_ms       wall time inside the server, request in to
#                                  response out (includes JSON parsing)
#                   cpu_ms         process CPU time (user + system, all threads)
#                                  spent during the request. This is the
#                                  compute cost. Under concurrent requests it
#                                  includes the others' work, so measure it
#                                  one request at a time.
#                   rss_mb         process memory after the request
#                   peak_rss_mb    process peak memory so far (Windows only)

state = {}
_log_lock = threading.Lock()
_proc = psutil.Process()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def write_log(record):
    """Append one record. A logging failure is printed, never raised — the
    request it describes has already been answered."""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with _log_lock, LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"[log] could not write {LOG_PATH}: {exc}")


def cpu_seconds():
    t = _proc.cpu_times()
    return t.user + t.system


def memory_mb():
    info = _proc.memory_info()
    peak = getattr(info, "peak_wset", None)  # Windows exposes the peak; others don't
    return round(info.rss / 1e6, 1), (round(peak / 1e6, 1) if peak else None)


@asynccontextmanager
async def lifespan(app):
    started = time.perf_counter()
    state["tokenizer"] = AutoTokenizer.from_pretrained(MODEL_ID)
    state["model"] = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).eval()
    state["labels"] = [state["model"].config.id2label[i] for i in range(state["model"].config.num_labels)]
    state["load_seconds"] = round(time.perf_counter() - started, 2)
    rss, _ = memory_mb()
    write_log({
        "ts": now_iso(),
        "event": "startup",
        "model": MODEL_ID,
        "load_seconds": state["load_seconds"],
        "rss_mb": rss,
        "torch_threads": torch.get_num_threads(),
        "torch_version": torch.__version__,
        "python_version": platform.python_version(),
        "device": "cpu",
    })
    print(f"Loaded {MODEL_ID} in {state['load_seconds']}s — labels: {', '.join(state['labels'])}")
    print(f"Logging to {LOG_PATH}")
    yield
    state.clear()


app = FastAPI(title="TakeMeter", version="1.0", lifespan=lifespan)


@app.middleware("http")
async def log_classify(request: Request, call_next):
    """Time and record every /classify call, including ones the endpoint never
    sees (bad JSON, wrong shape) and ones that crash inside it."""
    if request.url.path != "/classify":
        return await call_next(request)

    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    request.state.result = {}
    request.state.error = None
    started, cpu_started = time.perf_counter(), cpu_seconds()
    body = await request.body()

    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:
        request.state.error = request.state.error or "inference_error"
        request.state.exception = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        result = request.state.result
        text = result.get("text")
        raw = text if text is not None else body.decode("utf-8", errors="replace")
        rss, peak = memory_mb()
        write_log({
            "ts": now_iso(),
            "event": "request",
            "model": MODEL_ID,
            "request_id": request_id,
            "status": status,
            "error": request.state.error,
            "exception": getattr(request.state, "exception", None),
            "input_preview": raw[:PREVIEW_CHARS],
            "input_chars": len(raw),
            "n_tokens": result.get("n_tokens"),
            "truncated": result.get("truncated"),
            "label": result.get("label"),
            "confidence": result.get("confidence"),
            "scores": result.get("scores"),
            "tokenize_ms": result.get("tokenize_ms"),
            "inference_ms": result.get("inference_ms"),
            "total_ms": round((time.perf_counter() - started) * 1000, 2),
            "cpu_ms": round((cpu_seconds() - cpu_started) * 1000, 1),
            "rss_mb": rss,
            "peak_rss_mb": peak,
        })


class InputError(Exception):
    def __init__(self, error, detail):
        self.error, self.detail = error, detail


def error_body(error, detail):
    return {"error": error, "detail": detail}


@app.exception_handler(InputError)
def input_error(request: Request, exc: InputError):
    request.state.error = exc.error
    return JSONResponse(status_code=400, content=error_body(exc.error, exc.detail))


@app.exception_handler(RequestValidationError)
def invalid_request(request: Request, exc: RequestValidationError):
    # FastAPI's default here is a 422. A body that isn't JSON, or JSON without a
    # string `text`, is the client's mistake — that's a 400.
    if any(e.get("type") == "json_invalid" for e in exc.errors()):
        request.state.error = "invalid_json"
        return JSONResponse(status_code=400, content=error_body("invalid_json", "Request body is not valid JSON."))
    request.state.error = "invalid_request"
    return JSONResponse(
        status_code=400,
        content=error_body("invalid_request", 'Body must be a JSON object like {"text": "<post>"}.'),
    )


@app.exception_handler(Exception)
def unexpected_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=error_body("inference_error", f"{type(exc).__name__}: {exc}"))


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    request_id: str
    label: str
    confidence: float
    scores: dict[str, float]
    truncated: bool
    latency_ms: float


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_ID,
        "labels": state["labels"],
        "load_seconds": state["load_seconds"],
        "torch_threads": torch.get_num_threads(),
        "log": str(LOG_PATH),
    }


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest, request: Request):
    # A plain `def`, not `async def`: FastAPI runs it in a worker thread, so a
    # slow inference doesn't block the event loop.
    started = time.perf_counter()
    result = request.state.result
    text = req.text.strip()
    result["text"] = text
    if not text:
        raise InputError("empty_text", "`text` is empty or only whitespace.")
    if len(text) > MAX_CHARS:
        raise InputError("text_too_long", f"`text` is {len(text)} characters; the limit is {MAX_CHARS}.")

    # One tokenizer pass: any overflow comes back as extra rows, so more than
    # one row means the model only saw the first MAX_LENGTH tokens.
    # The rows can differ in length, so they stay lists until we keep the first.
    t0 = time.perf_counter()
    encoded = state["tokenizer"](
        text, truncation=True, max_length=MAX_LENGTH, return_overflowing_tokens=True,
    )
    truncated = len(encoded["input_ids"]) > 1
    inputs = {k: torch.tensor(encoded[k][:1]) for k in ("input_ids", "attention_mask")}
    t1 = time.perf_counter()

    # The capstone improvement. `strip()` above only knows about whitespace, so
    # text made of characters the tokenizer throws away (null bytes, other
    # control characters) got past it, and the model classified nothing but
    # its own [CLS] and [SEP]. Judge emptiness by what the model would read.
    content_tokens = len(encoded["input_ids"][0]) - state["tokenizer"].num_special_tokens_to_add()
    if content_tokens < 1:
        result.update(n_tokens=len(encoded["input_ids"][0]), tokenize_ms=round((t1 - t0) * 1000, 2))
        raise InputError("no_content", "`text` has no characters the model can read.")

    with torch.inference_mode():
        logits = state["model"](**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1).tolist()
    t2 = time.perf_counter()

    best = max(range(len(probs)), key=probs.__getitem__)
    scores = {l: round(p, 4) for l, p in zip(state["labels"], probs)}
    result.update(
        n_tokens=int(inputs["input_ids"].shape[1]),
        truncated=truncated,
        label=state["labels"][best],
        confidence=round(probs[best], 4),
        scores=scores,
        tokenize_ms=round((t1 - t0) * 1000, 2),
        inference_ms=round((t2 - t1) * 1000, 2),
    )
    return ClassifyResponse(
        request_id=request.state.request_id,
        label=result["label"],
        confidence=result["confidence"],
        scores=scores,
        truncated=truncated,
        latency_ms=round((time.perf_counter() - started) * 1000, 2),
    )


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
