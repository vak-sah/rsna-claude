"""Tests for the end-to-end stub.

These run without Drive, network or a GPU — every path comes from pytest's `tmp_path`, which
is what `AGENTS.md` §7 requires of anything in `tests/`. If a future test can't be written this
way, the module under test is mixing I/O with logic and the seam needs fixing, not the test.
"""

from pipeline import stub


def test_run_round_trips_records(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("alpha\nbeta\ngamma\n")
    dst = tmp_path / "out.txt"

    written = stub.run(src, dst)

    assert written == 3
    assert dst.read_text() == "alpha\nbeta\ngamma\n"


def test_load_drops_blank_lines_and_strips_whitespace(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("  alpha  \n\n\t\nbeta\n   \n")

    assert stub.load(src) == ["alpha", "beta"]


def test_transform_is_identity_but_does_not_alias_its_input():
    records = ["alpha", "beta"]

    result = stub.transform(records)

    assert result == records
    result.append("gamma")
    assert records == ["alpha", "beta"]


def test_save_creates_missing_parent_directories(tmp_path):
    dst = tmp_path / "nested" / "deeper" / "out.txt"

    stub.save(["alpha"], dst)

    assert dst.read_text() == "alpha\n"


def test_run_on_empty_input_writes_an_empty_file(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("\n  \n")
    dst = tmp_path / "out.txt"

    assert stub.run(src, dst) == 0
    assert dst.read_text() == ""
