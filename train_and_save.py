#!/usr/bin/env python3
"""
Train the model the service serves, and save it.

    python train_and_save.py

This is the notebook's improved configuration (unit 6, The Improvement):
class-weighted loss, seed 2024 — the best of the three "after" seeds. The
notebook trains and throws the model away; this keeps it.

Writes:
    models/takemeter/       the model and tokenizer (gitignored, ~255 MB)
    served_model.json       what was trained, on what, and how it scored —
                            committed, so the served model has a record

Publish it to the Hub with the hf CLI (see RUNNING.md):

    hf upload v1assets/takemeter-distilbert models/takemeter .
"""

import json
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

# Same values as takemeter.ipynb, section 2.
LABELS = ["troubleshooting", "recommendation_request", "release_showcase"]
BASE_MODEL = "distilbert-base-uncased"
EPOCHS = 3
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 128
SEED = 2024

CSV = "labels.csv"
OUT_DIR = Path("models/takemeter")
RECORD = Path("served_model.json")
HUB_REPO = "v1assets/takemeter-distilbert"


def split_dataset(df, seed, test_size=0.15, val_size=0.15):
    """Stratified 70/15/15 — copied from the notebook so the split matches."""
    def _stratify_on(frame):
        counts = frame["label"].value_counts()
        return frame["label"] if counts.min() >= 2 else None

    rest, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=_stratify_on(df)
    )
    val_share = val_size / (1 - test_size)
    train, val = train_test_split(
        rest, test_size=val_share, random_state=seed, stratify=_stratify_on(rest)
    )
    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def to_ids(df, labels):
    lookup = {label: i for i, label in enumerate(labels)}
    out = df.copy()
    out["labels"] = out["label"].astype(str).str.strip().map(lookup)
    return out[["text", "labels"]]


def compute_metrics(eval_pred):
    logits, gold = eval_pred
    predicted = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(gold, predicted),
        "f1_macro": f1_score(gold, predicted, average="macro", zero_division=0),
    }


class WeightedTrainer(Trainer):
    """Trainer whose loss weights each label, so a rare label costs more to miss."""

    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        weight = self.class_weights.to(outputs.logits.device)
        loss = torch.nn.functional.cross_entropy(outputs.logits, labels, weight=weight)
        return (loss, outputs) if return_outputs else loss


def main():
    started = time.perf_counter()
    df = pd.read_csv(CSV)
    train_df, val_df, test_df = split_dataset(df, SEED)
    print(f"train {len(train_df)} · val {len(val_df)} · test {len(test_df)}")

    set_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(LABELS),
        id2label={i: l for i, l in enumerate(LABELS)},
        label2id={l: i for i, l in enumerate(LABELS)},
    )

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=MAX_LENGTH)

    train_ds = Dataset.from_pandas(to_ids(train_df, LABELS)).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(to_ids(val_df, LABELS)).map(tokenize, batched=True)
    test_ds = Dataset.from_pandas(to_ids(test_df, LABELS)).map(tokenize, batched=True)

    counts = train_df["label"].astype(str).str.strip().value_counts()
    n, k = len(train_df), len(LABELS)
    class_weights = torch.tensor([n / (k * counts[l]) for l in LABELS], dtype=torch.float)
    print("Class weights:", {l: round(float(w), 2) for l, w in zip(LABELS, class_weights)})

    args = TrainingArguments(
        output_dir="./takemeter_out",
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=10,
        seed=SEED,
        report_to="none",
    )
    trainer = WeightedTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        class_weights=class_weights,
    )
    trainer.train()

    test_metrics = trainer.evaluate(test_ds, metric_key_prefix="test")
    print(f"test accuracy {test_metrics['test_accuracy']:.3f}   macro F1 {test_metrics['test_f1_macro']:.3f}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(OUT_DIR))
    tokenizer.save_pretrained(str(OUT_DIR))
    size_mb = sum(p.stat().st_size for p in OUT_DIR.rglob("*") if p.is_file()) / 1e6

    record = {
        "hub_repo": HUB_REPO,
        "base_model": BASE_MODEL,
        "labels": LABELS,
        "seed": SEED,
        "weight_classes": True,
        "class_weights": {l: round(float(w), 4) for l, w in zip(LABELS, class_weights)},
        "epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "batch_size": BATCH_SIZE,
        "max_length": MAX_LENGTH,
        "n_train": len(train_df),
        "n_val": len(val_df),
        "n_test": len(test_df),
        "test_accuracy": round(test_metrics["test_accuracy"], 4),
        "test_f1_macro": round(test_metrics["test_f1_macro"], 4),
        "model_size_mb": round(size_mb, 1),
        "device": str(trainer.args.device),
        "torch_version": torch.__version__,
        "python_version": platform.python_version(),
        "train_seconds": round(time.perf_counter() - started, 1),
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {OUT_DIR} ({size_mb:.1f} MB). Wrote {RECORD}.")


if __name__ == "__main__":
    main()
