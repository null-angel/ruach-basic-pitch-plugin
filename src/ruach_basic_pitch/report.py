"""The step's outcome types and the report the lab shows beside the branch."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Literal

Status = Literal["ok", "silent", "error"]


@dataclass(frozen=True)
class StemOutcome:
    name: str
    title: str
    status: Status
    notes: int = 0
    midi_file: str | None = None
    detail: str = ""


def render_report_csv(outcomes: list[StemOutcome]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["stem", "status", "notes", "detail"])
    for o in outcomes:
        writer.writerow([o.name, o.status, o.notes, " ".join(o.detail.split())])
    return buffer.getvalue()


def summarize(outcomes: list[StemOutcome]) -> str:
    """One line, 300 characters at most (the lab's limit for ``summary``)."""
    done = [o for o in outcomes if o.status == "ok"]
    failed = [o for o in outcomes if o.status == "error"]
    text = f"{len(done)} of {len(outcomes)} stems transcribed, {sum(o.notes for o in done)} notes"
    if failed:
        text += f", {len(failed)} failed"
    return text[:300]
