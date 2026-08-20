# STRATEGY — how we intend to win

**Read when:** before proposing or judging any experiment. **Changes:** when a belief is
falsified, a bet is priced, or an idea is spent.

This file holds the reasoning: what the competition actually rewards, what we believe about it
and how strongly, and every idea we have for exploiting that — ranked, priced, and each with the
test that would settle it. `STATE.md` holds the ordered queue and what has landed;
`EXPERIMENTS.md` holds what each run measured. Nothing is repeated between the three.

---

## 0. How to read the confidence marks

Kaggle and rsna.org are **blocked by the egress proxy in agent sessions**, so much of §1 was
assembled from search results and from two public third-party repositories, not from the
competition pages themselves. Every factual claim carries its provenance:

| Mark | Means |
|---|---|
| **[V]** | Verified — seen in two or more independent sources during research |
| **[T]** | Third-party — one public source (a competitor's public repo), plausible, **unverified** |
| **[H]** | Hypothesis or derivation of ours — reasoning, not observation |

**Nothing marked [T] may be used as the basis of an irreversible decision until a session with
Kaggle access confirms it.** That is queue item 1 in `STATE.md`, and it exists because roughly
40% of this document is currently [T].

---

## 1. The competition, in facts

| Fact | Value | Mark |
|---|---|---|
| Competition | RSNA Knee Abnormality Detection, `rsna-knee-abnormality-detection` | [V] |
| Task | 12 binary findings per knee MRI **study** | [V] |
| Metric | **Macro-averaged ROC-AUC** over the 12 labels | [V] |
| Format | Kaggle **code competition** — notebook submission, internet off, **≤9 h** | [T] |
| Final submission | **2026-10-22**; entry/merger deadline 2026-10-15 | [V] / [T] |
| Prize pool | **$77,000**, including a **separate efficiency track** | [V] |
| Efficiency prizes | $18,000 over 3 places | [T] |
| Train studies | **4,407** | [V] |
| Studies with all 12 labels | **58 (1.3 %)** | [V] |
| Studies with a report only | **4,349 (98.7 %)** | [V] |
| Test studies | ~1,300; public LB 30 %, private 70 % | [T] |
| Total dataset size | **569.8 GB**, ~819,640 files | [T] |
| Train series | 24,371 (3–14 per study, median 5) | [T] |
| Slices per series | 11–320, median ~30 | [T] |
| Planes | Sagittal / Coronal / Axial, all three present in every train study | [T] |
| Sites | 16 or 19 — **sources disagree**, across five continents | [V] (conflicting) |
| Report languages | 12; English ~39 %, then Turkish, Spanish, Greek, German, Cyrillic, French, Dutch | [V] / [T] |

**The 12 labels** [V]: ACL · MCL · Medial Meniscus · Lateral Meniscus · Medial OA · Lateral OA ·
PF OA · Effusion · Synovitis · Baker's · Contusion · Fracture.

### 1.1 How the ground truth was made — the single most important fact

Ground truth is **image-derived**: two subspecialty MSK radiologists reading the pixels,
adjudicated by a third. The reports are ordinary clinical reads by one signing radiologist.
These are different instruments, and the host has said the image label wins when they
disagree. An independent audit on 20 of the 58 dual-labelled studies put report-derived
agreement at **82.5 %**. [T]

Every criterion is **severity-thresholded**, and borderline findings were graded **negative**
to favour specificity: [T]

- **ACL** — high-grade partial or full tear (>50 % of fibres). Signal change or thickening
  without discontinuity is **negative**.
- **MCL** — high-grade partial or complete **acute** tear. Low-grade sprains, chronic change:
  **negative**.
- **Meniscus** — abnormal signal **definitely contacting the surface on ≥2 images**, or a
  morphologic abnormality. Intrasubstance degeneration that does not reach the surface:
  **negative**.
- **OA** (×3 compartments) — a **moderate or large area (≥ ~1 cm)** of cartilage loss
  **>50 % of thickness**.
- **Effusion / Baker's** — a **moderate or large** fluid collection.
- **Contusion** — marrow-oedema-like signal from impact, **without** a discrete fracture line.
- **Fracture** — an acute cortical break or fracture line.

If this is true, the labels are not noisy — they follow a rubric, and the rubric is public.
Almost everything in §3 and §5 follows from it.

### 1.2 Where the field stood on 8 Aug 2026 [T]

Public LB top 0.939, then 0.933, 0.929, and a dense cluster at exactly **0.891** — the
signature of a public baseline being forked unchanged. 676 teams. The public baseline already
does multilingual rule extraction, physical-scale normalisation, six plane×sequence slots with
a presence mask, and DINOv2-small at 224–336 px. **0.891 is the floor, not a target.** The
interesting question is the 0.048 between the fork cluster and the leader.

---

## 2. What the metric actually rewards

Macro ROC-AUC over 12 labels is a much stranger objective than it looks, and most of our edge
comes from taking its consequences literally.

**It is rank-only, per label.** Only the ordering of the 4,407 (or 1,300) studies within one
label column matters. Consequences:

1. **Calibration is worthless.** Probabilities, thresholds, prevalence matching, class balance —
   none of it can change the score. Any monotone transform of a column is free.
2. **Soft, ordinal, uncalibrated targets are legal.** We do not need to know whether a study is
   positive. We need to know whether it is *worse than* another study. That is a far weaker
   requirement, and reports supply it directly.
3. **Losses that optimise ranking beat losses that optimise classification.** A pairwise
   logistic (RankNet) loss is a differentiable lower bound on AUC. BCE is not.
4. **Ensembling should average ranks, not probabilities.** Rank-averaging is invariant to each
   member's scale and monotone quirks; probability-averaging is not.
5. **The 12 columns are completely independent.** They can have different models, different
   resolutions, different input slots, different ensembles. Nothing couples them but our
   convenience.

**It is macro-averaged.** Consequences:

6. **Every label is worth exactly the same**, no matter how rare. A label with 40 positives in
   the test set carries the same 1/12 of the score as one with 700.
7. **The gradient of effort points at your worst label.** Moving your weakest column from 0.60
   to 0.70 is worth exactly as much as moving your best from 0.90 to 1.00 — and is perhaps ten
   times easier. This is the most under-exploited property of the whole competition.
8. **Rare labels dominate the variance** of the private score. A uniformly decent model beats a
   spiky one of the same mean.
9. **A column you cannot predict costs nothing to surrender.** A constant column scores exactly
   0.5. A column your model gets *backwards* scores below 0.5 — and flipping its sign is free.

---

## 3. Three reframes

### Reframe 1 — this is a weak-supervision problem wearing a computer-vision costume

58 labelled studies out of 4,407. There is no supervised image dataset here; there is a corpus
of 4,349 multilingual reports and an instruction to manufacture one. Whoever turns text into
the best training targets sets the ceiling for every vision model trained downstream. Spend
early effort on labels, not architectures.

### Reframe 2 — the rubric is a severity threshold and the metric is a rank, so fit the severity axis, not the label

This is our central bet, and it is a step past what the public work does.

The failure everyone is fighting is that a report saying *"small effusion"* or *"mild
chondropathy"* or *"grade 2b intrasubstance signal"* is correctly labelled **0** by the rubric.
Treated as a binary target, that is 18 % label error. Treated as a *rank*, it is not error at
all — it is precise information that the study sits below the threshold but above a normal knee.

So: extract an **ordinal severity** per label from the report, and train the model to reproduce
the **ordering**, never the binary decision. A model that ranks severity correctly scores the
same AUC as one that reproduces the radiologists' threshold exactly, because AUC is invariant to
where you put the cut. We get to skip the hardest part of the problem — deciding where the
threshold is — by never needing to know.

Concretely (`L2` below): a pairwise loss over report-derived severity pairs, weighted by the
severity gap, so confident comparisons (`"complete rupture"` vs `"intact"`) dominate and
near-threshold comparisons (`"mild"` vs `"moderate"`) contribute little. Unmentioned findings
simply form no pair. Nothing needs calibrating; nothing needs a threshold; missing labels are
native rather than imputed.

### Reframe 3 — the efficiency track is a second prize on the same work, and it is under-contested

The published efficiency metric is [T]

```
Efficiency = AUC / (Benchmark − maxAUC) + RuntimeSeconds / 32400        (minimise)
```

with `Benchmark` = the sample-submission AUC (0.5) and `maxAUC` = the best private-LB score.
The denominator is negative, so lower runtime and higher AUC both reduce it.

The exchange rate, and it is **insensitive to the unknown `maxAUC`**: [H]

| maxAUC | Seconds worth 0.01 AUC |
|---|---|
| 0.94 | 736 |
| 0.95 | **720** |
| 0.96 | 704 |

**+0.001 AUC ≙ 72 seconds. An extra hour of runtime must buy +0.05 AUC to break even.** Nothing
buys +0.05 AUC per hour once you are above 0.90. Worked examples at maxAUC = 0.95:

| Submission | AUC | Runtime | Efficiency | |
|---|---|---|---|---|
| Fast and good | 0.905 | 15 min | **−1.983** | ✅ best |
| Fast and good | 0.910 | 30 min | −1.967 | |
| Fast, weaker | 0.880 | 8 min | −1.941 | |
| Strong, slow | 0.920 | 3 h | −1.711 | |
| Everything, 8 h | 0.935 | 8 h | −1.189 | ✗ |

Burning the full 9 h costs 1.0 — the same as giving away 0.45 AUC. The target is roughly
**0.90+ AUC in under 25 minutes**, and the work that gets us there (distillation, slot pruning,
cheap decoding) is the same work that makes main-track iteration fast. It is not a fork in the
road; it is a second ticket on the same effort.

---

## 4. The constraint ledger

| Constraint | Reality | What it forces |
|---|---|---|
| **Storage** | ~570 GB of DICOM [T]; Kaggle notebook output ~20 GB; Drive is far smaller | All heavy pixel work happens on Kaggle, kernel-to-kernel. Nothing large crosses a local machine or Drive |
| **Train compute** | Kaggle ~30 GPU-h/week (T4); Colab Pro units are a supplement | ~250–270 T4-hours to the deadline. That is ~30 full training runs at 8 h. Budget them |
| **Inference compute** | 9 h for ~1,300 studies = **25 s/study** | The main track is *not* runtime-constrained. Training compute is the real limit |
| **Efficiency runtime** | ~25 min target = **~1.1 s/study**, including notebook startup and imports | Decode cost becomes comparable to model cost. §6 is a separate design, not a smaller version of the main one |
| **Time** | 63 days from 2026-08-20 | ~5 phases. Any idea needing more than a week must earn it before it starts |
| **Rules — data security** | Rule 4.b plausibly forbids sending competition data to any third party [T] | **No report text, no pixel data, no per-study rows in an agent session.** Aggregates, schemas and code only. Open-weights models run locally or on Kaggle |
| **Rules — external data** | MRNet, fastMRI+, OAI, SKM-TEA are click-through licensed; unclear whether they count as "freely and publicly available" [T] | Treated as blocked. Do not build anything that depends on them until the host rules |
| **Hardware** | Kaggle's PyTorch ships no Pascal kernels — a P100 session dies at the first convolution [T] | Always select T4 |
| **Agent access** | Kaggle and rsna.org are blocked from this session | The user is the only channel to the competition pages, the LB, and any run output |

---

## 5. Idea bank

Ranked within each family. **Cost** is our time plus GPU-hours; **Edge** is how much of this we
expect to be doing that most of the field is not. Every entry names the test that settles it, so
none of them can quietly become an article of faith. IDs are stable —
`EXPERIMENTS.md` refers to them.

### 5.1 Labels and supervision — where the ceiling is set

**L1. Ordinal severity extraction, with two lexicons rather than one.** [T-confirmed direction]
Reports grade findings consistently across languages (`grade 2b`, `grado 4`, `Outerbridge`,
`mild/moderate/severe`, `leve`, `geringe`, `ελάχιστη`, `massive`). But the rubric asks two
different questions: **"how much?"** for Effusion, Synovitis, Baker's and the three OA labels,
and **"what kind?"** for ACL, MCL, both menisci, Contusion, Fracture. Magnitude vocabulary for
the first six, categorical vocabulary for the second six. A third party measured **+0.046 macro
AUC over presence extraction** on the 58 gold studies, 11/12 labels improved. *Cost: days.
Edge: medium — the public baseline extracts presence.* **Test:** bootstrap CI on the 58 gold,
never a point estimate.

**L2. Train with a pairwise ranking loss over severity, not BCE over a binarised label.** [H]
The metric's own surrogate. For label ℓ and studies i, j with extracted severities `s_i > s_j`:

```
loss = Σ_pairs  w_ij · softplus( −( f_ℓ(x_i) − f_ℓ(x_j) ) / τ )      w_ij ∝ (s_i − s_j)
```

Gap-weighting means confident comparisons dominate and near-threshold ones — exactly where the
report/image disagreement lives — contribute almost nothing. Unmentioned findings form no pair
instead of being imputed as 0. No calibration, no threshold, no prevalence assumption anywhere.
*Cost: a day to implement, then it is free. Edge: high — we have seen nobody do this here.*
**Test:** same folds, same labeller, swap the loss. Grouped OOF macro-AUC.

**L3. "Unmentioned" is missing-not-at-random, and the missingness is site-shaped.** [T+H]
A 30-word report does not list negatives; a 300-word structured one does. Section-header rates
run from 1.6 % (German) to 99.8 % (Spanish), and format tracks language, which tracks site — so
mapping *unmentioned → 0* injects a **site-correlated bias into the labels themselves**. Model
the reporting propensity: estimate `P(mentioned | present, site, label)` and weight accordingly,
so silence in a long structured report is near-evidence of absence and silence in a short one is
almost no evidence at all. *Cost: a day. Edge: high.* **Test:** does the grouped-vs-random CV
gap shrink?

**L4. A noise-transition layer, fitted on the 58 gold.** [H]
The gold set is too small to train on and exactly the right size to *calibrate a mapping*. Fit a
per-label 2×2 transition `P(gold | report state)`, train the network on weak labels **through**
that layer, and drop the layer at test. This uses the 58 studies for the one thing they can
support — estimating a low-dimensional correction — instead of the thing they cannot (fitting a
network). *Cost: a day. Edge: high.* **Test:** leave-one-out on the 58, plus grouped OOF.

**L5. Several independent labellers, with disagreement as an uncertainty channel.** [T+H]
Build at least three: hand-written rules (L1), an open-weights multilingual LLM run on Kaggle,
and report-embedding kNN (L6). Where they agree, weight the study up; where they disagree, weight
it down rather than forcing a winner. Cheap, robust, and it also gives ensemble diversity along
the axis that matters most here — label source, not model seed. *Cost: 2–3 days. Edge: medium.*

**L6. Label propagation through report embeddings.** [H]
Embed all 4,407 reports with a frozen multilingual encoder and propagate the 58 gold labels to
their nearest neighbours in report space. It sidesteps lexicon engineering entirely, works
across all 12 languages for free, and is the only method here that uses the gold labels as
*training* signal without overfitting them. *Cost: a day. Edge: high — nobody does this.*
**Test:** leave-one-out gold AUC vs the rule labeller, per label.

**L7. Translate once, then label once.** [H]
One open-weights MT pass to normalise all reports to English collapses twelve lexicons into one.
Risk: MT flattens exactly the severity nuance L1 depends on. Worth one measurement, not faith.
*Cost: a day of Kaggle CPU. Edge: low-medium.* **Test:** L1 accuracy on translated vs native.

**L8. Extract far more than 12 findings.** [H]
The reports mention chondromalacia grade, PCL, LCL, plica, bone-marrow oedema, cysts, prior ACL
reconstruction, hardware, patellar tendinopathy, joint bodies, tibial plateau, alignment. Add
20–40 auxiliary heads. They cost nothing at inference (drop them), they trained the backbone on
five times the supervision, and several of them are strongly informative about the 12 that
count. *Cost: a day on top of L1. Edge: medium-high.*

**L9. An "overall abnormality" latent.** [H]
A single "how bad is this knee" head, supervised by *any finding mentioned* — a far less noisy
target than any individual label. Two uses: a strong auxiliary task, and a per-label blending
prior (`F4`), because findings co-occur and a weak column borrows strength from the strong ones.
*Cost: hours. Edge: medium.*

**L10. Cross-modal distillation of privileged information.** [H+T]
The report exists at train time and not at test — the textbook privileged-information setup.
Train the image encoder to additionally regress a frozen multilingual sentence embedding of the
report. This transfers everything the 12 binary columns throw away, at zero inference cost.
*Cost: a day. Edge: high, and higher variance.* **Test:** grouped OOF with and without the
auxiliary head.

**L11. Label correlation structure.** [H]
Fracture implies contusion and effusion far more often than chance; the three OA compartments
co-vary. A low-rank label-embedding head shares statistical strength toward the rare labels —
which, under macro-averaging (§2.6), is where the score is.

### 5.2 Validation you can trust

**V1. Grouped folds, frozen on day one, used forever.** [T]
Random K-fold reportedly inflates AUC by **~0.053** through site memorisation, and one team saw
a **0.136** gap. The proposed key is `language | manufacturer | model` — 75 groups, largest
5.8 %, 27 groups with ≥50 studies. A five-part scanner fingerprint including `ImagingFrequency`
does **not** work: it varies per scan, producing 2,668 singletons. *Freeze the fold assignment
in the very first data step and never regenerate it* — every number in `EXPERIMENTS.md` must be
comparable to every other.

**V2. Report grouped and random CV on every run, and treat the gap as the measurement.** [T+H]
Train and test are drawn from the *same* sites, so grouped CV is pessimistic and random CV is
optimistic; the truth is between them, and the **gap is a direct readout of how much the model
is leaning on site rather than anatomy**. Use grouped CV to choose architecture, random CV as
the optimistic bound, and the gap as the diagnostic.

**V3. Adversarial validation, train vs test.** [H]
Train a classifier to tell train studies from test studies using DICOM headers alone. If it
scores ~0.5, the distributions match and random CV is trustworthy. If it scores high, its
per-study probabilities become **importance weights** that make CV mimic the test distribution.
Standard Kaggle instrumentation; we have seen nobody apply it here. *Cost: hours. Edge: high.*

**V4. Never quote a point estimate on 58 studies.** With n=58 and per-label prevalences of
20–60 %, a bootstrap CI on macro AUC is roughly ±0.06, and per-label ±0.15. The gold set can
establish *direction*; it cannot rank two models. Anything decided on gold alone is a coin flip
wearing a decimal point.

**V5. One change per run.** With ~30 full training runs available before the deadline (§4),
a confounded run is 3 % of the campaign.

### 5.3 The leaderboard as a measuring instrument

This family is, we believe, the sharpest edge available, and it is pure arithmetic.

**P1. Per-label LB probing.** [H]
A **constant column scores exactly 0.5**. So submit real predictions for one label and constants
for the other eleven:

```
LB = ( 11 × 0.5 + AUC_ℓ ) / 12        →        AUC_ℓ = 12 × LB − 5.5
```

That recovers a label's **public-LB AUC exactly**, on ~390 real test studies, where our gold
estimate has a ±0.15 interval on 58. Twelve probes over three days — a trivial fraction of the
submission budget — and we know precisely which columns are weak *on the actual test set*.
Group probes (real predictions for a subset `S` of labels) give partial sums faster:
`LB = ((12−|S|)·0.5 + Σ_{ℓ∈S} AUC_ℓ)/12`, so four group probes localise the weak labels and
targeted probes finish the job.

Combined with §2.7 this closes a loop nobody else is running:

> **probe → find the weakest column → aim the next experiment at it → re-probe.**

Caveats, stated so they are not forgotten: it measures the *public* 30 % only; it costs
submissions; and it must stay at the level of **aggregate statistics**. Reverse-engineering
per-study labels from the LB does not generalise to the private split and is the kind of thing
that gets solutions disqualified. We do not go there.

**P2. Test-set prevalence, from the same channel.** [H]
Score a 0/1 indicator column on a chosen subset `S`. Then
`AUC = 0.5 + 0.5·( P(S | positive) − P(S | negative) )`, and two nested subsets give enough
equations to solve for the label's test prevalence. Prevalence tells us which columns carry the
private-score variance (§2.8), which is what final-submission selection turns on.

**P3. Price the site prior with a metadata-only submission.** [H]
A header-only model reportedly scores 0.6515 under random folds and 0.5981 under grouped
folds [T] — and most teams will read that as "leakage, remove it". **That reading is probably
wrong.** Train and test share the same sites, so site is not a leak; it is a legitimate,
transferable feature, and the honest estimate of its value on the LB is the *random-fold*
number, not the grouped one. One metadata-only submission settles it in an afternoon and tells
us whether to feed scanner identity to the model or strip it out. *Edge: high, and contrarian.*

**P4. The runtime channel.** [H]
The hidden test cannot be inspected — but Kaggle reports our own notebook's **runtime**, and we
control it. `time.sleep(k)` conditioned on a measured property of the hidden test turns runtime
into a readable numeric channel: *how many test series use a compressed transfer syntax*, *how
many studies are missing a slot*, *the median slice count*. One probe submission, one number
back. It is legal (we are reading our own notebook's clock), cheap, and it removes the single
biggest unknown in the efficiency design — what the hidden test actually costs to decode.
Never do this on a submission intended for either leaderboard.

**P5. Fixed-overhead probe.** [H]
Submit a notebook that writes `sample_submission.csv` and exits. Its runtime is the floor that
no optimisation can go below — notebook startup, imports, dataset mount. §6 cannot be designed
without that number.

**P6. Sign-flip audit.** [H]
Any column whose OOF AUC is *reliably* below 0.5 is information we are holding backwards.
Flipping it is free (§2.9). One third party reported PF OA at 0.415 on gold [T]. Confirm on
grouped OOF and, if real, on the LB before shipping it.

**P7. Constant-column insurance.** [H]
If a column's OOF AUC is at or below 0.5 with a wide interval, replacing it with a constant
fixes it at exactly 0.5 — same expected score, no downside variance. A candidate difference
between our two final submissions.

### 5.4 Images — what the pixels actually need

**I1. Normalise physical scale, not pixel count.** [T]
`PixelSpacing` spans 5.1× across the corpus. A fixed-pixel resize feeds the network anatomy that
differs several-fold in scale. **Crop a constant millimetre extent, then resize.** 130 mm covers
99.6 % of series and sits exactly at the knee of the coverage curve; 140 mm covers only 94.9 %.
This is a correctness requirement, not a refinement.

**I2. Centre the crop on the joint, not on the image.** [H]
Sagittal, coronal and axial acquisitions of one study all target the same anatomy, so **the
intersection of their three fields of view in patient coordinates is the joint centre** — free,
deterministic, no learning, computed from `ImagePositionPatient` and `ImageOrientationPatient`
alone. Fall back to the intensity centroid where a plane is missing. A fixed-centre crop wastes
a variable fraction of a 130 mm window on air; this recovers it. *Cost: hours. Edge: high.*

**I3. Horizontal flip **with a label swap** — the augmentation the public baseline refuses.** [H]
The public baseline forbids h-flip because it exchanges medial and lateral. That is the right
observation and the wrong conclusion. Flip the image **and swap the labels**:
`Medial Meniscus ↔ Lateral Meniscus`, `Medial OA ↔ Lateral OA`; mask **MCL** out of the loss on
flipped copies, since its lateral counterpart is not a label. ACL, PF OA, Effusion, Synovitis,
Baker's, Contusion and Fracture are unaffected. This doubles the effective dataset, imposes the
correct anatomical symmetry as an inductive bias, makes laterality canonicalisation loss-free
rather than lossy, and gives a valid TTA member at test. *Cost: hours. Edge: high — this is a
mistake in the public baseline that half the field has forked.*

**I4. Pool the way the rubric quantifies.** [H] — *our best idea*
The rubric does not ask "is it present". It states an explicit quantifier per finding, and the
quantifier tells us the aggregation function:

| Rubric wording | Quantifier | Pooling over slices |
|---|---|---|
| meniscal signal contacting the surface **on ≥2 images** | count ≥ 2 | soft **top-2** / count head |
| a **≥1 cm area** of >50 % cartilage loss | extent | **area**-weighted sum over slices |
| **moderate or large** effusion / Baker's | volume | **sum** over slices |
| an acute cortical break | ∃ | **max** over slices |
| >50 % of ACL fibres disrupted | proportion | **fraction** over the structure |

Mean pooling — what the public baseline does — is wrong for **all five**. Fitting the pooling
operator to the stated criterion is nearly free, is why the labels look the way they do, and
directly attacks the "mean pooling underweights focal findings" failure everyone reports.
*Cost: a day. Edge: very high; we have seen this nowhere.*

**I5. Compartment sub-crops for the five side-specific labels.** [H]
Once the joint centre is known (I2), the medial and lateral compartments are geometrically
determined. Medial OA needs the medial third of the coronal stack — nothing else. Cropping to it
is a **3× effective-resolution gain at identical cost**, and it targets 5 of the 12 labels
(both menisci, both tibiofemoral OA, MCL). A patellofemoral crop does the same for PF OA.
*Cost: a day. Edge: very high.*

**I6. Resolution where it matters, and only there.** [T+H]
A meniscal tear is a ~1 mm feature; Nyquist wants ≤0.5 mm/px. At a 130 mm crop, 224 px gives
0.58 mm/px (**too coarse**) and 336 px gives 0.39 mm/px (adequate). But Effusion, Baker's and
Synovitis are large findings and are fine at 224. **Route resolution per label.** This pays
twice: accuracy in the main track, runtime in the efficiency track. Cache at 336 — downsampling
later is free, upsampling is impossible.

**I7. Attention or top-k pooling over slices, never mean.** [T+H]
Subsumed by I4 where the rubric is explicit; the general form elsewhere. A finding on 2 of 30
slices is diluted 15× by a mean.

**I8. A label-conditioned query head.** [H]
Twelve learned queries attending over the token set of all slots × slices, one transformer
decoder layer. Each label picks its own slices and its own planes — PF OA is an axial finding,
the cruciates are sagittal, the compartments are coronal — instead of sharing one pooled vector.
It is ~12 queries of extra compute, it replaces both the pooling and the per-label heads, and
the attention maps are free interpretability for the solution write-up (which RSNA prizes may
weigh). *Cost: 2 days. Edge: medium-high.*

**I9. Cross-plane consistency.** [H]
A real finding appears in more than one plane; a texture artefact does not. Add a consistency
term between per-plane predictions. It is a regulariser that encodes how the ground truth was
actually produced.

**I10. Slice-axis context beyond 2.5D triplets.** [H]
A small transformer or GRU over per-slice embeddings costs less than 3D convolutions and carries
much more than an `[n−2, n, n+2]` triplet.

**I11. Condition on sequence, don't waste capacity distinguishing it.** [H]
FiLM the backbone on `(plane, fluid-sensitive, TR/TE bucket)` so one set of weights serves all
six slots without spending capacity on telling them apart. `Fluid_Sensitive` and
`Fat_Suppression` are reportedly **perfectly correlated** — one bit, not two [T].

**I12. Slot dropout, and a presence mask.** [T+H]
Slot coverage across studies runs from 100 % (axial fluid-sensitive) to 19.4 % (axial
non-fluid) [T]. Train with random slot dropout so the model degrades gracefully when the hidden
test is missing one.

**I13. Self-supervised pretraining on 819k in-domain slices — including the test set.** [H]
The largest untapped resource in the competition is the unlabelled pixels, and the test images
are ours to pretrain on (they are given). An MAE or DINO run on knee MRI slices would put a
genuinely in-domain backbone under everything else. Expensive — this is the one idea that wants
Colab Pro A100 time rather than Kaggle T4s. *Cost: 20–40 GPU-h. Edge: high, most teams will not
pay it.* Park until the cheap wins are banked.

**I14. Backbone selection is an accuracy-per-FLOP question, not an accuracy question.** Because
of the efficiency track, rank candidates (DINOv2-S/B, ConvNeXt-T, EfficientNet, RadImageNet,
BiomedCLIP) on T4 fp16 throughput as well as OOF AUC. Weights must be attached as a Kaggle
dataset — internet is off in the submission.

### 5.5 Site and domain

**D1. Site is a feature, not a leak — probably.** [H] See P3. Test and train share the sites;
a study from a site whose case mix is 60 % ACL tears genuinely *is* more likely to have one.
Most of the field will "correctly" strip this and lose the points. **But** the host has warned
that prevalence differs between train, public and private splits [T], which is exactly the
condition under which this bet fails. Price it with a submission before believing either way.

**D2. Site-conditional rank normalisation at test time.** [H]
All ~1,300 test studies are in hand at inference — this is a transductive setting. Rank-normalise
predictions within each detected scanner group to remove site-driven score *shifts*, then blend
with the global ranking at a weight tuned on grouped OOF. The blend weight is the knob that
trades D1's prior against D2's correction; do not choose it by argument, choose it by CV.

**D3. Domain-adversarial training** (gradient reversal on the 75 site groups) to suppress site
information. Cheap to try; expect a wash if D1 is right. Run it to know, not to believe.

**D4. Test-time statistic adaptation.** Recompute normalisation statistics on the test
distribution. Minutes to implement, occasionally worth a few thousandths.

**D5. Transductive pseudo-labelling inside the submission.** [H]
Predict on the test set, take the confident tails, fine-tune the head for a few hundred steps,
re-predict. Legal, sometimes real, and costs runtime — **main track only**; it is precisely the
kind of thing the efficiency exchange rate forbids.

### 5.6 Fusion

**F1. Rank-average, per label.** [H] Not probability-average. §2.4.

**F2. Buy diversity along the label-source axis first.** [H]
Label noise is the dominant error term (Reframe 1), so two models trained on *different label
sources* decorrelate far more than two seeds of the same model. Order of value: label source >
pooling operator > resolution > slot subset > backbone > seed.

**F3. Optimise ensemble weights independently per label.** [H]
Macro-AUC decomposes completely, so there is no reason at all to share blend weights across the
12 columns. A per-label simplex search on grouped OOF ranks is free and exactly matches the
metric. Hill-climbing with replacement (Caruana) over the member pool is the robust version.

**F4. Blend a global-abnormality prior into the weak columns.** [H]
`rank_ℓ ← (1−α_ℓ)·rank_ℓ + α_ℓ·rank_global`, with `α_ℓ` fitted per label on OOF. Findings
co-occur, so a column with little evidence of its own borrows from L9. Costs nothing at
inference.

**F5. Two final submissions, chosen for decorrelation, not for rank.** With ~910 private
studies and 12 macro-averaged columns, the private draw is noisy. Pick the best grouped-CV
ensemble and a structurally different, simpler model — not the top two entries of one family.

### 5.7 Long shots — the ones that sound wrong until you check

High variance, high ceiling, and mostly cheap to *test* even when they would be expensive to
ship. Each is here because there is a specific reason it might work, not because it is exotic.
They are ordered by our estimate of *plausibility × payoff*, not by how strange they sound.

**X1. Stop treating the study as six 2-D stacks. Rebuild the knee.** — *the big one*

Every public approach picks one series per plane, samples slices, and runs a 2-D backbone over
six unrelated image streams. But sagittal, coronal and axial acquisitions of the same knee are
**already in a common coordinate system** — DICOM gives us `ImagePositionPatient` and
`ImageOrientationPatient` for every slice, so the map from any slot into patient space is exact
and free. Nothing has to be *learned* to register them; the geometry is in the header.

So resample all available slots onto **one isotropic patient-space grid** and hand the network a
single registered multi-channel volume of the knee instead of six unregistered stacks. Each
plane contributes high resolution along its own two axes and thick slices along the third, so
the fused volume is sharper in every direction than any single stack — this is exactly what a
radiology workstation's multi-planar reconstruction does, and it is what a radiologist looks at.

What falls out of it, all at once:

- **Cross-plane consistency (I9) becomes structural** rather than a loss term — a voxel is one
  voxel, seen by up to six acquisitions.
- **Compartment crops (I5) become exact** — medial, lateral and patellofemoral regions are
  coordinates in a known frame, not guesses on an image.
- **Physical scale (I1) and laterality (I3) are solved by construction** — the grid is in
  millimetres and the knee can be reflected into a canonical side before sampling.
- **Anatomy-aligned oblique reformats become possible.** Radiologists reformat *along* the ACL
  to judge it, and along the meniscal body for tears. We can sample slabs on those oblique
  planes, which no axis-aligned pipeline can see.
- **The fluid channel becomes real.** Registered fluid-sensitive and structural slots occupy the
  same voxel grid, so their ratio is a physically meaningful "fluid map" — the thing that makes
  effusion, synovitis and Baker's obvious to a human reader.
- **It is cheaper at inference**, which is the part that surprises. One small 3-D pass over a
  130 mm³ volume at ~0.7 mm replaces ~96 2-D forward passes. That is an efficiency-track idea
  wearing an accuracy-track costume.

Risks, honestly: slices are thick (3–3.5 mm), so the fused volume is anisotropic in practice;
patient motion between series breaks the assumption that the geometry is exact; and 3-D
backbones have far weaker pretrained initialisations than 2-D ones. Mitigation: keep a 2-D
backbone and sample **reformatted 2-D planes** out of the registered volume — all of the
benefits above except the last, none of the pretraining loss.
*Cost: 3–4 days. Edge: very high.* **Test:** same backbone, same labels, same folds — slices
from raw stacks versus slices reformatted from the registered volume.

**X2. Read the identifiers before reading the pixels.**

Half an hour of archaeology, occasionally decisive, and skipped by nearly everyone because it
feels beneath the problem:

- **`StudyInstanceUID` prefixes.** DICOM UIDs are hierarchical and begin with an organisation
  root. If the organisers re-issued UIDs under one root this yields nothing — but if any
  original roots survived, **the prefix is an exact institution key**, available at test time,
  requiring zero DICOM reads. That would be a better fold key than `language|manufacturer|model`
  (V1) and a better site feature than anything in §5.5.
- **UID suffixes and dates.** UID tails sometimes encode timestamps. If the test split is
  *temporally* later than train, that is a distribution shift worth knowing about — and a
  feature worth having.
- **Row order.** `train.csv`, `test.csv` and `sample_submission.csv` are sometimes ordered by
  site, by date, or by label. Check the autocorrelation of everything against row index.
- **Near-duplicate studies.** Pseudonymous `PatientID`s are reportedly unique [T], but
  de-identification can re-randomise them per study and hide genuine repeats. A cheap fingerprint
  (header tuple plus a pixel hash of one mid-slice) finds repeated patients across train **and
  test**. Repeats inside train are a fold-leak to fix; a train/test repeat is something else
  entirely.

*Cost: half a day, once, on the metadata scan we already have to do. Edge: high, because the
payoff is binary and nobody checks.*

**X3. The negatives are contaminated and the positives are pure — so use PU learning.**

"Ambiguous or borderline findings were graded as negative to favour specificity" [T] is not a
footnote about label noise. It is a precise statement that the **negative class contains an
unknown fraction of true-but-borderline positives while the positive class is clean**. That is
the positive-unlabelled setting, exactly, and it has a correct treatment: a non-negative risk
estimator with an estimated contamination rate, rather than a symmetric loss that assumes both
classes are equally trustworthy.

It composes with the ranking loss (L2) — asymmetric pair weighting, confident on
positive-over-negative pairs and sceptical of negative-over-negative ones — and the
contamination rate per label is estimable from the 58 gold studies.
*Cost: a day. Edge: high; almost nobody reaches for PU learning in a Kaggle CV competition.*

**X4. Do not model the label. Model the panel that produced it.**

The gold labels came from **two subspecialty readers plus an adjudicator, with ties broken
toward negative** [T]. So build the same machine: a deliberately **strict** labeller, a
deliberately **lenient** one, and an adjudication rule that resolves them the way the panel did.
Train separate models on the strict and lenient targets and combine their ranks.

The point is not the ensemble. It is that the disagreement between a strict and a lenient reader
*is* the borderline zone — the exact region where the rubric threw the coin — so the strict/
lenient gap gives us a **per-study, per-label estimate of ambiguity** with no extra supervision.
Feed it to the pair weighting in L2, to the sample weighting in L5, and to the cascade in E7.
*Cost: 2 days on top of L1. Edge: high.*

**X5. Let the rubric be the classifier.**

We have the official criteria in words. Build a CLIP-style two-tower model — image encoder plus
a frozen multilingual text encoder — and classify by cosine similarity to text prototypes
written **from the rubric itself**: *"complete discontinuity of the anterior cruciate ligament"*
versus *"intact anterior cruciate ligament with mild intrasubstance signal"*. The severity axis
is then defined by **interpolating between prompts**, not by a lexicon we hand-built.

Two things make this less mad than it sounds here. First, we already want an image→report
alignment objective for other reasons (L10), so the second tower is nearly free. Second, the
rubric's exact wording is the *definition* of the ground truth — using it verbatim as the
classifier is closer to the target than any proxy label we can construct. It also transfers
across all 12 languages without a lexicon, and costs 12 dot products at inference.
*Cost: 2–3 days. Edge: very high, and genuinely uncertain.*

**X6. Reports have authors, and authors have thresholds.**

Gold labels came from one central panel; the reports came from dozens of local radiologists, each
with their own reporting threshold and house style. That is a textbook **mixed-effects** problem:
`severity_observed = finding_true + site_bias + noise`. Fit the labeller as a random-effects model
with a per-site (per-language, per-institution) intercept per label, and the site-correlated label
bias that L3 identifies is *estimated and removed* rather than merely down-weighted.
*Cost: a day, and it is statistics rather than GPU. Edge: high.*

**X7. Ask what the 58 gold studies are a sample of.**

They are ~2× enriched in positives and every one has at least one finding [T] — so they are not a
random draw from the training corpus. The interesting question is what they *are* a draw from. If
the 58 were annotated in the same batch, by the same panel, under the same sampling rule as the
**test set**, then they are a small sample of the test distribution, and they should be weighted
far more heavily than their count suggests.

This is answerable in an afternoon with the machinery of V3: train an adversarial classifier
58-versus-corpus, and another 58-versus-test, on headers alone. If the 58 look like the test set
and unlike the rest of train, that changes how every downstream weight is set.
*Cost: hours. Edge: high, and nobody will have asked.*

**X8. Cascade at the I/O level, not the compute level.**

E7 saves GPU time by only running the heavy model on the uncertain middle of the ranking. The
sharper version saves the **decode** as well: for studies the cheap pass already places firmly in
either tail, *never read their pixels at all* beyond the scout slices. Since decoding is
comparable to inference at the efficiency budget (§6), skipping I/O for 40 % of the test set is a
larger win than any kernel-level optimisation — and it is available only because AUC tolerates
coarse ranking at the extremes.
*Cost: a day. Edge: very high, inside the efficiency track.*

**X9. Ship the compiled engine, not the model.**

`torch.compile` and TensorRT spend **minutes** building kernels — pure loss at 72 seconds per
0.001 AUC. Kaggle's hardware is fixed and known (T4), so build the engine offline for the exact
shapes and attach it as a dataset, with a plain-PyTorch fallback if it fails to load. Fix the
input shape so CUDA graphs hold and nothing recompiles mid-run. *Cost: a day. Edge: high, and
almost purely mechanical.*

**X10. Clean the labels with the model, then retrain.**

After the first honest OOF, the studies where the model and the report disagree most are either
label errors or model errors, and confident-learning gives a principled way to tell them apart.
Down-weight or re-label the worst, retrain, repeat — twice, not ten times, or we will simply be
fitting our own predictions. *Cost: hours per round. Edge: medium-high.*

**X11. Free supervision from geometry: predict one plane from another.**

A self-supervised objective that needs no label at all and uses **train and test studies alike**:
predict the coronal representation of a study from its sagittal one. It is far cheaper than a
general MAE (I13), it is targeted at exactly the invariance we want, and — like everything
transductive here — the test images are ours to use.
*Cost: a day. Edge: medium-high.*

**X12. Twelve specialists instead of one generalist.**

Macro-AUC decomposes completely (§2.5), so there is no principled reason to share a backbone
across labels beyond our own convenience. Twelve small label-specific models — each with its own
slots, crop, resolution and pooling operator — can beat one large shared one at similar total
compute, and in the efficiency track we then pay only for the specialists we keep. It is
laborious, which is exactly why the field will not do it, and the metric rewards it exactly.
*Cost: high. Edge: medium-high.* Do it for the two or three weakest columns first (§2.7), not
for all twelve at once.

**X13. Disagreement under symmetry as a free confidence signal.**

The flip-and-swap augmentation (I3) gives a second, genuinely independent view of the same study.
Where the two views agree, the prediction is stable; where they disagree, it is not. That is a
per-study confidence estimate costing one extra forward pass, and it is exactly the signal the
cascade (E7, X8) needs to decide who gets the expensive model. One idea paying for two.

**X14. And the one we will not do.**

The public LB is ~390 studies. With enough probes one could, in principle, reverse-engineer
individual labels from it. It would raise the public score, it would do nothing for the private
one, and it is the kind of thing that gets solutions disqualified. P1 and P2 stay at the level of
**aggregate statistics** — per-label AUC and prevalence — and go no further. Recording the line
here so that no future session has to rediscover where it is.

### 5.8 Rules, risk and prize mechanics

**R1. No competition data ever enters an agent session.** Report text, pixel data and per-study
rows stay on Kaggle and Colab. Aggregates, schemas, code and metrics only. This is `PLAYBOOK.md`'s
loudest entry and it binds the user as well as the agent.

**R2. External datasets stay blocked** until the host rules on click-through licences. Nothing
in the queue depends on them.

**R3. Confirm how the efficiency entry is selected** — automatically from all submissions, or
designated. The answer changes whether we ship one submission or two.

**R4. Prizes usually require a documented solution and code delivery**, and RSNA presents
winners at the annual meeting. `EXPERIMENTS.md`, kept honestly, *is* four-fifths of that
document. Write it as we go; do not reconstruct it in November.

**R5. Check for side prizes** — novelty, fairness, or clinical-utility awards attach to RSNA
challenges more often than to ordinary Kaggle competitions, and they are contested by far fewer
teams.

---

## 6. The efficiency submission, designed as its own thing

Target: **≥0.90 AUC in under 25 minutes**, ~1.1 s/study including startup. At that budget,
**decoding is comparable to inference**, which is a different engineering problem from the main
track and needs a different design.

**E1. Distil the main-track ensemble into one small student — and distil *ranks*.** The single
largest AUC-per-FLOP lever there is. The teacher's ordering is the target; its probabilities are
irrelevant (§2.1).

**E2. Read pixels without decoding them.** Every training series is reportedly **Explicit VR
Little Endian, uncompressed** [T]. That means `PixelData` is a raw byte array at a known offset:
read headers with `stop_before_pixels=True`, then `np.memmap` and take a **strided** slice.
Downsampling 4× on read cuts I/O ~16× before any decode work happens. Keep a `pylibjpeg` path
for the compressed syntaxes the data description mentions — **P4 tells us whether the hidden
test contains any**, which is exactly why P4 exists.

**E3. Overlap decode and inference.** Most submissions decode everything, then infer. A
producer/consumer pipeline — CPU workers decoding while the GPU runs — typically halves
wall-clock for free. Nobody's leaderboard position was ever lost to this; several efficiency
prizes have been.

**E4. Foveated slice selection.** A coarse scout pass at ¼ resolution over strided slices
identifies which slices matter; only those are read at full resolution. Combines with E2 — the
scout is nearly free because it is the strided read.

**E5. Prune slots and slices to what each label needs.** Measure marginal AUC per slot. If three
of the six slots carry 98 % of the score, the other three are pure runtime. Per-label routing
(I5, I6) compounds: read the medial coronal third at 336 for Medial OA, and nothing else.

**E6. The obvious kernels: fp16, `channels_last`, `torch.compile`, CUDA graphs, batch across
studies, sort by shape to avoid padding waste.** Consider int8 with calibration. These are
multiplicative with everything above.

**E7. An AUC-aware cascade.** [H] — *our second-best idea*
AUC only cares about *pairwise ordering*, and pairs at the extremes are already ordered
correctly by a cheap model. So: run the small student on everything, then spend the expensive
model **only on the middle band of the ranking** — the ~30 % of studies whose ordering is
actually uncertain — and re-rank within that band, which leaves the global order outside it
untouched. Roughly 60 % of the heavy compute disappears for a small fraction of the AUC. This
technique exists because the metric is a rank; it would be unavailable under log loss.

**E8. Attack the fixed overhead.** No `pip install` in the submission (it is minutes of pure
loss), minimal imports, weights attached as a small dataset. P5 measures the floor.

**E10. The long shots that are really efficiency ideas.** X1 (one registered volume instead of
six 2-D stacks) replaces ~96 forward passes with one small 3-D pass. X8 skips *decoding* for the
studies the cascade has already placed in either tail. X9 ships a prebuilt engine so no minute of
the budget goes to compiling kernels. X13 gets the cascade's confidence signal for one extra
forward pass. Read §5.7 as part of this section, not separately from it.

**E9. Price every component against the ledger.** `+0.001 AUC ≙ 72 s`. Flip-and-swap TTA
doubling inference is worth it only if it buys more than its own runtime — and now that is an
arithmetic question with a number, not a matter of taste. Every row of `EXPERIMENTS.md` for an
efficiency candidate carries both AUC and seconds, so the trade is always visible.

---

## 7. The campaign — 63 days

Dates are targets, not commitments; the queue in `STATE.md` is authoritative for order.

| Phase | Days | What lands | Gate to the next phase |
|---|---|---|---|
| **0 — Recon** | Aug 20–24 | Every [T] in §1 confirmed or corrected; rules read; efficiency formula verified; overhead and runtime probes submitted | This document has no unverified load-bearing claim |
| **1 — Ground truth** | Aug 24–Sep 7 | Header scan, frozen grouped folds, severity labeller, gold evaluation with CIs, the cache | A trainable dataset exists and CV is trustworthy |
| **2 — First real model** | Sep 7–Sep 21 | Rank loss, rubric-matched pooling, flip-and-swap, joint-centred crops; first OOF and first LB | Beating the public baseline cluster on grouped CV |
| **3 — The macro-AUC loop** | Sep 21–Oct 8 | Per-label probes, specialists for the weakest columns, compartment crops, ensembling | Diminishing returns on the weakest label |
| **4 — Efficiency + close** | Oct 8–Oct 22 | Distilled student, strided decode, cascade; final ensemble; both final submissions selected; solution written | Submitted, with a day of slack |

Two rules for the whole campaign: **one change per run** (V5), and **every run gets a row in
`EXPERIMENTS.md`** — grouped CV, random CV, gold, LB, runtime — whether or not it worked.
Failed runs are the cheapest information available and the first thing anyone forgets to record.

---

## 8. What must be verified before this document is trusted

In rough order of how much of the plan collapses if the answer surprises us.

1. **Do test studies come with reports?** Everything here assumes not — that reports are
   train-time-only privileged information. RSNA's public wording ("the first to use both images
   and the text of radiology reports to train *and test* AI models") is ambiguous, and if reports
   *are* available at inference, this is a text competition and the entire plan changes shape.
   **Settle this first.**
2. **The exact efficiency formula and how the efficiency entry is selected** — §3 Reframe 3 and
   all of §6 are priced off it.
3. **The metric page**: macro ROC-AUC confirmed, and how ties and any absent labels are handled.
4. **The rules**: Rule 4.b's actual text, external data, pretrained weights, submission limits,
   number of final selections, and whether the host has since ruled on the LLM-API question.
5. **The 12 label definitions and the severity thresholds**, verbatim from the host — §1.1 is
   [T] and Reframe 2 is built on it.
6. **Data shape**: file count, total size, test size, public/private split, transfer syntaxes in
   the hidden test, and whether the 58/4,349 split is exactly as reported.
7. **Kaggle's current limits**: GPU quota per week, session length, notebook output size, private
   dataset size — §4's budget depends on all four.
8. **The leaderboard now.** §1.2 is a 12-day-old third-party snapshot.

---

## 9. Sources

Read during the 2026-08-20 research session. Kaggle and rsna.org were unreachable from the agent
session; everything below is what was reachable.

- Kaggle competition pages — **blocked by egress proxy**, never read directly
- RSNA challenge and press pages — **blocked by egress proxy**, seen only through search snippets
- Search-result summaries: competition scope, prize pool, deadline, 12 findings, macro ROC-AUC,
  the 58 / 4,349 split, site and language counts
- `github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection` — a competitor's public
  strategy and Phase-0 findings documents. The origin of most [T] marks: dataset size, series and
  slot statistics, laterality analysis, fold-grouping experiments, the host Q&A quotes, the label
  criteria, the LB snapshot, and the efficiency formula
- `github.com/JunhaoLiXD/RSNA_Knee_Abnormality_Detection` — a competitor's public baseline
  write-up: label names, data counts, series-selection and preprocessing choices, LB reference
  points (0.613 → 0.664)

Both repositories are public third-party work. They are **evidence about the problem, not a
specification and not a source of code** — see `PLAYBOOK.md` § Reference notes for what we take
from them, what we deliberately do not, and where we expect to diverge.
