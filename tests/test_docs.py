"""Guards against the docs drifting out of alignment with each other and with the repo.

Every failure here is a real inconsistency an agent would trip over: a pointer to a file that
isn't there, a cross-reference to a section that doesn't exist, or a layout list that no longer
matches what's on disk. Those are cheap to introduce and annoying to find by reading.

This is deliberately small. It checks facts that are mechanically checkable and nothing about
wording or content — style is a judgement call and does not belong in CI.

To change what's enforced, edit the four tests below. To exempt a path from the layout check,
add it to IGNORED.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = sorted(REPO.glob("*.md"))

# START_HERE.md is referenced by AGENTS.md but deletes itself during onboarding, so a missing
# one is correct rather than broken. It is the only file allowed to be referenced and absent.
SELF_DELETING = {"START_HERE.md"}

# Not part of the layout listing: git internals, caches, and anything already gitignored.
IGNORED = {".git", ".github", ".gitignore", ".pytest_cache", "__pycache__", ".ipynb_checkpoints"}


def test_referenced_markdown_files_exist():
    """Any `SOMETHING.md` named in a doc must exist, or be the self-deleting one."""
    missing = []
    for doc in DOCS:
        for name in set(re.findall(r"\b([A-Z_]+\.md)\b", doc.read_text())):
            if name not in SELF_DELETING and not (REPO / name).exists():
                missing.append(f"{doc.name} points at {name}, which does not exist")
    assert not missing, "\n".join(missing)


def test_agents_section_references_resolve():
    """`AGENTS.md §N` must name a section that AGENTS.md actually has."""
    agents = (REPO / "AGENTS.md").read_text()
    existing = set(re.findall(r"^## (\d+)\.", agents, re.M))

    broken = []
    for doc in DOCS:
        text = doc.read_text()
        # "AGENTS.md §6" from other files; bare "§6" inside AGENTS.md itself
        refs = re.findall(r"AGENTS\.md`? §(\d+)", text)
        if doc.name == "AGENTS.md":
            refs += re.findall(r"§(\d+)", text)
        for n in set(refs):
            if n not in existing:
                broken.append(f"{doc.name} references AGENTS.md §{n}, which has no such section")
    assert not broken, "\n".join(broken)


def test_readme_layout_matches_the_repo():
    """The layout block lists what is actually here, in both directions."""
    readme = (REPO / "README.md").read_text()
    block = re.search(r"## Layout\n+```\n(.*?)```", readme, re.S)
    assert block, "README.md has no Layout code block"

    listed = {line.split()[0].rstrip("/") for line in block.group(1).splitlines() if line.strip()}
    actual = {p.name for p in REPO.iterdir() if p.name not in IGNORED}
    # entries may be nested paths (src/pipeline/); compare on their top-level component
    listed_top = {n.split("/")[0] for n in listed}

    listed_but_absent = {n for n in listed if not (REPO / n).exists() and n not in SELF_DELETING}
    present_but_unlisted = actual - listed_top - SELF_DELETING

    assert not listed_but_absent, f"README Layout lists what isn't here: {sorted(listed_but_absent)}"
    assert not present_but_unlisted, f"in the repo but missing from README Layout: {sorted(present_but_unlisted)}"


def test_pipeline_section_drops_the_stub_once_a_real_stage_exists():
    """§ Pipeline may describe the stub only while the stub is all there is.

    `AGENTS.md` §6 puts the README pipeline line in the extraction checklist, but that is
    judgement, and judgement is what slips on the tenth feature rather than the first. This is
    the mechanical half: the moment `src/pipeline/` holds a real module, the placeholder text is
    false by definition, so it cannot survive to the default branch.

    Only the README claim is asserted. Whether `stub.py` itself is deleted in the same PR or the
    next one is a judgement call, and a test that forced it would fire on a legitimate
    intermediate commit.
    """
    modules = {p.stem for p in (REPO / "src" / "pipeline").glob("*.py")} - {"__init__"}
    if modules <= {"stub"}:
        return

    readme = (REPO / "README.md").read_text()
    section = re.search(r"^## Pipeline$(.*)", readme, re.S | re.M)
    assert section, "README.md has no Pipeline section"
    assert "stub" not in section.group(1), (
        f"src/pipeline/ has real modules ({sorted(modules - {'stub'})}), but README's Pipeline "
        "section still describes the stub — replace it with one line per real stage"
    )
