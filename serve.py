#!/usr/bin/env python3
"""
TakeMeter as a local HTTP service.

    python serve.py

Loads the fine-tuned classifier once, then answers:

    GET  /health     is it up, and which model is loaded
    POST /classify   {"text": "..."}  ->  label, confidence, per-label scores
    GET  /docs       FastAPI's built-in page for trying it by hand

The model comes from the Hugging Face Hub (v1assets/takemeter-distilbert) and
is cached after the first download. Point TAKEMETER_MODEL at a local folder
(e.g. models/takemeter) to serve a model you just trained instead.
"""

import os
import time
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = os.environ.get("TAKEMETER_MODEL", "v1assets/takemeter-distilbert")
HOST = os.environ.get("TAKEMETER_HOST", "127.0.0.1")
PORT = int(os.environ.get("TAKEMETER_PORT", "8000"))
MAX_LENGTH = 128  # what the model was trained with — see served_model.json

state = {}


@asynccontextmanager
async def lifespan(app):
    started = time.perf_counter()
    state["tokenizer"] = AutoTokenizer.from_pretrained(MODEL_ID)
    state["model"] = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).eval()
    state["labels"] = [state["model"].config.id2label[i] for i in range(state["model"].config.num_labels)]
    state["load_seconds"] = round(time.perf_counter() - started, 2)
    print(f"Loaded {MODEL_ID} in {state['load_seconds']}s — labels: {', '.join(state['labels'])}")
    yield
    state.clear()


app = FastAPI(title="TakeMeter", version="1.0", lifespan=lifespan)


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    label: str
    confidence: float
    scores: dict[str, float]
    latency_ms: float


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_ID,
        "labels": state["labels"],
        "load_seconds": state["load_seconds"],
        "torch_threads": torch.get_num_threads(),
    }


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    # A plain `def`, not `async def`: FastAPI runs it in a worker thread, so a
    # slow inference doesn't block the event loop.
    started = time.perf_counter()
    inputs = state["tokenizer"](
        req.text, truncation=True, max_length=MAX_LENGTH, return_tensors="pt"
    )
    with torch.inference_mode():
        logits = state["model"](**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1).tolist()
    best = max(range(len(probs)), key=probs.__getitem__)
    return ClassifyResponse(
        label=state["labels"][best],
        confidence=round(probs[best], 4),
        scores={l: round(p, 4) for l, p in zip(state["labels"], probs)},
        latency_ms=round((time.perf_counter() - started) * 1000, 2),
    )


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
