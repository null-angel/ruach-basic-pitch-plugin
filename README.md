# ruach-basic-pitch

A [Ruach Studio](https://github.com/igrbible/Ruach_Studio) Refiner plugin that
transcribes the stems of a take to MIDI with Spotify's
[Basic Pitch](https://github.com/spotify/basic-pitch).

Ruach Studio gets its MIDI from the *score* YuE2 writes before it renders audio.
This plugin goes the other way: it reads the finished (or refined) audio and
recovers notes from it, one `.mid` per stem, so you can edit what the model
actually sang and played.

## What it does

Adds one step, **To MIDI**, after the Refiner's own steps:

1. Receives the take's stem set (the lab runs it with `"input": "stems"`).
2. Runs Basic Pitch on each stem. It works best on one instrument at a time,
   which is why it works on stems and not the full mix.
3. Writes `<stem>.mid` for every stem that contains notes.
4. Writes `report.csv` (`stem,status,notes,detail`) and a one-line summary.

A stem with no detected notes gets no MIDI file and shows as `silent` in the
report. A stem that fails shows as `error`; the other stems still finish. The
step only fails if every stem fails.

## Install

Requires the Linux/WSL2 setup Ruach Studio itself runs on, and Python 3.10+.

```bash
cd <ruach-studio>/user/plugins
git clone https://github.com/null-angel/ruach-basic-pitch-plugin ruach-basic-pitch   # or symlink a folder kept elsewhere
cd ruach-basic-pitch
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The plugin has its own venv (`"python": ".venv/bin/python"` in `plugin.json`),
so TensorFlow and Basic Pitch stay out of the studio's environment. Reload the
studio page; the lab reads `user/plugins/*/plugin.json` on request
(`GET /lab/plugins`). A plugin that does not parse shows up under `errors`
there while the others still load.

## Use

In the Refiner, split the take into stems first (the panel offers a split when
there is none), then run **To MIDI** on a stem set.

| Field | Default | Meaning |
| --- | --- | --- |
| Onset threshold | 0.5 | Higher means fewer, surer notes |
| Frame threshold | 0.3 | Higher means shorter, tidier notes |
| Shortest note, ms | 127 | Notes shorter than this are dropped |
| Pitch bends | on | Keep pitch-bend messages |

## Layout

```
plugin.json                    what the lab reads: id, step, fields
transcribe.py                  thin entry point: PYTHON transcribe.py AUDIO OUTDIR PARAMS.json
src/ruach_basic_pitch/
  manifest.py                  read the stem set's manifest.json
  params.py                    parse and clamp the step's fields
  transcriber.py               Transcriber protocol + the real Basic Pitch adapter
  runner.py                    run every stem, collect outcomes (pure; injectable)
  report.py                    outcome type, report.csv, summary line
  cli.py                       the lab's command-line contract
tests/                         pytest-bdd scenarios + unit tests
```

Design notes: the runner depends on a `Transcriber` protocol rather than on
Basic Pitch, so tests inject a fake and never load TensorFlow (dependency
inversion). The runner and helpers are pure functions over small frozen
dataclasses, and the only I/O is at the edges (`manifest.py`, `runner.py`
writing outputs, `cli.py`).

## Develop

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

Behaviour is specified in `tests/features/transcribe.feature` (Gherkin, run by
pytest-bdd). Add a scenario first, then the step, then the code.

## Things to know

- **Stem manifest shape.** Ruach's docs say `manifest.json` "lists the stems,
  each with `name`, `title` and `file`". `manifest.py` accepts either
  `{"stems": [...]}` or a bare list. If a real take's manifest differs,
  `load_stems` is the one place to change.
- **`.mid` in the take tree.** The plugin docs define audio versions and
  text/JSON/CSV reports, but not MIDI. The lab may show a `.mid` branch that
  does not play. If that bothers you, add a sonified WAV per stem (Basic Pitch
  can render one) and list it first in `files`.
- **Non-stem input.** The step is declared `"input": "stems"`, so it does not
  run on a single file.
- **Licence.** Basic Pitch is Apache-2.0. This plugin runs in a separate process
  and venv from Ruach Studio (AGPL-3.0); choose the licence for this repo as
  you like.

## Contract with the lab

The lab runs `PYTHON transcribe.py AUDIO OUTDIR PARAMS.json` in the plugin
folder. `AUDIO` is the stem set's folder. The last line of stdout is JSON:

```json
{"files": [{"name": "Vocals (MIDI)", "file": "vocals.mid"},
           {"name": "note counts", "file": "report.csv"}],
 "summary": "2 of 2 stems transcribed, 412 notes", "took": 18.3}
```

Full reference: Ruach Studio's `docs/PLUGINS.md`.
