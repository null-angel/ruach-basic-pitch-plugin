"""Reading the stem set the Ruach lab hands a ``"input": "stems"`` step.

The lab passes a folder containing ``manifest.json``; each stem has a ``name``,
a ``title`` and a ``file``. See Ruach Studio's docs/PLUGINS.md.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class ManifestError(Exception):
    """The stem set is missing, unreadable or points outside its folder."""


@dataclass(frozen=True)
class Stem:
    name: str
    title: str
    path: Path


def load_stems(audio_dir: Path) -> list[Stem]:
    """Return the stems listed in ``audio_dir/manifest.json``.

    Accepts either ``{"stems": [...]}`` or a bare list, since the studio's docs
    only promise that the manifest "lists the stems".
    """
    manifest_path = audio_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ManifestError(f"no manifest.json in {audio_dir}")
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest.json is not valid JSON: {exc}") from exc

    entries = raw.get("stems") if isinstance(raw, dict) else raw
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest.json lists no stems")

    root = audio_dir.resolve()
    return [_to_stem(entry, root) for entry in entries]


def _to_stem(entry: object, root: Path) -> Stem:
    if not isinstance(entry, dict) or "name" not in entry or "file" not in entry:
        raise ManifestError(f"stem entry needs a name and a file: {entry!r}")
    path = (root / str(entry["file"])).resolve()
    if root not in path.parents:
        raise ManifestError(f"stem file leaves its folder: {entry['file']}")
    name = str(entry["name"])
    return Stem(name=name, title=str(entry.get("title") or name), path=path)
