"""Running the step: stems in, MIDI files and a report out.

Pure with respect to the transcriber (injected) and the clock (injected), so
the whole flow is testable without Basic Pitch or TensorFlow.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .manifest import Stem
from .params import Params
from .report import StemOutcome, render_report_csv, summarize
from .transcriber import Transcriber

REPORT_FILE = "report.csv"


@dataclass(frozen=True)
class StepResult:
    outcomes: list[StemOutcome]
    took: float

    @property
    def succeeded(self) -> bool:
        """True unless every stem failed."""
        return any(o.status != "error" for o in self.outcomes)

    def to_payload(self) -> dict:
        """The one JSON line the lab reads from the step's last line of output."""
        files = [
            {"name": f"{o.title} (MIDI)", "file": o.midi_file}
            for o in self.outcomes
            if o.midi_file
        ]
        files.append({"name": "note counts", "file": REPORT_FILE})
        return {"files": files, "summary": summarize(self.outcomes), "took": self.took}


def transcribe_stem(
    stem: Stem, out_dir: Path, params: Params, transcribe: Transcriber
) -> StemOutcome:
    """Transcribe one stem. A failure becomes an outcome, not an exception,
    so one bad stem does not lose the others."""
    try:
        result = transcribe(stem.path, params)
    except Exception as exc:  # noqa: BLE001 - isolate per-stem failures
        return StemOutcome(stem.name, stem.title, "error", detail=f"{type(exc).__name__}: {exc}")

    if result.note_count == 0:
        return StemOutcome(stem.name, stem.title, "silent")

    filename = f"{Path(stem.name).name}.mid"
    result.midi.write(str(out_dir / filename))
    return StemOutcome(stem.name, stem.title, "ok", notes=result.note_count, midi_file=filename)


def run_step(
    stems: list[Stem],
    out_dir: Path,
    params: Params,
    transcribe: Transcriber,
    clock: Callable[[], float] = time.monotonic,
) -> StepResult:
    started = clock()
    out_dir.mkdir(parents=True, exist_ok=True)
    outcomes = [transcribe_stem(stem, out_dir, params, transcribe) for stem in stems]
    (out_dir / REPORT_FILE).write_text(render_report_csv(outcomes), encoding="utf-8")
    return StepResult(outcomes=outcomes, took=round(clock() - started, 1))
