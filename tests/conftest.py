"""Shared fixtures: a fake transcriber so tests never load Basic Pitch."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ruach_basic_pitch.params import Params  # noqa: E402
from ruach_basic_pitch.transcriber import Transcription  # noqa: E402


class FakeMidi:
    def write(self, filename: str) -> None:
        Path(filename).write_bytes(b"MThd")


class FakeTranscriber:
    """Looks up behaviour by the stem's file name (``<name>.wav``)."""

    def __init__(self) -> None:
        self.notes: dict[str, int] = {}
        self.failing: set[str] = set()

    def __call__(self, audio_path: Path, params: Params) -> Transcription:
        name = audio_path.stem
        if name in self.failing:
            raise RuntimeError(f"cannot hear {name}")
        return Transcription(midi=FakeMidi(), note_count=self.notes.get(name, 0))


@pytest.fixture
def transcriber() -> FakeTranscriber:
    return FakeTranscriber()
