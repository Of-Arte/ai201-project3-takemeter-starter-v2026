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

| Measure          | Baseline | Trained | Difference |
| ---------------- | -------- | ------- | ---------- |
| Overall accuracy |          |         |            |
| Macro F1         |          |         |            |
| F1 — `label_one` |          |         |            |
| F1 — `label_two` |          |         |            |

**What I predicted before I looked:**

<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**

<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->

---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| --------- | ------ | ------- | ------ | --------- | ------- |
| 1.        |        |         |        |           |         |
| 2.        |        |         |        |           |         |
| 3.        |        |         |        |           |         |
| 4.        |        |         |        |           |         |
| 5.        |        |         |        |           |         |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |     |     |     |
| ---------------- | --- | --- | --- |
| \*\*\*\*         |     |     |     |
| \*\*\*\*         |     |     |     |
| \*\*\*\*         |     |     |     |

**My biggest off-diagonal number, and what it means:**

<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->

---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   |           |        |         |               |
| 2   |           |        |         |               |
| 3   |           |        |         |               |
| 4   |           |        |         |               |
| 5   |           |        |         |               |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->

---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** **_ / 30 = _**%

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

> _The post:_
>
> _Staff said / I said:_
>
> _My call, and why:_
>
> _Which pile:_

**2.**

> _The post:_
>
> _Staff said / I said:_
>
> _My call, and why:_
>
> _Which pile:_

**What the pattern in my disagreements tells me:**

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
| --------- | ------ | ------- | ------ | --------- | ------- |
| 1.        |        |         |        |           |         |
| 2.        |        |         |        |           |         |
| 3.        |        |         |        |           |         |
| 4.        |        |         |        |           |         |
| 5.        |        |         |        |           |         |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

**The gap between what I meant my labels to capture and what the model
learned:**

<!-- Two sentences. Your confusion matrix is the evidence. -->

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
