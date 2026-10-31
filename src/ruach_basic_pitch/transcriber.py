"""The seam between the plugin and Basic Pitch.

``Transcriber`` is a Protocol, so the runner depends on the abstraction and
tests can pass a fake. ``basic_pitch_transcriber`` is the real one; it imports
Basic Pitch lazily so that importing this package stays cheap.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .params import Params


class MidiLike(Protocol):
    def write(self, filename: str) -> None: ...


@dataclass(frozen=True)
class Transcription:
    midi: MidiLike
    note_count: int


class Transcriber(Protocol):
    def __call__(self, audio_path: Path, params: Params) -> Transcription: ...


def basic_pitch_transcriber(audio_path: Path, params: Params) -> Transcription:
    from basic_pitch.inference import predict

    _, midi, note_events = predict(
        str(audio_path),
        onset_threshold=params.onset,
        frame_threshold=params.frame,
        minimum_note_length=params.min_note_ms,
        multiple_pitch_bends=params.bends,
    )
    return Transcription(midi=midi, note_count=len(note_events))
