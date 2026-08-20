# STATE

**Read when:** first thing, every session. **Changes:** when the project moves.
Where this project is. Detail lives in `git log`; structure lives in `README.md`; reasoning
lives in `STRATEGY.md`; measurements live in `EXPERIMENTS.md`.

## 1. Goal

Win the **RSNA Knee Abnormality Detection** Kaggle competition — both the **main track** and the
**efficiency track** — by the final submission deadline of **2026-10-22**. The task is 12 binary
findings per knee MRI study, scored by **macro-averaged ROC-AUC**, submitted as a code notebook
with internet off. MVP is a submitted notebook that beats the public-baseline cluster (~0.891 as
of 2026-08-08) on trustworthy grouped cross-validation, plus a second, deliberately cheap
submission aimed at the efficiency prize. Everything is built under hard constraints — ~570 GB of
DICOM that never leaves Kaggle, ~30 Kaggle GPU-hours a week, 58 labelled studies out of 4,407,
and 63 days — so the edge has to come from **being smarter about the metric and the labels**,
not from spending more compute. `STRATEGY.md` is where that edge is argued and ranked.

References — evidence about the problem, never a specification (`AGENTS.md` §1):
- The competition itself: overview, data description, rules, and the host's discussion posts —
  the only authoritative source, and the one the agent cannot reach (`PLAYBOOK.md` § Gotchas).
- `github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection` — a competitor's public
  strategy and data-audit notes. Most of what we currently believe about the data shape.
- `github.com/JunhaoLiXD/RSNA_Knee_Abnormality_Detection` — a competitor's public 2.5D baseline
  write-up: label names, preprocessing choices, leaderboard reference points.
- What each of those gives us, what we refuse to take from them, and where we expect to diverge:
  `PLAYBOOK.md` § Reference notes.

## 2. Done
1. Onboarding — repo made specific to this competition: goal, strategy, run log, references,
   dual-host (Kaggle + Colab) notebook config. _(unchecked)_

## 3. In progress
- none

## 4. Next
1. **Recon.** Read the competition pages and rules; confirm or correct every `[T]` fact in
   `STRATEGY.md` §1, above all *whether test studies come with reports* (§8.1) and the exact
   efficiency formula (§8.2). Nothing below is safe until this lands.
2. **Metadata scan.** Header-only pass over all series on Kaggle CPU: geometry, laterality, site
   fingerprint, slot coverage, slice counts, transfer syntaxes — plus the identifier archaeology
   in `STRATEGY.md` X2. Aggregates only, never per-study rows in a session.
3. **Folds, frozen forever.** Grouped fold assignment (V1), adversarial validation train-vs-test
   (V3), and the 58-gold provenance check (X7). Every later number is comparable only to numbers
   built on these folds.
4. **Severity labeller.** Two lexicons, magnitude and categorical (L1), site random effects (X6),
   report-embedding kNN as a second source (L6). Evaluated on the 58 gold with intervals, never
   point estimates (V4).
5. **The cache.** Joint-centred 130 mm crop (I2), 336 px, six slots with a presence mask, uint8 —
   built on Kaggle, kernel to kernel. The one artifact every model trains on.
6. **First real model.** Pairwise rank loss over severity (L2), rubric-matched pooling (I4),
   flip-with-label-swap (I3). First grouped OOF, first submission.
7. **Instrument the leaderboard.** Per-label AUC probes (P1), fixed-overhead and runtime probes
   (P5, P4), and the metadata-only submission that prices the site prior (P3).
8. **Aim at the weakest columns.** Whatever P1 says they are: compartment sub-crops (I5),
   per-label resolution (I6), specialists where they earn it (X12).
9. **Efficiency submission.** Distil the ensemble to one small student (E1), strided decode (E2),
   pipelined I/O (E3), I/O-level cascade (X8). Target ≥0.90 AUC under 25 minutes.
10. **Close.** Per-label rank-weighted ensemble (F1, F3), two decorrelated final submissions
    (F5), solution write-up out of `EXPERIMENTS.md`.

## 5. Optional / later
- Registered patient-space volume and oblique anatomy-aligned reformats (`STRATEGY.md` X1) — the
  highest-ceiling idea we have, and the most expensive. Promote it the moment items 1–6 are done.
- Self-supervised pretraining on the 819k unlabelled slices, test set included (I13) — the one
  idea that wants Colab Pro A100 time rather than Kaggle T4s.
- PU-learning loss for the contaminated negative class (X3); noise-transition layer from the 58
  gold (L4); strict/lenient adjudication panel (X4).
- Rubric-as-prompt zero-shot head (X5); cross-modal distillation of the report (L10).
- Transductive test-time adaptation and pseudo-labelling inside the 9-hour submission (D5).
- Auxiliary heads for the 20–40 findings the reports mention beyond the 12 scored ones (L8).

## 6. Parked / dropped
- **External datasets** (MRNet, fastMRI+, OAI, SKM-TEA) — click-through licences, unclear whether
  they count as "freely and publicly available" under the rules, and the host has not ruled.
  Nothing in the queue depends on them. Revisit only if the host rules in favour.
- **Hosted LLM APIs for report labelling** — Rule 4.b (Data Security) plausibly forbids sending
  competition data to a third party. Open-weights models on Kaggle or Colab instead. This one is
  not a preference; see `PLAYBOOK.md` § Gotchas.
