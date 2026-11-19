# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

This project trains TakeMeter to classify user posts from the **r/gta5modding** subreddit community. r/gta5modding is a public forum where Grand Theft Auto V players, modders, and tool developers interact.

### Candidate Distinctions Observed

From reading posts in the community, I noticed the following types of content:

1. **Crashes / Error inquiries:** Some posts explicitly paste error popups, ScriptHookV logs, crash codes, or ask how to fix game launch failures.
2. **Mod requests & recommendations:** Other posts do not have a broken game, but rather ask the community what mods exist for specific gameplay enhancements.
3. **Releases & Project collaborations:** Some posts share links to new mods, GitHub repositories, tools, or announce projects looking for contributors.

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `troubleshooting`

**Definition:** Troubleshooting posts feature a user reporting an issue (crash, error, bug) and is asking the community for help or a solution to fix it.

**Example 1:** "

> This might be a long shot but I've tried literally everything I can think of to fix this for 2 days now. I've started with a clean gtaV install on the latest update build with just lspdfr installed. I purchased the thinlinesanctuary duty gear and lbv packs from his website and installed one of them into my mods folder with openIV and added it to my dlclist and it crashes my game every time, either when I load lspdfr through the rage console or load eup through the rage console and try to open the EUP menu. The dev just told me it's because the game ran out of memory but I have heapadjuster, packfile limit adjuster and game config xml installed and one small duty belt pack shouldn't cause my game to run out of memory. If anyone can help I'd be eternally grateful."

**Example 2:**

> I have a AMD RYZEN 3 3200G 4-Core 3.6GHz (4.0 GHz Turbo) APU w/ Radeon Vega 8 Graphics and GIGABYTE GeForce GTX 1050 2GB Graphics Card and I installed some little mods like (Ls life)(pull me over)(home invasion)(better chases)(stolen) no texture mods and kept everything at normal in settings. Can I get help

### `recommendation_request`

**Definition:** Users are asking the community for suggestions, recommendations, or advice on mod selection.

**Example 1:**

> Can someone pls recommend me some mods for the enhanced version of gta 5. I want the mods to be story friendly and controller friendly. Ive already got Nve and gore variety installed and it would be great if id just have to drag the mods into my onigiri folder and not make a 50gb mods folder

**Example 2:**

> So I'm lowkey getting bored of Online's constant need for moneh grind and I want to add a few mods to single player (legacy version) and play. So I need good mod recommendations.

If it is possible, I would like to somehow play as an OC I created in singleplayer instead of Franklin, Michael or Trevor, if it makes sense

### `release_showcase`

**Definition:** Users are sharing their own mods or tools with the community, sharing images, videos, or links to download the mod.

**Example 1:**

> Newly released alternative to FivePD with a focus on realism, for FiveM server owners: https://forum.cfx.re/t/police-simulator-v-policing-gamemode/5230989/5

**Example 2:**

> Just wanted to share with you guys that I just released a giveaway of both Basic and VIP licenses in a video showcase by Angelito.

Check it out if you wanna join the giveaway or if you want to watch a full Disturbed showcase
🔥 Watch video: https://youtu.be/x4uBmYGt2_I

Useful information to those who're still looking for Luna alternatives with a limited budget.

### The hardest boundary

**Which two labels:** troubleshooting vs. recommendation_request

**The decision rule I used every time:**

Ask what the poster wants as the _answer_. If the answer they want is a fix for something that is currently broken it is `troubleshooting`. If the answer they want is the name of a mod, menu, or script, it is `recommendation_request`. When a post asks for both, the question in the title or the final sentence decides.

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:** r/gta5modding, a public subreddit, 2020 to October 2026. I first tried r/GTA5mods, but every route I tried returned only the same 11 posts, so I switched. I collected posts through Reddit's public RSS feeds: 8 pages of `/new` (800 posts). I dropped removed and deleted posts and posts with almost no text, then chose 200 by reading them.

**How I labelled them:** Claude pre-labelled 180 posts against my three definitions in `label_definitions.txt`. I double checked them, and labelled the remaining 20 rows in the note column.

**Counts per label:**

| Label                    | Count | Share |
| ------------------------ | ----- | ----- |
| `troubleshooting`        | 84    | 42%   |
| `recommendation_request` | 84    | 42%   |
| `release_showcase`       | 32    | 16%   |
| **Total**                | 200   | 100%  |

**Three hard cases**

**1.**

> _The post:_ "How to get OpenIV mods to work with NV Enhanced/Onigiri?" The poster has installed scripts and Menyoo, but nothing that goes through OpenIV works, and asks for "a comprehensive and working guide".
>
> _Could have been:_ `troubleshooting` or `recommendation_request`.
>
> _I chose `troubleshooting`, because:_ mods are installed and not working, which is something broken. It asks for a guide, so by my rule it is a fix request.

**2.**

> _The post:_ "Running GTA 5 with DirectX 12". It shares a link to a wrapper and says it should not be bannable and works online.
>
> _Could have been:_ `release_showcase` or `recommendation_request`.
>
> _I chose `release_showcase`, because:_ the poster is sharing a pre-existing tool with the community and asks nothing.

**3.**

> _The post:_ "Do I need to reinstall all my mods and scripts from scratch?" After a game update, the game crashes on the loading screen with no error message, and the poster asks whether to reinstall mods or the whole game.
>
> _Could have been:_ `troubleshooting` or `recommendation_request` (it asks for advice).
>
> _I chose `troubleshooting`, because:_ something is currently broken, and the advice asked for is a fix.

---

## The Training Run

**Base model:** `distilbert-base-uncased`, fine-tuned for 3-way classification (`troubleshooting`, `recommendation_request`, `release_showcase`).

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, 128 tokens per post, seed 42. Trained on Apple Silicon GPU (`mps`), torch 2.14.1, Python 3.12.12.

**Anything I changed from the defaults, and why:** Every setting is the notebook's default.

**Split sizes:** 70/15/15

---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- _What I asked for:_ A way to pull real posts from r/GTA5mods after a previous attempt failed with 403 and 429 errors.
- _What came back:_ Claude tried the public JSON and RSS feeds, an archive mirror, and the official listing API through a Devvit app, and showed that every route returned the same 11 posts.
- _What I changed:_ I told it to try r/gta5modding, which returned hundreds of posts.

**Moment 2**

- _What I asked for:_ Collect and store 200 posts, then label 180 of them, leaving 20 `cold` rows.
- _What came back:_ A `labels.csv` of 200 rows.
- _What I changed:_ I labeled the 20 cold rows based on my decision rules. <!-- Update this line after you review the labels, e.g. how many you corrected. -->

**Pre-labelling disclosure:** Claude pre-labelled 180 rows. Rows are marked `ai_prelabeled` or `cold` in the note column. <!-- Edit this once you have reviewed the labels: say how many you read and how many you changed. -->

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure                       | Baseline | Trained | Difference |
| ----------------------------- | -------- | ------- | ---------- |
| Overall accuracy              | 0.833    | 0.733   | -0.100     |
| Macro F1                      | 0.863    | 0.540   | -0.323     |
| F1 — `recommendation_request` | 0.762    | 0.870   | +0.108     |
| F1 — `release_showcase`       | 1.000    | 0.000   | -1.000     |
| F1 — `troubleshooting`        | 0.828    | 0.750   | -0.078     |

**What I predicted before I looked:**

<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

I predict the baseline model will beat the trained model on release_showcase because the trained model misclassified many of the release showcase posts as troubleshooting due to the similarity between the post content and a lack of clear examples found within the subreddit.

**What the gap actually means:**

<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->

The baseline outperformed the trained model overall. It performed better on 2 of the 3 metrics, mostly because of the misclassification of release_showcase posts. The finetuning did improve performance on recommendation_request posts due to being able to recognize request patterns which were more plentiful within the subreddit's dataset.

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion                        | Target                  | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| -------------------------------- | ----------------------- | ------- | ------ | --------- | ------- |
| 1. Overall accuracy              | ≥ 0.78 across all seeds | 0.733   | 0.567  | 0.700     | MISSED  |
| 2. F1 — `troubleshooting`        | ≥ 0.80 across all seeds | 0.750   | 0.643  | 0.815     | MISSED  |
| 3. F1 — `recommendation_request` | ≥ 0.72 across all seeds | 0.870   | 0.593  | 0.714     | MISSED  |
| 4. Dataset class balance         | No class > 65%          | 42.0%   | 42.0%  | 42.0%     | MET     |
| 5. High-confidence accuracy      | ≥ 0.88 when conf ≥ 0.85 | 0.800   | 1.000  | 1.000     | MISSED  |

Accuracy swung 0.167 across seeds, dropping to 0.567 on seed 7. It is clear that the dataset is too small and lopsided (lack of release_showcase examples) to properly train the model.

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted           | troubleshooting | recommendation_request | release_showcase |
| -------------------------- | --------------- | ---------------------- | ---------------- |
| **troubleshooting**        | 12              | 0                      | 0                |
| **recommendation_request** | 3               | 10                     | 0                |
| **release_showcase**       | 5               | 0                      | 0                |

Biggest confusion: 5 real `release_showcase` posts called `troubleshooting`.
The other direction: 0 real `troubleshooting` posts called `release_showcase`.

That's lopsided — the model leans toward `troubleshooting` on this pair.
A direction like that usually points at your labelling rather than the
model. Your agreement report is the thing that can tell you which.

**My biggest off-diagonal number, and what it means:**

<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->

---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| #   | Criterion                     | Target                  | Verdict | How I decided                                                                                                                                           |
| --- | ----------------------------- | ----------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Overall accuracy              | ≥ 0.78 across all seeds | MISSED  | 0.733, 0.567, 0.700. All three are under 0.78, so it missed on every seed, not just the bad one.                                                        |
| 2   | F1 — `troubleshooting`        | ≥ 0.80 across all seeds | MISSED  | 0.750, 0.643, 0.815. Only seed 2024 reached 0.80, and the target has to hold on all three.                                                              |
| 3   | F1 — `recommendation_request` | ≥ 0.72 across all seeds | MISSED  | 0.870, 0.593, 0.714. Seed 42 cleared it easily, but seed 7 missed by a wide margin and seed 2024 missed by 0.006. A miss by 0.006 is still a miss.      |
| 4   | Dataset class balance         | No class > 65%          | MET     | The largest classes are `troubleshooting` and `recommendation_request` at 42% each. This is a property of the dataset, so it is the same on every seed. |
| 5   | High-confidence accuracy      | ≥ 0.88 when conf ≥ 0.85 | MISSED  | 0.800, 1.000, 1.000. Seed 42 is below 0.88. The 1.000 results on seeds 7 and 2024 do not rescue it, because the target has to hold on every seed.       |

**Diagnoses**

**Criteria 1 and 2 (accuracy, `troubleshooting` F1):** `release_showcase` has only about 22 training posts and scored F1 0.000 on every seed, with its misses scattered across both other labels. That is too few examples and limits accuracy.

**Criterion 3 (`recommendation_request` F1):** On seed 7 the matrix shows 4 `troubleshooting` posts called `recommendation_request` and 4 the other way, so the model never learned this boundary. It is a hard pair, made worse by a small test set.

**Criterion 5 (high-confidence accuracy):** Mean confidence is about 0.5 whether the model is right or wrong, so it has learned little it is sure of.

---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** **28 / 30 = 93.3**%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**

> _The post:_ "I tracked sleep against session quality for eleven weeks. Under seven hours the next day's intervals were 6-8 seconds per mile slower, every time bar one. Small sample, one runner, but it's consistent enough that I've stopped scheduling hard days after late shifts."
>
> _Staff said / I said:_ `analysis` / `reaction`
>
> _My call, and why:_ Staff is right. Rule 3 says recency and personal experience do not outrank a load-bearing fact, and here the data is the reason for the conclusion.
>
> _Which pile:_ (a) the rule covered it and I applied it loosely.

**2.**

> _The post:_ "Everyone blames the hill at 18 miles. I split the field into people who ran the first half under 1:45 and over, and the slowdown after 18 was almost identical for both groups. If the hill were the problem the fast starters would fall apart harder."
>
> _Staff said / I said:_ `analysis` / `hot_take`
>
> _My call, and why:_ Staff is right. I read it as a hot take because it was presented as an opinion. However, it presents a logical argument with reasoning that can be evaluated, which is a characteristic of an analysis.
>
> _Which pile:_ (a) the rule covered it and I applied it loosely.

**What the pattern in my disagreements tells me:**

Both misses were analysis posts that I under-credited, for opposite reasons. One because it was personal and one because it had no hard numbers. Neither came from a gap in the rules, so I did not argue a win on any disagreement.

---

## The Improvement

**What I changed:** I weighted the training loss by the inverse of each label's share of the training split, so a missed `release_showcase` post costs about 2.6 times as much as a missed post of the other two labels. Nothing else changed: same 200 labels, same splits, same seeds, same settings.

**Which diagnosis pointed at it:** Criteria 1 and 2. `release_showcase` had F1 0.000 on all three seeds because it has only about 22 training posts and the model never predicted it.

### Run Log — After

| Criterion                        | Target                  | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| -------------------------------- | ----------------------- | ------- | ------ | --------- | ------- |
| 1. Overall accuracy              | ≥ 0.78 across all seeds | 0.733   | 0.700  | 0.733     | MISSED  |
| 2. F1 — `troubleshooting`        | ≥ 0.80 across all seeds | 0.750   | 0.714  | 0.800     | MISSED  |
| 3. F1 — `recommendation_request` | ≥ 0.72 across all seeds | 0.870   | 0.720  | 0.696     | MISSED  |
| 4. Dataset class balance         | No class > 65%          | 42.0%   | 42.0%  | 42.0%     | MET     |
| 5. High-confidence accuracy      | ≥ 0.88 when conf ≥ 0.85 | 0.800   | 1.000  | 0.800     | MISSED  |

**Did it help, and how do I know:** Partly, but it did not change any verdict. Release_showcase F1 went from 0.000 to 0.571 on seeds 7 and 2024, so the model now predicts the label. Accuracy spread across seeds fell from 0.167 to 0.033, and mean accuracy rose from 0.667 to 0.722. It did nothing on seed 42, where all 5 release_showcase posts were still called troubleshooting.

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

**`release_showcase`:** After weighting, F1 is 0.571 on seeds 7 and 2024 and still 0.000 on seed 42, so 3 of 5 test posts are still missed on the better seeds. The label is learnable, since the baseline scored 1.000, but with only 22 training posts the model needs more examples than I can add right now.

**Criteria 1 and 2:** These stay missed until release_showcase improves, since its misses cap accuracy and flood troubleshooting with false positives.

**Criterion 3:** I would re-read the posts near the troubleshooting boundary and apply my decision rule once.

**Criterion 5:** I would retest it on a larger test split, because only a few predictions reach 0.85 confidence.

**The gap between what I meant my labels to capture and what the model
learned:**

I meant my labels to separate three kinds of post: fixes, mod suggestions, and mod releases. The model learned only the first two since it has too few examples to learn what a release post looks like.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

**What This Extends**

This extends TakeMeter, my fine-tuned classifier that sorts modding subreddit posts into `troubleshooting`, `recommendation_request` and `release_showcase`. Until now it only existed inside `takemeter.ipynb` where it trained, printed a score, and had no way to ask it about a new post. The improved version is saved and published to the Hugging Face Hub, with a local FastAPI endpoint that loads it and classifies posts over HTTP. Every request writes a structured JSONL log record with its latency and compute cost.

**The Shape**

Shape A — deploy and instrument. I'm adding a local HTTP service (`POST /classify`, `GET /health`) which validates its input and logs each request as a JSONL record. The log records the timestamp, input, predicted label and confidence, a latency breakdown, and memory the request used.

Out of scope:
- **Model quality.** I'm not retraining for better accuracy, adding labels, or collecting more `release_showcase` examples. The weak `release_showcase` recall documented above stays as it is.
- **A custom front end.** FastAPI's built-in `/docs` page is the only UI.
- **Hosted deployment.** I'm not putting the service on a public URL, no auth, or rate limiting.

**Running It**

Path B — local with logs. `python serve.py` starts the service on `http://127.0.0.1:8000`; [RUNNING.md](RUNNING.md) has the full setup, the environment, and the model (269 MB, downloaded from the public Hub repo `v1assets/takemeter-distilbert` on first start). I tested it by cloning the repo into an empty folder with an empty Hugging Face cache and following RUNNING.md: the first start downloaded the model and loaded in 9.3 s, and `client.py` got 37 of 37 requests logged and 0.7667 accuracy, the same as my working copy. It isn't hosted because the process holds about 650 MB once serving, more than the 512 MB free tier.

**Instrumentation**

`serve.py` appends one JSON line to `logs/requests.jsonl` for every `/classify` request — answered, rejected or crashed — and one at startup. A middleware wraps the endpoint, so even a body that isn't valid JSON, which FastAPI rejects before my code runs, still leaves a record.

| Field | What it holds |
|---|---|
| `ts`, `event`, `model` | UTC timestamp, `startup` or `request`, which model served it |
| `request_id` | 8 hex chars, also returned to the caller as `X-Request-ID` |
| `status`, `error`, `exception` | HTTP status sent; the error code (`empty_text`, `text_too_long`, `invalid_request`, `invalid_json`, `inference_error`); the Python exception on a 500 |
| `input_preview`, `input_chars` | First 120 characters of the post (or of the raw body if it wasn't JSON), and its length |
| `n_tokens`, `truncated` | Tokens the model read (max 128), and whether the post was cut off |
| `label`, `confidence`, `scores` | The prediction and all three probabilities; null unless status is 200 |
| `tokenize_ms`, `inference_ms`, `total_ms` | Latency by stage, and wall time from request in to response out |
| `cpu_ms` | Process CPU time (user + system, all threads) during the request — the compute cost |
| `rss_mb`, `peak_rss_mb` | Process memory after the request, and the peak so far |
| startup only: `load_seconds`, `torch_threads`, versions | How long the model took to load, and what it ran on |

These are from one real session (`python serve.py`, then `python client.py --label cost-01` through `cost-10`), copied from `logs/requests.jsonl` unedited: the startup record, the first request after startup, ten answered posts from run `cost-02`, and all seven failed requests from the same run.

```jsonl
{"ts": "2026-11-19T00:15:01.266+00:00", "event": "startup", "model": "v1assets/takemeter-distilbert", "load_seconds": 2.52, "rss_mb": 453.3, "torch_threads": 6, "torch_version": "2.15.0+cpu", "python_version": "3.12.1", "device": "cpu"}
{"ts": "2026-11-19T00:15:03.898+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "55ab54c0", "status": 200, "error": null, "exception": null, "input_preview": "any good menus??\r\n\r\nHey everyone. I wanted to get a good menu i can play in public lobbies without any worries. I dont m", "input_chars": 247, "n_tokens": 64, "truncated": false, "label": "recommendation_request", "confidence": 0.3983, "scores": {"troubleshooting": 0.355, "recommendation_request": 0.3983, "release_showcase": 0.2467}, "tokenize_ms": 27.5, "inference_ms": 1175.98, "total_ms": 1267.22, "cpu_ms": 4531.2, "rss_mb": 638.1, "peak_rss_mb": 639.1}
{"ts": "2026-11-19T00:15:08.197+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "01168fd0", "status": 200, "error": null, "exception": null, "input_preview": "any good menus??\r\n\r\nHey everyone. I wanted to get a good menu i can play in public lobbies without any worries. I dont m", "input_chars": 247, "n_tokens": 64, "truncated": false, "label": "recommendation_request", "confidence": 0.3983, "scores": {"troubleshooting": 0.355, "recommendation_request": 0.3983, "release_showcase": 0.2467}, "tokenize_ms": 0.3, "inference_ms": 34.53, "total_ms": 36.0, "cpu_ms": 218.8, "rss_mb": 665.2, "peak_rss_mb": 665.2}
{"ts": "2026-11-19T00:15:08.245+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "d4458bd1", "status": 200, "error": null, "exception": null, "input_preview": "LSPDFR mods/ FivePD Discord Server\r\n\r\nhttps://discord.gg/7U2TQSjPaV (If this isn't allowed delete it) Here i release stu", "input_chars": 332, "n_tokens": 106, "truncated": false, "label": "release_showcase", "confidence": 0.3472, "scores": {"troubleshooting": 0.3104, "recommendation_request": 0.3425, "release_showcase": 0.3472}, "tokenize_ms": 0.51, "inference_ms": 43.34, "total_ms": 45.05, "cpu_ms": 203.1, "rss_mb": 665.2, "peak_rss_mb": 665.2}
{"ts": "2026-11-19T00:15:08.294+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "f4884a44", "status": 200, "error": null, "exception": null, "input_preview": "2024 What mod menu is better?\r\n\r\nHello people, I had questions about what mod menu is better because the Midnight mod me", "input_chars": 518, "n_tokens": 107, "truncated": false, "label": "troubleshooting", "confidence": 0.3846, "scores": {"troubleshooting": 0.3846, "recommendation_request": 0.3584, "release_showcase": 0.2569}, "tokenize_ms": 0.78, "inference_ms": 45.71, "total_ms": 47.63, "cpu_ms": 265.6, "rss_mb": 665.2, "peak_rss_mb": 665.2}
{"ts": "2026-11-19T00:15:08.346+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "7d2bb3ef", "status": 200, "error": null, "exception": null, "input_preview": "Added cars not showing up\r\n\r\nPretty sure I’ve done it correctly…. Added it to mods folder, copped the line to dlc list, ", "input_chars": 652, "n_tokens": 128, "truncated": true, "label": "troubleshooting", "confidence": 0.4398, "scores": {"troubleshooting": 0.4398, "recommendation_request": 0.3253, "release_showcase": 0.2349}, "tokenize_ms": 0.77, "inference_ms": 47.17, "total_ms": 48.98, "cpu_ms": 281.2, "rss_mb": 665.3, "peak_rss_mb": 665.3}
{"ts": "2026-11-19T00:15:08.413+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "c8baf382", "status": 200, "error": null, "exception": null, "input_preview": "Any idea how to play with mods after Kortz Heist update? (Enhanced)\r\n\r\nEver since the last update my game will crash if ", "input_chars": 330, "n_tokens": 85, "truncated": false, "label": "troubleshooting", "confidence": 0.4277, "scores": {"troubleshooting": 0.4277, "recommendation_request": 0.3295, "release_showcase": 0.2428}, "tokenize_ms": 0.47, "inference_ms": 39.79, "total_ms": 41.41, "cpu_ms": 187.5, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:08.445+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "e779dd2a", "status": 200, "error": null, "exception": null, "input_preview": "Any script that has similar features to jinx?\r\n\r\nI heard jinx is getting deleted and thats sad because it makes cherax s", "input_chars": 203, "n_tokens": 45, "truncated": false, "label": "troubleshooting", "confidence": 0.3707, "scores": {"troubleshooting": 0.3707, "recommendation_request": 0.3615, "release_showcase": 0.2678}, "tokenize_ms": 0.27, "inference_ms": 27.88, "total_ms": 29.23, "cpu_ms": 187.5, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:08.501+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "7ef11581", "status": 200, "error": null, "exception": null, "input_preview": "heist editor 3.6 set up\r\n\r\nso i installed this heist editor off of unreal cheats however i cannot unzip the file due to ", "input_chars": 245, "n_tokens": 71, "truncated": false, "label": "troubleshooting", "confidence": 0.4181, "scores": {"troubleshooting": 0.4181, "recommendation_request": 0.3278, "release_showcase": 0.2541}, "tokenize_ms": 0.39, "inference_ms": 33.7, "total_ms": 35.32, "cpu_ms": 187.5, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:08.541+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "b819a2c3", "status": 200, "error": null, "exception": null, "input_preview": "Can't launch game bcs of ENB\r\n\r\nHello guys,so when i try to launch GTA V my game is crashing with error and in my GTA V ", "input_chars": 315, "n_tokens": 85, "truncated": false, "label": "troubleshooting", "confidence": 0.4476, "scores": {"troubleshooting": 0.4476, "recommendation_request": 0.3275, "release_showcase": 0.2249}, "tokenize_ms": 0.32, "inference_ms": 36.69, "total_ms": 38.08, "cpu_ms": 187.5, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:08.571+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "b473a587", "status": 200, "error": null, "exception": null, "input_preview": "I need to mod my gta 5 enhanced but the script hook is out dated\r\n\r\nI launch the game with script hook = crashes \r\n\r\n I ", "input_chars": 179, "n_tokens": 40, "truncated": false, "label": "troubleshooting", "confidence": 0.4388, "scores": {"troubleshooting": 0.4388, "recommendation_request": 0.3225, "release_showcase": 0.2388}, "tokenize_ms": 0.33, "inference_ms": 26.74, "total_ms": 28.24, "cpu_ms": 93.8, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:08.620+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "3b30e2e3", "status": 200, "error": null, "exception": null, "input_preview": "OpenIV.asi error\r\n\r\ni installed gta today after a while and i installed all base mods like two scripthook, heap adj ecc.", "input_chars": 417, "n_tokens": 114, "truncated": false, "label": "troubleshooting", "confidence": 0.4147, "scores": {"troubleshooting": 0.4147, "recommendation_request": 0.3147, "release_showcase": 0.2707}, "tokenize_ms": 0.53, "inference_ms": 44.93, "total_ms": 46.55, "cpu_ms": 250.0, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:15:09.569+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "b81723c4", "status": 400, "error": "empty_text", "exception": null, "input_preview": "", "input_chars": 0, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.79, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.571+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "af132ab5", "status": 400, "error": "empty_text", "exception": null, "input_preview": "", "input_chars": 0, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.74, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.595+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "0213ea4b", "status": 400, "error": "invalid_request", "exception": null, "input_preview": "{}", "input_chars": 2, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.72, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.597+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "92155be4", "status": 400, "error": "invalid_request", "exception": null, "input_preview": "{\"text\": 5}", "input_chars": 11, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.85, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.599+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "18e900bc", "status": 400, "error": "invalid_json", "exception": null, "input_preview": "{text", "input_chars": 5, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.56, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.602+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "713adb2e", "status": 400, "error": "invalid_request", "exception": null, "input_preview": "\"just a string\"", "input_chars": 15, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.68, "cpu_ms": 0.0, "rss_mb": 666.3, "peak_rss_mb": 666.3}
{"ts": "2026-11-19T00:15:09.604+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "ecb9f9ee", "status": 400, "error": "text_too_long", "exception": null, "input_preview": "word word word word word word word word word word word word word word word word word word word word word word word word ", "input_chars": 12499, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.76, "cpu_ms": 46.9, "rss_mb": 666.3, "peak_rss_mb": 666.3}
```

The seven failures are deliberate: `client.py` sends an empty string, whitespace only, `{}`, `{"text": 5}`, a body that isn't JSON, a bare JSON string and a 12,500-character post on every run. All seven got a 400 and a log record with their error code on all ten runs (70 of 70). I haven't produced a 500 yet — no request in this session crashed inference.

**What It Costs**

**0.25 CPU-seconds per classification** (mean `cpu_ms` 251.9 over 300 requests), measured, not estimated. Wall time is much lower, 40 ms at p50, because PyTorch spreads one inference over 6 threads, so the CPU time is the honest cost. There's no API spend: the model runs locally.

How I measured it: I started one fresh `python serve.py` and ran `python client.py --label cost-NN` ten times, one request at a time. That's 30 test posts and 7 bad inputs per run, 370 requests. `cpu_ms` is the process's CPU time read with `psutil` before and after each request, written by the server into its own log, and the client only averages records whose `request_id` it got back. The per-run summaries are committed in `runs/cost-01.json` … `runs/cost-10.json`.

| | Requests | Mean `cpu_ms` | `total_ms` p50 / p95 / max |
|---|---|---|---|
| All answered posts | 300 | 251.9 | 39.7 / 56.1 / 1267.2 |
| Excluding the first request after startup | 299 | 237.6 | 39.7 / 56.0 / 125.1 |
| First request after startup (cold) | 1 | 4531.2 | 1267.2 |
| Rejected (400) | 70 | 7.1 | 0.8 mean |
| Model load at startup | — | — | 2.52 s (from cache; 9.3 s with the download) |

Per-run means of `cpu_ms`: 396.3, 227.6, 247.4, 226.0, 233.3, 230.7, 245.3, 231.2, 246.9, 234.4. Run 1 is high only because it holds the cold first request. Windows reports CPU time in steps of about 15.6 ms, so a single request's `cpu_ms` is coarse; the mean over 300 isn't.

Memory is the other cost: 453 MB after loading, 667 MB peak while serving, held for as long as the service is up whether anyone is using it or not.

For a hundred people a day, one classification each:
100 × 0.252 CPU-s = **25.2 CPU-seconds a day**, plus one cold start per restart (2.5 s load + 4.5 CPU-s first request). That's under half a minute of one CPU core per day, and $0 in API fees. The real constraint at that volume isn't compute but memory: the service needs about 670 MB resident all day, which is why it doesn't fit a 512 MB free host.

**Run Log and Verdicts**

Each trial starts its own `serve.py` with its own log, sends one warm-up post, then sends the 30 test posts and 14 bad inputs ten times over, one at a time and scores the criteria from that trial's log. How each criterion is measured is in the docstring of `run_trials.py`. Criterion 1 uses the client's round-trip time (how long the caller waits), and criterion 2 uses 14 bad inputs (the 7 `client.py` always sent plus 7 found by probing the service).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Fast responses once the server is running | ≥ 90% of valid requests under 100 ms | 300/300 | 300/300 | 300/300 | MET |
| 2. Bad input gets a 400, never a 500 | 140/140 get a 400, zero 500 | 130/140 | 130/140 | 130/140 | MISSED |
| 3. Every request is logged | 100% | 441/441 | 441/441 | 441/441 | MET |
| 4. Memory stays under 750 MB | ≤ 750 MB peak | 667.1 MB | 666.5 MB | 666.8 MB | MET |
| 5. Most posts fit in the 128-token limit | ≤ 40% of 30 posts truncated | 10/30 | 10/30 | 10/30 | MET |

Raw files: `runs/before/trial-N.jsonl` (the server's log, written by `log_classify` in `serve.py`), `runs/before/trial-N.json` (every request the client sent and what came back, from `run_trial` in `run_trials.py`), `runs/before/summary.json`. The output below is from trial 1.

*Criterion 1.* Client round-trip p50 48.0 ms, p95 70.8 ms, max 81.8 ms; server `total_ms` p50 37.4 ms, p95 53.1 ms. Runs 2 and 3 maxed at 96.0 and 94.8 ms. The three slowest requests in trial 1, from `run_trial` in `run_trials.py`:

```json
{"request_id": "d288f3c8", "name": "post_26", "client_ms": 81.81, "server_ms": 79.81, "n_tokens": 128}
{"request_id": "7e571539", "name": "post_28", "client_ms": 81.43, "server_ms": 52.55, "n_tokens": 128}
{"request_id": "6f00b9ad", "name": "post_28", "client_ms": 77.22, "server_ms": 51.36, "n_tokens": 128}
```

*Criterion 2.* 13 of the 14 bad inputs got a 400 on every pass, `nul_only_text` (`{"text": "\u0000\u0000"}`) got a 200 all ten times, and no input got a 500:

```jsonl
{"ts": "2026-11-19T00:39:10.019+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "427c7299", "status": 200, "error": null, "exception": null, "input_preview": "\u0000\u0000", "input_chars": 2, "n_tokens": 2, "truncated": false, "label": "release_showcase", "confidence": 0.4184, "scores": {"troubleshooting": 0.2568, "recommendation_request": 0.3248, "release_showcase": 0.4184}, "tokenize_ms": 0.15, "inference_ms": 8.13, "total_ms": 9.39, "cpu_ms": 78.1, "rss_mb": 665.4, "peak_rss_mb": 665.4}
{"ts": "2026-11-19T00:39:09.951+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "6adde7d7", "status": 400, "error": "empty_text", "exception": null, "input_preview": "", "input_chars": 0, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 1.04, "cpu_ms": 0.0, "rss_mb": 665.1, "peak_rss_mb": 665.1}
{"ts": "2026-11-19T00:39:10.008+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "d48f09c8", "status": 400, "error": null, "exception": null, "input_preview": "{\"text\": \"�� broken bytes\"}", "input_chars": 27, "n_tokens": null, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": null, "inference_ms": null, "total_ms": 0.41, "cpu_ms": 0.0, "rss_mb": 665.4, "peak_rss_mb": 665.4}
```

*Criterion 3.* From `run_trial` in `run_trials.py`, trial 1: `{"logged": 441, "of": 441, "missing": [], "met": true}`. The 441 includes the warm-up and all 140 rejected requests.

*Criterion 4.* The startup record and the request with the highest `peak_rss_mb` in trial 1:

```jsonl
{"ts": "2026-11-19T00:39:08.132+00:00", "event": "startup", "model": "v1assets/takemeter-distilbert", "load_seconds": 0.84, "rss_mb": 452.5, "torch_threads": 6, "torch_version": "2.15.0+cpu", "python_version": "3.12.1", "device": "cpu"}
{"ts": "2026-11-19T00:39:13.794+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "5ca2a512", "status": 200, "error": null, "exception": null, "input_preview": "Texture glitching (black/purple squares) leading to ERR_GFX_STATE after recent GTA V Enhanced Update\r\n\r\nHi everyone, \r\n\r", "input_chars": 1559, "n_tokens": 128, "truncated": true, "label": "troubleshooting", "confidence": 0.372, "scores": {"troubleshooting": 0.372, "recommendation_request": 0.3272, "release_showcase": 0.3008}, "tokenize_ms": 1.05, "inference_ms": 48.71, "total_ms": 50.93, "cpu_ms": 375.0, "rss_mb": 667.1, "peak_rss_mb": 667.1}
```

*Criterion 5.* The first truncated post in trial 1 cut at 128 tokens:

```jsonl
{"ts": "2026-11-19T00:39:08.758+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "139e6019", "status": 200, "error": null, "exception": null, "input_preview": "Added cars not showing up\r\n\r\nPretty sure I’ve done it correctly…. Added it to mods folder, copped the line to dlc list, ", "input_chars": 652, "n_tokens": 128, "truncated": true, "label": "troubleshooting", "confidence": 0.4398, "scores": {"troubleshooting": 0.4398, "recommendation_request": 0.3253, "release_showcase": 0.2349}, "tokenize_ms": 0.6, "inference_ms": 40.27, "total_ms": 41.88, "cpu_ms": 187.5, "rss_mb": 659.2, "peak_rss_mb": 659.2}
```

All three trials of criteria 2 and 5 were identical. Each trial was a separate `serve.py` process with its own log and its own request ids. They're identical because both are decided by fixed inputs. Criteria 1 and 4, which depend on the machine, did vary.

**The Improvement**

What I changed: the empty-input check in `classify()` in `serve.py`. Before, a post counted as empty only if `text.strip()` was empty. Now, after tokenizing, the service also counts the tokens the model would actually read — the tokenized length minus the `[CLS]` and `[SEP]` it adds — and if that's zero it returns a 400 with the new error code `no_content`, before inference runs. That's the only behaviour change; `RUNNING.md` and the log-field notes in `serve.py` now list `no_content`.

Why this change: it's aimed at the one miss in the before run. Criterion 2 failed on `nul_only_text` alone — 10 of 10 passes in all three trials returned a 200. `strip()` only removes whitespace, so `"\u0000\u0000"` passed the check, and the tokenizer then dropped both characters, so the model classified nothing but its own `[CLS]` and `[SEP]` (`n_tokens: 2`) and answered `release_showcase` at 0.4184. Checking emptiness by what the model reads instead of by what `strip()` sees closes that gap for any character the tokenizer discards, not just null bytes. A one-letter post (`"a"`) still classifies.

Run Log — After. `python run_trials.py --label after`, the same three-trial procedure and the same 441 requests per trial as before.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Fast responses once the server is running | ≥ 90% of valid requests under 100 ms | 300/300 | 300/300 | 299/300 | MET |
| 2. Bad input gets a 400, never a 500 | 140/140 get a 400, zero 500 | 140/140 | 140/140 | 140/140 | MET |
| 3. Every request is logged | 100% | 441/441 | 441/441 | 441/441 | MET |
| 4. Memory stays under 750 MB | ≤ 750 MB peak | 667.2 MB | 666.3 MB | 666.5 MB | MET |
| 5. Most posts fit in the 128-token limit | ≤ 40% of 30 posts truncated | 10/30 | 10/30 | 10/30 | MET |

Before and after, side by side:

| Criterion | Before (runs 1 / 2 / 3) | Verdict | After (runs 1 / 2 / 3) | Verdict |
|---|---|---|---|---|
| 1 | 300 / 300 / 300 of 300 | MET | 300 / 300 / 299 of 300 | MET |
| 2 | 130 / 130 / 130 of 140 | MISSED | 140 / 140 / 140 of 140 | MET |
| 3 | 441 / 441 / 441 of 441 | MET | 441 / 441 / 441 of 441 | MET |
| 4 | 667.1 / 666.5 / 666.8 MB | MET | 667.2 / 666.3 / 666.5 MB | MET |
| 5 | 10 / 10 / 10 of 30 | MET | 10 / 10 / 10 of 30 | MET |

The same `nul_only_text` request after the fix, from `log_classify` in `serve.py` (`runs/after/trial-1.jsonl`) — a 400 `no_content`, with no `inference_ms` because the model never ran:

```jsonl
{"ts": "2026-11-19T00:50:41.841+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "ce1975fa", "status": 400, "error": "no_content", "exception": null, "input_preview": "\u0000\u0000", "input_chars": 2, "n_tokens": 2, "truncated": null, "label": null, "confidence": null, "scores": null, "tokenize_ms": 0.16, "inference_ms": null, "total_ms": 0.97, "cpu_ms": 15.6, "rss_mb": 666.2, "peak_rss_mb": 666.2}
```

Did it help: yes, for what it was aimed at. Criterion 2 went from MISSED (130/140 in every trial) to MET (140/140 in every trial), and nothing else changed verdict. Accuracy on the 30 test posts is still 0.7667 in every trial, so the check didn't reject any real post.

One thing moved the wrong way, and it isn't the fix. Run 3 of criterion 1 had its first request over 100 ms (`runs/after/trial-3.jsonl`, request `e63ad1bc`): a 128-token post whose forward pass took 119.8 ms, when the same post took about 50 ms on the other nine passes of that trial. The new check runs after tokenizing and before inference and costs under a millisecond (`tokenize_ms` 1.13 here), so it can't account for 70 ms. Criterion 1 is still met at 299/300, but the before run already peaked at 96 ms, so the 100 ms margin on full-length posts is thin:

```jsonl
{"ts": "2026-11-19T00:51:44.846+00:00", "event": "request", "model": "v1assets/takemeter-distilbert", "request_id": "e63ad1bc", "status": 200, "error": null, "exception": null, "input_preview": "Need help with crashing\r\n\r\nThis might be a long shot but I've tried literally everything I can think of to fix this for ", "input_chars": 799, "n_tokens": 128, "truncated": true, "label": "troubleshooting", "confidence": 0.4166, "scores": {"troubleshooting": 0.4166, "recommendation_request": 0.3294, "release_showcase": 0.254}, "tokenize_ms": 1.13, "inference_ms": 119.82, "total_ms": 122.3, "cpu_ms": 562.5, "rss_mb": 665.8, "peak_rss_mb": 666.5}
```

**What's Still Broken**

All five criteria were met after the fix but criterion 5 was set too loose.

Whether a post gets cut off depends only on the post and the 128-token limit.  All six trials cut the same 10 of 30 posts. The 40% target was placed above a number that was always going to be 33%.

Why I stopped: Raising the limit means retraining the model at 256 tokens, which is out of scope for this unit.

What I'd do next: Retrain at 256 tokens, then run all five criteria with `run_trials.py`. Posts being classified on only part of their text is the only gap I measured that changes the answer a user will see.

**How I Used AI**

I used Claude Code to build the service, the logging and the trial runner.

What I asked: Wrap my classifier in a FastAPI service where bad input gets a 400, and an error gets a 500 while the server keeps running.

What I got back: `serve.py` with those error handlers, with code that marked long posts as `truncated`. The code crashed on any post over 128 tokens and the request failed with a 500 `inference_error` (`ValueError: Unable to create tensor…`).

What changed: The 500 handler sent back clean JSON, and the server still answered `/health` afterwards. So I kept the handler and had the truncation code fixed to keep the rows and use only the first one. Resubmitting the same long post gave a 200 with `truncated: true`.