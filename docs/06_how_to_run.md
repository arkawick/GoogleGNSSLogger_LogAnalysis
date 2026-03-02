# How to Run the GNSS Quality Analysis

Complete step-by-step guide — from recording a log on a phone to viewing the
full quality report.

---

## Overview

```
Phone (GnssLogger)  →  3 log files  →  LogN/ folder  →  run_analysis.py  →  LogN/outputs/
```

The entire analysis for one log runs in a single command:
```
python scripts/run_analysis.py LogN
```

---

## Step 1 — Record a Log on the Phone

1. Install **GnssLogger** (v3.1.1.2 or later) from the Google Play Store.
2. Open the app and tap **Start Logging**.
3. Stand outdoors with a clear view of the sky for at least 60–120 seconds.
4. Tap **Stop Logging**.
5. The app saves three files to `Android/data/com.google.android.apps.location.gps.gnsslogger/files/`:
   ```
   gnss_log_YYYY_MM_DD_HH_MM_SS.txt    ← raw GNSS + IMU measurements (CSV)
   gnss_log_YYYY_MM_DD_HH_MM_SS.nmea   ← NMEA 0183 sentences
   gnss_log_YYYY_MM_DD_HH_MM_SS.26o    ← RINEX 4.01 observation file
   ```

Transfer these three files to your computer (USB, Google Drive, etc.).

---

## Step 2 — Create a Log Folder

In the project root, create a new numbered folder and place the three files
inside it:

```
GoogleGNSSLogger_LogAnalysis/
├── Log4/                         ← new folder
│   ├── gnss_log_2026_03_10_...txt
│   ├── gnss_log_2026_03_10_...nmea
│   └── gnss_log_2026_03_10_...26o
```

The folder name can be anything (`Log4`, `Pixel9_outdoor`, etc.), but using
`LogN` keeps it consistent with the existing structure.

---

## Step 3 — One-Time Setup (first time only)

Make sure Python 3.10+ and Jupyter are installed, then install the required
packages:

```bash
pip install -r requirements.txt
pip install jupyter nbconvert
```

Verify Jupyter is available:
```bash
jupyter --version
```

---

## Step 4 — Run the Analysis

From the **project root** directory:

```bash
python scripts/run_analysis.py Log4
```

### What you will see

```
----------------------------------------------------
  Log dir    : Log4
  Log file   : gnss_log_2026_03_10_09_30_00.txt
  Device     : Google Pixel 9 (Android 16)
  Chipset    : MPSS.DE.9.0
  Bias thresh: 40.0 ns
----------------------------------------------------

Executing notebook...  (this may take ~30 s)

Done.
Executed notebook -> Log4\outputs\gnss_quality_analysis_v2_Log4.ipynb
```

### What the script does automatically

| Step | What happens |
|------|-------------|
| Header parse | Reads `Manufacturer`, `Model`, `Platform`, `GNSS Hardware Model Name` from the `.txt` file's first comment line |
| Device label | Builds `"<Manufacturer> <Model> (Android <version>)"` from parsed fields |
| Threshold choice | `MPSS.HI` chipsets → 200 ns (reports 75–129 ns); all others → 40 ns |
| Notebook clone | Copies `scripts/gnss_quality_analysis_v2.ipynb` to a temp file |
| Config patch | Replaces `LOG_DIR`, `DEVICE_NAME`, `BIAS_UNC_THRESH` in the temp copy |
| Execution | Runs all cells via `jupyter nbconvert --execute` |
| Save | Moves the executed notebook to `Log4/outputs/gnss_quality_analysis_v2_Log4.ipynb` |
| Cleanup | Deletes the temp copy |

The **master notebook** (`scripts/gnss_quality_analysis_v2.ipynb`) is **never
modified**.

---

## Step 5 — View the Results

Open the executed notebook:

```bash
jupyter notebook Log4/outputs/gnss_quality_analysis_v2_Log4.ipynb
```

Or open it directly in **VS Code** (with the Jupyter extension).

The notebook contains all plots inline — no separate PNG files to manage.

### What the notebook produces

| Output | Location | Description |
|--------|----------|-------------|
| Executed notebook | `Log4/outputs/gnss_quality_analysis_v2_Log4.ipynb` | All plots embedded |
| CN0 over time | inline | Carrier-to-noise density per constellation |
| Sky plot | inline | Polar satellite sky view coloured by CN0 |
| Satellite counts | inline | Tracked vs used per constellation |
| Fix scatter | inline | Position fixes coloured by provider |
| Quality scorecard | inline | PASS / FAIL / N/A table for all 41 checks |
| Quality radar | inline | Inverted radar chart (centre = PASS) |
| Summary bar chart | inline | Per-section pass rate |
| All PNGs | `Log4/outputs/` | Saved as `.png` files alongside the notebook |

---

## Optional — Override Auto-detection

If the auto-detected device label is wrong, or you want to force a different
threshold:

```bash
# Override device label
python scripts/run_analysis.py Log4 --device "Pixel 9 Pro (Tensor G4)"

# Override BiasUncertaintyNanos threshold
python scripts/run_analysis.py Log4 --threshold 200

# Both at once
python scripts/run_analysis.py Log4 --device "Custom Label" --threshold 100
```

---

## Optional — Generate the Standalone Radar Chart

The standalone radar script (`scripts/gnss_radar.py`) produces a high-resolution
radar PNG independent of Jupyter. It requires manual update because it needs the
PASS/FAIL results from the notebook.

1. Open `scripts/gnss_radar.py` in any text editor.
2. Edit the four lines at the top of the file:

```python
LOG_DIR_NAME = "Log4"
DEVICE       = "Google Pixel 9 (Android 16)"
SCORE        = "23 / 28 applicable  (82 %)"    # from the notebook scorecard
```

3. Update the `CHECKS` list — set each entry to `"PASS"`, `"FAIL"`, or `"NA"`
   based on the results in the executed notebook.

4. Run from the project root:
```bash
python scripts/gnss_radar.py
```

Output: `Log4/outputs/gnss_radar_inverted.png`

---

## Optional — Change a Quality Threshold

All 41 thresholds are stored in `parameters/thresholds.json`. Open the file and
change the `"threshold"` value for any check:

```json
"cn0_top4": {
    "name":      "Avg CN0 Top 4 Per Epoch",
    "threshold": 40.0,        ← change this number
    "operator":  ">=",
    "unit":      "dBHz"
}
```

Then rerun the analysis — the notebook loads thresholds from this file at
runtime, so no notebook editing is needed:

```bash
python scripts/run_analysis.py Log4
```

---

## Troubleshooting

### `ERROR: no gnss_log_*.txt found`
The `.txt` file is not in the log folder. Check the folder name and that the
file was transferred correctly.

### `ERROR: could not find the config cell`
The master notebook's config cell no longer contains `LOG_DIR`, `DEVICE_NAME`,
and `BIAS_UNC_THRESH` on separate lines. Do not rename or delete those
variables.

### `NOTEBOOK EXECUTION FAILED`
The last 3 000 characters of the error are printed. Common causes:
- Missing dependency → run `pip install -r requirements.txt`
- Corrupt or empty log file → verify the `.txt` file has `Raw,` data rows
- Path issue → run from the **project root**, not from inside `scripts/`

### All measurements filtered out (0 raw rows)
The `BIAS_UNC_THRESH` is too strict. If the device is an `MPSS.HI` chipset
(BiasUncNanos 75–129 ns) the threshold should be 200 ns. The script sets this
automatically, but you can also force it:
```bash
python scripts/run_analysis.py Log4 --threshold 200
```

### `jupyter: command not found`
Jupyter is not installed or not in PATH:
```bash
pip install jupyter nbconvert
```

---

## Quick Reference

```bash
# Analyse a new log
python scripts/run_analysis.py LogN

# With overrides
python scripts/run_analysis.py LogN --device "Label" --threshold 200

# Standalone radar (after manually updating CHECKS in the script)
python scripts/gnss_radar.py

# View results
jupyter notebook LogN/outputs/gnss_quality_analysis_v2_LogN.ipynb
```

---

## File Reference

| File | Purpose |
|------|---------|
| `scripts/run_analysis.py` | One-command runner — this is all you need |
| `scripts/gnss_quality_analysis_v2.ipynb` | Master notebook (do not edit config here) |
| `scripts/gnss_radar.py` | Standalone radar chart (edit manually) |
| `parameters/thresholds.json` | All 41 quality thresholds — edit to change pass/fail criteria |
| `LogN/outputs/gnss_quality_analysis_v2_LogN.ipynb` | Executed notebook with all results |
| `docs/00_overview.md` | Project structure and device comparison table |
| `docs/01_gnsslogger_txt.md` | GnssLogger `.txt` format reference |
| `docs/02_nmea.md` | NMEA 0183 format reference |
| `docs/03_rinex.md` | RINEX 4.01 format reference |
| `docs/LogN/04_data_summary.md` | Physical interpretation of LogN |
| `docs/LogN/05_gnss_quality_report.md` | Detailed quality report for LogN |
