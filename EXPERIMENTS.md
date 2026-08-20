# EXPERIMENTS — the run log

**Read when:** before proposing a run, and before believing a number. **Changes:** after every
run that produced a measurement, including the ones that failed.

One row per run. `STRATEGY.md` says what we believe and why; this file says what we measured.
When the two disagree, this file wins and `STRATEGY.md` gets edited.

By the end of the competition this log **is** the solution write-up that prize claims and the
RSNA presentation require (`STRATEGY.md` R4). Written as we go it costs a minute a run;
reconstructed in November it costs a week and is half fiction.

---

## How to add a row

| Column | What goes in it |
|---|---|
| `#` | Run number, never reused |
| `Date` | When it finished |
| `Idea` | The `STRATEGY.md` idea IDs this run tests (`L2`, `I4`, `X1` …) |
| `What changed` | **One thing.** If it is two things, it is two runs |
| `CV-g` | Macro ROC-AUC, **grouped** folds — the primary decision metric |
| `CV-r` | Macro ROC-AUC, **random** folds — the optimistic bound |
| `Gold` | Macro ROC-AUC on the 58 gold studies, **with a bootstrap interval or not at all** |
| `LB` | Public leaderboard, if submitted |
| `Runtime` | Submission wall-clock in seconds — required for anything aimed at the efficiency track |
| `GPU-h` | What the run cost to train, so the budget in `STRATEGY.md` §4 stays honest |
| `Verdict` | `keep` / `drop` / `inconclusive`, and one clause of why |

Rules that make the table worth reading:

- **One change per run.** A confounded run is 3 % of the campaign budget spent on nothing.
- **The same frozen folds, every time.** A run on regenerated folds is not comparable to anything
  and should be marked so.
- **`CV-g − CV-r` is a measurement**, not a nuisance: it reads out how much the model is leaning
  on site rather than anatomy (`STRATEGY.md` V2).
- **Never a bare point estimate on the 58 gold studies** (`STRATEGY.md` V4). Interval or nothing.
- **Failed runs get rows.** They are the cheapest information in the project and the first thing
  anyone drops.

---

## Runs

| # | Date | Idea | What changed | CV-g | CV-r | Gold | LB | Runtime | GPU-h | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | _nothing yet_ | — | — | — | — | — | — | — |

---

## External reference points

Not our runs. Public numbers from third parties, recorded so we always know what "good" means
this week and never mistake one of these for something we measured. Every line is **[T]** in
`STRATEGY.md`'s sense — one public source, unverified.

| Date | Whose | What | Score |
|---|---|---|---|
| 2026-08-08 | public LB | Leader | 0.939 |
| 2026-08-08 | public LB | 2nd / 3rd | 0.933 / 0.929 |
| 2026-08-08 | public LB | The forked-baseline cluster, 676 teams total | 0.891 |
| 2026-08-08 | public notebook | `pilkwang/rsna-knee-baseline-v1` — DINOv2-S, 130 mm crop, 6 slots, rule labeller | 0.809 → cluster at 0.891 |
| ~2026-08 | competitor repo | 3-plane 2.5D EfficientNet-B0, rule weak labels (V01) | 0.613 |
| ~2026-08 | competitor repo | + hierarchical calibrated soft labels (V03); 58-gold OOF 0.632 | 0.664 |
| 2026-08-08 | competitor probe | DICOM headers only, no pixels — random folds | 0.6515 |
| 2026-08-08 | competitor probe | DICOM headers only, no pixels — scanner-grouped folds | 0.5981 |
| 2026-08-08 | competitor probe | Series composition alone (4 CSV columns) | 0.5954 |
| 2026-08-08 | competitor result | Severity extractor vs presence extractor, on 58 gold | +0.046 [+0.008, +0.082] |

The last row is the only published evidence for `STRATEGY.md`'s central bet, it was measured on
58 studies across three iterations against the same 58, and its author says so. Treat the
direction as supported and the magnitude as an upper bound — and re-measure it ourselves.

The gap that matters is **0.891 → 0.939**. The forked cluster is the floor; the leader is the
target. Anything of ours that lands below 0.891 has not yet started.
