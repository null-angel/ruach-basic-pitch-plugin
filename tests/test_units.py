"""Unit tests for the pure helpers (params parsing, report rendering)."""
from ruach_basic_pitch.params import Params, parse_params
from ruach_basic_pitch.report import StemOutcome, render_report_csv, summarize


def test_params_default_when_empty():
    assert parse_params({}) == Params()


def test_params_are_clamped_to_the_field_bounds():
    p = parse_params({"onset": 5, "frame": -1, "min_note_ms": 9999})
    assert (p.onset, p.frame, p.min_note_ms) == (0.9, 0.1, 500)


def test_params_ignore_garbage_values():
    assert parse_params({"onset": "loud"}).onset == Params().onset


def test_report_flattens_multiline_error_detail():
    outcome = StemOutcome("bass", "Bass", "error", detail="boom\nsecond line")
    assert "boom second line" in render_report_csv([outcome])


def test_summary_counts_notes_and_failures():
    outcomes = [
        StemOutcome("a", "A", "ok", notes=3, midi_file="a.mid"),
        StemOutcome("b", "B", "error", detail="x"),
    ]
    assert summarize(outcomes) == "1 of 2 stems transcribed, 3 notes, 1 failed"
