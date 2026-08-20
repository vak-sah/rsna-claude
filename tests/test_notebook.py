"""Guards the notebook's structure, and the two `AGENTS.md` §5 rules that are otherwise prose.

The notebook is the one file nobody can execute in CI — no Colab runtime, no Drive, no GPU — so
it is also the easiest place for a break to reach the default branch unnoticed. These checks
cover what *can* be established without running it: that it is well-formed, that every cell is
valid Python, and that the two structural rules hold.

Deliberately not checked: anything about behaviour. Running the notebook is the user's job
(`AGENTS.md` §8), and no test here should imply otherwise.

Uses only json and ast so CI needs no dependency beyond pytest.
"""

import ast
import json
import re
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "command_center.ipynb"


def cells(kind=None):
    nb = json.loads(NOTEBOOK.read_text())
    return [c for c in nb["cells"] if kind is None or c["cell_type"] == kind]


def source(cell):
    src = cell["source"]
    return src if isinstance(src, str) else "".join(src)


def test_notebook_is_well_formed():
    """Valid JSON, nbformat 4, and every cell has the fields a reader expects."""
    nb = json.loads(NOTEBOOK.read_text())
    assert nb["nbformat"] == 4
    assert nb["cells"], "notebook has no cells"
    for i, cell in enumerate(nb["cells"]):
        assert cell["cell_type"] in {"code", "markdown"}, f"cell {i}: odd cell_type"
        assert "source" in cell, f"cell {i}: no source"
        if cell["cell_type"] == "code":
            assert cell.get("outputs") == [], f"cell {i}: committed output — CI should strip it"


def test_every_code_cell_parses():
    """A typo in the notebook must fail here, not in the user's Colab runtime."""
    for i, cell in enumerate(cells("code")):
        text = source(cell)
        # IPython magics and shell escapes are not Python; blank them for the syntax check
        cleaned = "\n".join(
            "" if line.lstrip().startswith(("!", "%")) else line for line in text.split("\n")
        )
        try:
            ast.parse(cleaned)
        except SyntaxError as exc:
            raise AssertionError(f"cell {i} does not parse: line {exc.lineno}: {exc.msg}") from None


def test_every_knob_lives_in_one_cell():
    """`AGENTS.md` §5: every knob lives in the config cell — so exactly one cell declares them.

    This rule has been broken before, silently: REPO_URL and PACKAGES were declared in the setup
    cell, which meant two places to look for the values that change how a run behaves.

    Scope: this matches ALL-CAPS declarations, which is the convention rather than the
    definition — `AGENTS.md` §5 is. Tightening the pattern further would fire on every ordinary
    local in every cell.
    """
    declaring = {
        i: names
        for i, cell in enumerate(cells("code"))
        if (names := re.findall(r"^([A-Z][A-Z_0-9]*)\s*[:=]", source(cell), re.M))
    }
    assert len(declaring) == 1, (
        "knobs must be declared in exactly one cell (the config cell), but top-level constants "
        f"appear in {len(declaring)}: { {i: n for i, n in declaring.items()} }"
    )


def test_working_cells_say_what_they_do():
    """`AGENTS.md` §6: a cell that does more than one thing carries a docstring, from the start.

    Docstrings decay late rather than early — the first features get them and the tenth does
    not, by which point the notebook is the only place the work is described. The threshold is
    the cell's own structure, not a line count: a single-statement cell is self-evident, and
    anything sequencing two or more statements is doing something a reader has to reconstruct.
    """
    for i, cell in enumerate(cells("code")):
        cleaned = "\n".join(
            "" if line.lstrip().startswith(("!", "%")) else line
            for line in source(cell).split("\n")
        )
        body = ast.parse(cleaned).body
        if len(body) < 2:
            continue
        assert ast.get_docstring(ast.Module(body=body, type_ignores=[])), (
            f"cell {i} runs {len(body)} statements with no opening docstring — say what it does "
            "and what the user should see"
        )


def test_no_tests_in_notebook_cells():
    """`AGENTS.md` §5: tests live in `tests/`, never in a cell, so output stays readable."""
    for i, cell in enumerate(cells("code")):
        text = source(cell)
        assert not re.search(r"^\s*def test_", text, re.M), f"cell {i} defines a test"
        assert not re.search(r"^\s*import (pytest|unittest)", text, re.M), (
            f"cell {i} imports a test framework"
        )
