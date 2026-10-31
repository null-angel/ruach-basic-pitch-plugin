"""The step's fields, as the lab writes them to ``PARAMS.json``."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Params:
    onset: float = 0.5
    frame: float = 0.3
    min_note_ms: float = 127.0
    bends: bool = True


def _clamp(value: object, low: float, high: float, default: float) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def parse_params(raw: dict) -> Params:
    """Build ``Params`` from the lab's dict, falling back to defaults.

    The lab already cleans values to each field's bounds; clamping again keeps
    the step safe when it is run by hand.
    """
    d = Params()
    return Params(
        onset=_clamp(raw.get("onset"), 0.1, 0.9, d.onset),
        frame=_clamp(raw.get("frame"), 0.1, 0.9, d.frame),
        min_note_ms=_clamp(raw.get("min_note_ms"), 20, 500, d.min_note_ms),
        bends=bool(raw.get("bends", d.bends)),
    )


def load_params(path: Path) -> Params:
    return parse_params(json.loads(path.read_text(encoding="utf-8")))
