# rsna-claude — RSNA Knee Abnormality Detection

<!-- Read when: orienting, or before running anything. Changes: when structure or setup changes. -->

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vak-sah/rsna-claude/blob/main/command_center.ipynb)

A run at the [RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
Kaggle competition — 12 binary findings per knee MRI study, scored by macro ROC-AUC, aiming at
both the main and the efficiency prize. Built notebook-first: features get worked out in the
command center, then extracted to `src/` once they settle.

The interesting constraint is that only **58 of 4,407 training studies carry labels** — the other
4,349 come with a multilingual radiology report and nothing else. So this is a weak-supervision
problem wearing a computer-vision costume, and the plan for exploiting that is `STRATEGY.md`.

## Running it

`command_center.ipynb` is the workspace, and it runs on **two hosts**:

- **Kaggle** — where the pixels are. The competition data is ~570 GB, so every step that touches
  DICOM runs as a Kaggle kernel and hands its output to the next one. Upload the notebook to a
  Kaggle notebook, attach the competition dataset, pick the **T4** accelerator (never the P100 —
  `PLAYBOOK.md`), and run.
- **Colab** — where iteration is comfortable. Click the badge above, and the setup cell mounts
  Drive and clones the repo. Use it for anything that fits in a cached subset.

The notebook detects which host it is on and resolves its paths accordingly. Everything else is
the same in both places: the **config cell** runs first and holds every knob, each with the
alternatives weighed and the reason the current value won. It is the only thing you edit — setup
below it just acts on those values.

To keep notebook edits from Colab, use its **Save in GitHub** button; that click is the commit,
no PR step. Run output is stripped automatically on push, so it never reaches git. First save
asks you to **Authorize googlecolab** — OAuth, nothing to store. If the notebook looks stale
after the agent changed it, reopen the link or append `?flush_cache=true`. Tests are `pytest -q`
from the repo root — no Drive, no network, no GPU, so the same command works in CI, a terminal,
or a cell.

Working with an agent here: `AGENTS.md` is both the contract and the entry point — it names what
to read, in what order, and how a session runs. Most agents pick it up unprompted. One that
doesn't needs a single sentence: *read `AGENTS.md` and follow it*.

One rule is worth repeating outside that file, because breaking it is expensive: **no competition
data — report text, pixel data, per-study rows — ever goes into an agent session.** Aggregates,
schemas, code and metrics only. `PLAYBOOK.md` § Gotchas has the reasoning.

## Layout

```
command_center.ipynb   the workspace — setup, config cell, features being built, output
src/pipeline/          the archive: settled logic, one module per feature, docstring at the top
tests/                 all tests. never in a notebook cell
pyproject.toml         pytest config only — makes src/ importable. not packaging
.github/workflows/     CI: runs the tests, and strips notebook output, on every push
.gitignore             keeps data, weights, caches, outputs and credentials out of git
LICENSE                Apache 2.0
README.md              this file: what, how to run, what's where, how it flows
STATE.md               what's done, what's in progress, what's next
STRATEGY.md            how we intend to win: the metric's consequences, and every idea, ranked
EXPERIMENTS.md         the run log — one row per run, and what it measured
PLAYBOOK.md            environment quirks, manual setup, solved problems, dead ends
AGENTS.md              how agents and the user work in this repo
CLAUDE.md              points Claude Code at AGENTS.md
```

Data, weights, outputs and credentials are **not** in this repo — on Kaggle they live in the
mounted competition dataset and in kernel outputs; on Colab they live under the Drive root set in
the notebook's config cell, which is the only place that path appears.

## Pipeline

<!-- input → each stage → output. one line per stage, naming the module that owns it. -->

Nothing real yet — `src/pipeline/stub.py` is a passthrough that proves the wiring works. The
first stage replaces it, and the order the stages will arrive in is `STATE.md` § Next.
