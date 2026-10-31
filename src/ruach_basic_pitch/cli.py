"""Command line contract with the Ruach lab: ``AUDIO OUTDIR PARAMS.json``.

Prints the result as one JSON line (last line of stdout). On failure it writes
the reason to stderr and exits 1; the lab shows stderr's last line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .manifest import ManifestError, load_stems
from .params import load_params
from .runner import run_step
from .transcriber import Transcriber, basic_pitch_transcriber


def main(argv: list[str], transcribe: Transcriber = basic_pitch_transcriber) -> int:
    if len(argv) != 3:
        print("usage: transcribe.py AUDIO OUTDIR PARAMS.json", file=sys.stderr)
        return 2
    audio_dir, out_dir, params_path = Path(argv[0]), Path(argv[1]), Path(argv[2])

    try:
        stems = load_stems(audio_dir)
        params = load_params(params_path)
    except (ManifestError, OSError, json.JSONDecodeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    result = run_step(stems, out_dir, params, transcribe)
    if not result.succeeded:
        first = next(o for o in result.outcomes if o.status == "error")
        print(f"every stem failed; first: {first.name}: {first.detail}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_payload()))
    return 0
