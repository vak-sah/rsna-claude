# PLAYBOOK

**Read when:** session start, and before re-deriving anything.
**Changes:** whenever something is learned. Append, rarely delete.

What this project learned the hard way: environment quirks, manual steps, solved problems, dead
ends. An entry earns its place by saving someone from re-deriving something.

Not paths (notebook config cell), not layout or pipeline (`README.md`), not status (`STATE.md`),
not reasoning (`STRATEGY.md`), not measurements (`EXPERIMENTS.md`).
If the user corrects the same thing twice, it belongs here.

## Manual one-time setup

- **Kaggle account, competition rules accepted.** Nothing in this project runs until the rules
  have been accepted on the competition page — the data is not mountable before that.
- **Kaggle API token**, needed only if pushing notebooks from Colab rather than uploading by
  hand. Download `kaggle.json` from Kaggle → Settings → API → Create New Token, then either:
  - Colab Secrets: add `KAGGLE_USERNAME` and `KAGGLE_KEY` (preferred — nothing on disk), or
  - place the file at `<DRIVE_ROOT>/secrets/kaggle.json` (path is derived in the notebook config
    cell; the folder is gitignored and the file never enters the repo).
- **Colab Pro** is the secondary host, for training on a cached subset. The primary host is
  Kaggle, because the competition data is ~570 GB and never leaves it.

## Reference notes

Written 2026-08-20, from a live read of what was reachable. **Kaggle and rsna.org were blocked**
(see § Gotchas), so the competition's own pages have never been read by an agent in this project
— everything attributed to them below arrived second-hand and is marked `[T]` in `STRATEGY.md`.

### The competition pages themselves — *the only authoritative reference, and unread*

- **Take:** everything. The metric, the rules, the label definitions, the data description, the
  host's discussion answers.
- **Do not take:** anything, yet — no agent has read them. `STATE.md` §4 item 1 exists solely to
  fix this, and `STRATEGY.md` §8 is the list of what to read for.
- **Diverge:** not applicable. There is no diverging from the rules.

### `github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection` — a competitor's public notes

Read once, in full, on 2026-08-20. A genuinely careful data audit, published openly.

- **Take:** the *measurements* and the *host quotes*, as leads to verify — dataset size, series
  and slot statistics, laterality coverage and the geometric side rule, the fold-grouping
  experiments (and the negative result that a scanner fingerprint containing `ImagingFrequency`
  produces 2,668 singletons), the physical-scale distribution behind a 130 mm crop, the finding
  that all training series are uncompressed, and the quoted label criteria and host Q&A. These
  saved us days of blind exploration and give us hypotheses with numbers attached.
- **Do not take:** their code, their pipeline, or their conclusions as settled. Their labelling
  approach — extract severity, calibrate to a soft target, train with weighted BCE — is one
  reasonable answer, and their own log shows how badly it can go wrong (a base-rate collapse, a
  reversed-prior bug). We are not forking it and we are not debugging it.
- **Diverge:** three places, deliberately. (1) They optimise a *classification* surrogate; we
  optimise a *ranking* one, because the metric is rank-only (`STRATEGY.md` L2). (2) They treat
  site information as leakage to be grouped away; we think it is a legitimate transferable
  feature and intend to price it on the leaderboard rather than argue about it (P3, D1).
  (3) They keep six independent 2-D stacks; our highest-ceiling idea is to register them into one
  patient-space volume (X1). Each of those is a choice they made under their own constraints, and
  each is ours to re-make.

### `github.com/JunhaoLiXD/RSNA_Knee_Abnormality_Detection` — a competitor's public baseline

- **Take:** the label names and their descriptions; the DICOM preprocessing checklist (spatial
  sort by `ImagePositionPatient` projected on the `ImageOrientationPatient` normal, `MONOCHROME1`
  inversion, rescale slope/intercept, multi-frame fallback, joint percentile clipping); the
  series-selection priority; and their leaderboard reference points (0.613 → 0.664), which
  calibrate what a competent 2.5D baseline is worth.
- **Do not take:** the architecture. Mean pooling over slices is wrong for the rubric this
  competition actually uses (`STRATEGY.md` I4), and they say themselves it underweights focal
  findings.
- **Diverge:** they select one primary series per plane; we intend to use all six plane×sequence
  slots with a presence mask, and eventually to stop treating them as separate streams at all.

## Conventions

- **Idea IDs are stable.** `STRATEGY.md` gives every idea an ID (`L2`, `I4`, `P1`, `E7`, `X1` …).
  `STATE.md` queue items and `EXPERIMENTS.md` rows cite them instead of restating them. If an
  idea is dropped, its ID is retired, never reused.
- **Two CV numbers, always.** Grouped and random, on the frozen folds, in that order. Their
  difference is a measurement in its own right (`STRATEGY.md` V2).
- **Never a bare number on the 58 gold studies.** Bootstrap interval or nothing (V4).
- **One change per run**, and every run gets a row in `EXPERIMENTS.md` — including the failures.
- **Folds are frozen once and never regenerated.** A number computed on different folds is not
  comparable to anything else in the log and must be marked as such.
- **Aggregates leave Kaggle; rows do not.** Anything reported back into a session is a count, a
  mean, a distribution or a metric — never report text, never pixel data, never per-study rows.

## Gotchas

- **Report text and pixel data must never enter an agent session.** Competition Rule 4.b (Data
  Security) plausibly forbids making competition data available to any party not participating,
  and a hosted assistant is such a party. This binds the user as much as the agent: do not paste
  report excerpts, DICOM contents or per-study rows into chat, and do not ask the agent to
  "have a look at" a study. Schemas, column names, aggregate statistics, code and metrics are
  fine. Any report processing runs with **open-weights models on Kaggle or Colab**, never through
  a hosted API. Internet-off applies to the *submission* notebook only, so offline label
  generation during development is unrestricted.
- **Kaggle and rsna.org are blocked by the egress proxy in agent sessions.** `www.kaggle.com`,
  `www.rsna.org` and several news sites all return `EGRESS_BLOCKED`; web *search* works and
  `github.com` / `raw.githubusercontent.com` are reachable. So the agent cannot read the
  competition pages, the leaderboard, the discussions or any Kaggle notebook. **The user is the
  only channel** for anything on Kaggle — paste summaries in, not data (see above). Do not
  attempt to route around the block; it is an organisation egress policy.
- **Never select the P100 on Kaggle.** The current Kaggle PyTorch build ships no Pascal kernels,
  so a P100 session dies at the first convolution. Choose the T4. `[T]` — reported by a
  competitor, cheap to confirm and expensive to trip over.
- **The dataset is ~570 GB.** It does not fit anywhere but Kaggle. Every pixel-touching step runs
  as a Kaggle kernel whose output the next kernel mounts directly; nothing large passes through
  Drive or a local machine. `[T]`
- **Kaggle notebook output is capped (~20 GB).** A 336 px, six-slot, 16-slice uint8 cache of all
  4,407 studies is roughly 48 GB, so it has to be built in several kernels — one or two slots
  each, as separate datasets — rather than in one pass. Confirm the current limit before
  designing around this number.
- **Time is UTC on Kaggle and the deadline is a wall.** Final submission 2026-10-22; entry and
  team-merger deadline 2026-10-15 `[T]`. Anything that must be *selected* has to exist days
  earlier, not hours.

## Known-bad approaches

- **A scanner fingerprint that includes `ImagingFrequency` is useless as a fold key** — it varies
  per scan rather than per scanner (63.685238 vs 63.685256) and produces thousands of singleton
  groups. Group on `language | manufacturer | model` instead. `[T]`
- **Random K-fold lies here.** It reportedly inflates macro AUC by ~0.053 through site
  memorisation, and one team measured a 0.136 gap on their own model. Grouped folds are the
  decision metric; random folds are reported alongside only as the optimistic bound. `[T]`
- **Mapping "not mentioned" to 0 is wrong, and wrong in a site-correlated way.** Report length and
  structure vary from 1.6 % to 99.8 % section-header rate by language, and a short report simply
  does not list negatives. `[T]`
- **Plain horizontal-flip augmentation is wrong** — it exchanges medial and lateral, which are
  distinct labels in four of the twelve. The public baseline's fix is to forbid the flip; ours is
  to flip *and swap the labels*, masking MCL (`STRATEGY.md` I3). Do not simply re-enable h-flip.
- **Mean pooling over slices** dilutes a two-slice finding by fifteen times and is wrong for
  every quantifier the rubric actually uses (`STRATEGY.md` I4).
