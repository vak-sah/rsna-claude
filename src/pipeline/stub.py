"""End-to-end stub: the smallest pipeline that proves the wiring works.

Reads records from a text file, passes them through untouched, writes them out again. The
absence of a real transformation is the point — this exists so a clone can confirm the whole
path (notebook -> `src/` -> `tests/` -> CI) is connected before any real feature is built, and
so the first real feature has something to replace instead of a blank page.

Inputs / outputs:
    load(path)            -> list[str]   non-blank lines, stripped
    transform(records)    -> list[str]   identity, for now
    save(records, path)   -> None        one record per line, creates parent dirs
    run(in_path, out_path)-> int         load -> transform -> save, returns records written

Every path is passed in explicitly. Nothing here knows about Drive or the network, so the
tests need neither.

To make this a real stage: replace `transform`. `load` and `save` stay as they are for as long
as the data is line-oriented — when it stops being, they are the two functions to change, and
`run` should not need touching. Delete this module once a real first stage exists; it has no
other callers than the notebook's pipeline cell.
"""

from pathlib import Path


def load(path: str | Path) -> list[str]:
    """Read `path` and return its non-blank lines, each stripped of surrounding whitespace."""
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]


def transform(records: list[str]) -> list[str]:
    """Return `records` unchanged. This is the seam a real first stage replaces."""
    return list(records)


def save(records: list[str], path: str | Path) -> None:
    """Write one record per line to `path`, creating parent directories if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{record}\n" for record in records))


def run(in_path: str | Path, out_path: str | Path) -> int:
    """Load, transform, save. Returns how many records were written."""
    records = transform(load(in_path))
    save(records, out_path)
    return len(records)
