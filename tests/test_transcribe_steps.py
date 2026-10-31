"""Step definitions for features/transcribe.feature (pytest-bdd)."""
import csv
import json

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ruach_basic_pitch.cli import main

scenarios("features/transcribe.feature")


@pytest.fixture
def audio_dir(tmp_path):
    folder = tmp_path / "stems"
    folder.mkdir()
    return folder


@pytest.fixture
def out_dir(tmp_path):
    return tmp_path / "out"


@pytest.fixture
def params_file(tmp_path):
    path = tmp_path / "params.json"
    path.write_text(json.dumps({"onset": 0.5, "bends": True}))
    return path


@pytest.fixture
def run_result():
    return {}


def _write_manifest(audio_dir, entries):
    (audio_dir / "manifest.json").write_text(json.dumps({"stems": entries}))


@given(parsers.parse('a stem set containing "{first}" and "{second}"'))
def stem_set(audio_dir, first, second):
    entries = []
    for name in (first, second):
        (audio_dir / f"{name}.wav").write_bytes(b"RIFF")
        entries.append({"name": name, "title": name.title(), "file": f"{name}.wav"})
    _write_manifest(audio_dir, entries)


@given("an audio folder without a manifest")
def no_manifest(audio_dir):
    pass


@given("a stem set whose manifest points outside its folder")
def escaping_manifest(audio_dir):
    _write_manifest(audio_dir, [{"name": "evil", "file": "../evil.wav"}])


@given(parsers.parse('the transcriber finds {count:d} notes in "{name}"'))
def finds_notes(transcriber, count, name):
    transcriber.notes[name] = count


@given(parsers.parse('the transcriber fails on "{name}"'))
def fails_on(transcriber, name):
    transcriber.failing.add(name)


@when("the step runs")
def run_step(audio_dir, out_dir, params_file, transcriber, run_result, capsys):
    run_result["code"] = main([str(audio_dir), str(out_dir), str(params_file)], transcribe=transcriber)
    captured = capsys.readouterr()
    run_result["stdout"], run_result["stderr"] = captured.out, captured.err


@then(parsers.parse('the file "{filename}" is written'))
def file_written(out_dir, filename):
    assert (out_dir / filename).is_file()


@then(parsers.parse('no file "{filename}" is written'))
def file_not_written(out_dir, filename):
    assert not (out_dir / filename).exists()


@then(parsers.parse('the report row for "{name}" says "{status}" with {count:d} notes'))
def report_row(out_dir, name, status, count):
    with (out_dir / "report.csv").open(newline="") as handle:
        rows = {row["stem"]: row for row in csv.DictReader(handle)}
    assert rows[name]["status"] == status
    assert int(rows[name]["notes"]) == count


@then(parsers.parse('the last line of output lists "{first}" and "{second}"'))
def last_line_lists(run_result, first, second):
    payload = json.loads(run_result["stdout"].strip().splitlines()[-1])
    listed = {entry["file"] for entry in payload["files"]}
    assert {first, second} <= listed


@then(parsers.parse("the step exits with code {code:d}"))
def exit_code(run_result, code):
    assert run_result["code"] == code


@then(parsers.parse('the error output mentions "{text}"'))
def error_mentions(run_result, text):
    assert text in run_result["stderr"]
