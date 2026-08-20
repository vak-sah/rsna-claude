# START HERE — first session on a new project

**Read when:** this file exists. That means the repo is a fresh copy of the template and has
never been made specific to anything. **Deleted:** at the end of this procedure, by you.

You are the agent. This is a script for the interview that turns a generic template into *this
user's* project. Work through it in order. The user is likely an amateur in this domain and
verifies slower than you produce — so ask in small groups, wait for each answer, and never ask
for something you can read yourself.

Where an answer is really a **choice between a few known options**, offer the options rather than
an open question. Someone unfamiliar with the domain picks far faster than they compose, and the
options themselves show what's possible. Keep open questions for things only they can know.

Open the session with one line: *"This looks like a fresh copy of the template — a couple of
rounds of questions and it's yours."* Then Step 1.

Ask **Steps 2 and 3 together** in one message. They're short and independent, and two rounds cost
the user less than three for the same answers.

---

## Step 0 — Read, don't ask

Before the first question, gather these silently. Asking for any of them is a bug.

| Value | Where from |
|---|---|
| `owner/repo` | `git remote get-url origin` |
| Default branch | `git symbolic-ref refs/remotes/origin/HEAD`, or `main` |
| Suggested project name | the repo name |

**Then check you're in the right place.** If `owner/repo` is
`vak-sah/NDD-notebook-driven-development`, this *is* the template — not a copy of it. Stop
immediately, run nothing from Steps 1–6, and say so:

> This is the template repository itself, so onboarding here would consume it. Create your own
> copy first — **Use this template → Create a new repository** — then open a session on that
> repo and say hello. The template stays untouched; GitHub copies the files and never writes
> back to the source.

Onboarding is destructive by design: it rewrites the Goal, repoints every URL, and deletes this
file. Doing that to the template destroys it for everyone who clones it later. Any other
`owner/repo` means you're in a copy — carry on to Step 1.

## Step 1 — Purpose

Ask these three together, in one message, and stop:

1. **What is this project for?** One or two sentences is plenty.
2. **What goes in and what comes out?** Data, files, an API, a number, a plot, a model —
   or "nothing yet", which is a real answer at this stage.
3. **What does done look like?** The thing that, once it works, means the MVP worked.

If an answer is vague, ask **one** follow-up. Not three. A vague Goal that gets sharpened in
week two is normal and costs less than an interrogation on day one.

**Then check the plan can actually work.** Two things can invalidate it before a line is
written, and both are far cheaper to catch here than at Step 5.

*Does the shape fit?* This repo is a Colab notebook over data, extracting to `src/`. If the
answers describe something whose centre of gravity is elsewhere — a web app, a mobile app, a
service — say so before writing anything down, and name the shape that *would* work here: what
the notebook produces, and what consumes it.

*Is anything blocking?* Licensing, terms of service, cost, rate limits, or access to data the
user doesn't control. If the goal depends on any of those, say what the constraint is and whether
it kills the goal or merely shapes it, then record it in `PLAYBOOK.md` § *Gotchas* so nobody
re-derives it.

In both cases: name it, recommend a way forward, and proceed — don't stop, and don't quietly
build a queue on a premise you already doubt. The user decides with the problem visible.

## Step 2 — References

> Are there repos, papers, sites or products you want this to follow? Links, and roughly what
> to take from each. "None" is fine.

Zero, one or several. For each one given: read it **once**, now, and write three things into
`PLAYBOOK.md` § *Reference notes* — what you're taking, what you're deliberately *not* taking,
and **where this project would plausibly diverge, with the alternative named**. Those notes are
the point; re-reading a big reference every session is a tax the repo exists to avoid.

The third element is what keeps a reference useful. It made its choices under its own
constraints, and notes that only record compliance turn it into a specification, which it isn't
(`AGENTS.md` §1). Name the choices that are the user's to re-make, so they can change direction
knowing what they're trading — and don't let the reference's own pipeline become the queue in
Step 5 by default.

**If you can't actually reach it** — no network, blocked domain, paywall — you may still write
what you know, but label it in `PLAYBOOK.md` as written from prior familiarity rather than a
live read, record the block under *Gotchas*, and say so in your report. An unread reference must
never look verified. Where it matters, make "verify this from a notebook cell" the first queue
item instead of asserting it now.

## Step 3 — Environment and paths

> Three quick ones:
> - **Drive folder** for this project's data and outputs. Default `MyDrive/projects/<repo name>`
>   — the shared `projects/` parent means MyDrive's root gains one folder however many projects
>   you start, instead of one per project. `MyDrive/<repo name>` is a click shallower if you
>   prefer; deeper than two levels buys nothing.
> - **Where does the input come from?** A file you'll drop in Drive, a download, an API, or
>   nothing yet.
> - **Any credentials needed?** An API key or token — name it, don't paste it. It goes in Colab
>   Secrets or a Drive file, never in the repo.

Give a concrete default for each, and say that **`go` accepts them all** — a user without strong
opinions should be able to finish the interview in one word.

## Step 4 — Write it down

Now do all of this without asking again:

- **`STATE.md` §1** — replace the whole Goal section with theirs, plus the references. This is
  the only time you rewrite the Goal.
- **`README.md`** — the title and the one-liner under it.
- **Repo identity**, using the `owner/repo` from Step 0 — the README Colab badge, and `REPO_URL`
  in the notebook config cell. Those are the only two.
- **`DRIVE_ROOT`** in the notebook config cell — the folder from Step 3.
- **`PLAYBOOK.md`** — reference notes from Step 2; the secret's *name* and location from Step 3.
- **`README.md`** — delete the *Start* section. It has served its purpose.

Nothing in the repo should now name the template. Check with a search for the old owner/repo
and the old Drive folder before moving on.

## Step 5 — Propose the route

Replace `STATE.md` §4 Next with an ordered path to their MVP — aim for 5–10 items, each one
line. Real features, not setup: the template already ships the notebook, `src/`, `tests/` and
CI, so the first item is the first thing their project actually *does*.

Show it and say plainly that it's a proposal and reordering is expected. Then stop and wait.

This is the one approval that matters, so get it right: from here on the queue is standing
authorization, and later sessions work through it without asking again (`AGENTS.md` §2, §3).
Reordering it later is always the user's to ask for, and always free.

## Step 6 — Finish

Delete this file. Commit everything from Steps 4 and 5 as one commit, and push it **to the
default branch** — not to a feature branch with a PR. Onboarding is initialization, not a
reviewable change: there is nothing to review, and a copy whose onboarding sits unmerged on a
branch is indistinguishable from a copy that was never onboarded at all.

If your environment forces branch-based work, push the branch, open the PR, and **merge it
yourself** once CI is green — marking it ready for review first if it was opened as a draft.
`AGENTS.md` §3 already authorises that merge and this is the one change with nothing to review,
so stopping here hands the user a blocker they cannot act on any better than you can. Only if
the merge is actually refused does it become theirs: say so in the report — plainly, not as a
footnote — that **onboarding is not complete until that PR is merged**, and why you could not.

**Then confirm it landed.** Re-read the default branch and check `START_HERE.md` is actually gone
from it. A local commit is not evidence; never report success on one.

If the push is **refused** — auth, permissions, an app not installed — don't retry blindly and
don't quietly settle for a local commit. Stop and report, under **Needs you**:

- the refusal message, verbatim;
- that the repo is **unchanged**, so `REPO_URL` still points at the template;
- that the notebook must not be run until this is fixed — it would clone and run the template's
  code, and look perfectly healthy doing it;
- that this container is ephemeral, so the commit dies with the session.

Report in the normal format (`AGENTS.md` §9). Under **Verify**: open the notebook badge and run
top to bottom, confirming the setup cell prints their repo and their Drive folder, and prints no
onboarding warning.

From the next session on, `AGENTS.md` §2 *Every session* is the loop. This file is gone and
never read again.
