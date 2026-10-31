# Troubleshooting

Start with the lab's own view: open `GET /lab/plugins` in the studio. A plugin
that does not read whole is named under `errors` there, and the other plugins
still load.

## The step does not appear

* Is the folder directly under `user/plugins/` (or a link to one)? The lab reads
  `user/plugins/*/plugin.json`.
* Reload the page after adding or changing a plugin.
* Check `GET /lab/plugins` for this plugin's entry under `errors`.
* The step's `script` must exist inside the plugin folder; a step whose script is
  missing or outside it is left out.

## The step fails immediately

The lab shows the **last line of standard error**. Common messages:

| Message | Cause | Fix |
| --- | --- | --- |
| `ManifestError: no manifest.json in …` | The step ran on a single file or an empty folder | Run it on a **stem set**; split the take into stems first |
| `ManifestError: manifest.json lists no stems` | The manifest is empty or has an unexpected shape | See [the manifest assumption](PLUGIN_CONTRACT.md#3-input-the-stem-manifest) |
| `ManifestError: stem entry needs a name and a file` | An entry is missing `name` or `file` | Inspect the take's `manifest.json` |
| `ManifestError: stem file leaves its folder` | A stem path escapes the stem folder | Refused on purpose; fix the manifest |
| `ModuleNotFoundError: No module named 'basic_pitch'` | The plugin's venv is missing or not populated | `python -m venv .venv && .venv/bin/pip install -r requirements.txt` in the plugin folder |
| `every stem failed; first: …` | Basic Pitch raised for each stem | See the error text in the message and in `report.csv` |

## `.venv/bin/python` not found

`plugin.json` points at `.venv/bin/python`, relative to the plugin folder. Create
the venv **inside the plugin folder**, or edit `"python"` in `plugin.json` to point
at another interpreter that has `basic-pitch` installed. Ruach itself runs on
Linux (Windows via WSL2), so the Linux layout `bin/python` is right.

## Installing Basic Pitch fails

Basic Pitch depends on TensorFlow (or, in newer releases, other runtimes). Match
the Python version to what its current release supports; if installation fails on
a very new Python, create the venv with an older one. Because the plugin has its
own venv, this never affects the studio's environment.

## It is slow

* The **first stem** is slow because the model loads. The plugin loads it once and
  reuses it for the other stems in the same run, but every run is a fresh process,
  so each run pays the load once.
* Cost grows with audio length. Long stems take longer.

## A stem has no MIDI file

Its `status` in `report.csv` is `silent` (no notes cleared the thresholds) or
`error` (see `detail`). For `silent`:

* Lower **Onset threshold** and **Frame threshold** to accept quieter or softer
  notes.
* Lower **Shortest note** if the part is fast.
* Drum and heavily noisy stems often produce no sensible pitched notes; that is a
  normal result, not a bug.

## The MIDI has too many (or too few) notes

* Too many, with chatter or ghost notes: raise **Onset threshold** and/or
  **Frame threshold**, or raise **Shortest note**.
* Too few, with notes cut short or missing: lower them.

Basic Pitch works best on **one instrument at a time**, which is why this plugin
works on stems. Transcribing a full mix will be much noisier.

## MIDI branches do not play

Ruach's plugin documentation describes audio versions and text/JSON/CSV reports;
it does not mention `.mid` files, so the lab may show a MIDI branch that cannot be
played or compared. The files are still written to the take's tree and can be
opened in a DAW or the studio's piano roll. If you want something audible in the
tree, a sonified WAV per stem is a natural addition; see
[Extension points](ARCHITECTURE.md#extension-points).

## Where do I find the output files?

They land in the take's tree as a branch of kind `plugin`, with the step's name,
its fields and its measure **(per Ruach's docs)**. `report.csv` has a Read button.
