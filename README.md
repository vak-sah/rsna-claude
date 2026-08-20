# NDD — notebook-driven development

<!-- Read when: orienting, or before running anything. Changes: when structure or setup changes. -->

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vak-sah/NDD-notebook-driven-development/blob/main/command_center.ipynb)

A starting point for notebook-driven development: build features in a Colab command center,
extract them to `src/` once they're settled, and keep the repo small enough to understand.

## Start

<!-- The agent deletes this section during onboarding — see START_HERE.md, Step 4. -->

**Use this template → open an agent session on _the new repo_ → say hello.**

The session has to be on your copy, not on this page's repo. *Use this template* copies the
files into a fresh repo with its own history and never writes back here, so the template can't
be damaged by starting a project — and an agent that finds itself running in the template
stops rather than onboarding it.

That is the whole procedure. `START_HERE.md` has the agent interview you — what the project is
for, what goes in and out, any references, which Drive folder, any credentials — then write the
answers into the repo, point everything at your repo, propose a route to MVP, and delete itself.
Nothing to prepare, nothing to edit by hand.

## Running it

`command_center.ipynb` is the workspace: features get built there, in as many cells as it takes
to see them working, and move into `src/` once they've settled. Click the badge and run top to
bottom on a fresh runtime.

The **config cell** runs first and holds every knob, each with the alternatives weighed and the
reason the current value won. It is the only thing you edit — setup below it just acts on those
values, mounting Drive, cloning the repo so `src/` imports, installing deps.

To keep notebook edits, use Colab's **Save in GitHub** button; that click is the commit, no PR
step. Run output is stripped automatically on push, so it never reaches git. Save before handing
back to the agent, so it works from your current notebook.

First save asks you to **Authorize googlecolab** — OAuth, nothing to store, and it may re-prompt
later. If the notebook looks stale after the agent changed it, reopen the link or append
`?flush_cache=true`. Tests are `pytest -q` from the repo root — no Drive, no network, no GPU, so
the same command works in CI, a terminal, or a cell.

Working with an agent here: `AGENTS.md` is both the contract and the entry point — it names what
to read, in what order, and how a session runs. Most agents pick it up unprompted. One that
doesn't needs a single sentence: *read `AGENTS.md` and follow it*.

## Layout

```
command_center.ipynb   the workspace — setup, config cell, features being built, output
src/pipeline/          the archive: settled logic, one module per feature, docstring at the top
tests/                 all tests. never in a notebook cell
pyproject.toml         pytest config only — makes src/ importable. not packaging
.github/workflows/     CI: runs the tests, and strips notebook output, on every push
.gitignore             keeps data, weights, caches, outputs and credentials out of git
START_HERE.md          the first-session interview. deletes itself once the repo is yours
LICENSE                Apache 2.0
README.md              this file: what, how to run, what's where, how it flows
STATE.md               what's done, what's in progress, what's next
PLAYBOOK.md            environment quirks, manual setup, solved problems, dead ends
AGENTS.md              how agents and the user work in this repo
CLAUDE.md              points Claude Code at AGENTS.md
```

Data, weights, outputs and credentials are **not** in this repo — they live under the Drive
root set in the notebook's config cell, which is the only place that path appears.

## Pipeline

<!-- input → each stage → output. one line per stage, naming the module that owns it. -->

Nothing real yet — `src/pipeline/stub.py` is a passthrough that proves the wiring works. The
first stage replaces it.
