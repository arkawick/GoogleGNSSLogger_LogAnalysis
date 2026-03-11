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

By default this runs **both** notebooks. To run only one:

```bash
python scripts/run_analysis.py Log4 --notebook v2    # v2 41-check only
python scripts/run_analysis.py Log4 --notebook ref   # Google reference only
python scripts/run_analysis.py Log4 --notebook both  # both (default)
```

### What you will see

```
----------------------------------------------------
  Log dir    : Log4
  Log file   : gnss_log_2026_03_10_17_19_07.txt
  Device     : Sony SO-51G (Android 16)
  Chipset    : MPSS.DE.9.0
  Bias thresh: 40.0 ns
  Notebooks  : both
----------------------------------------------------

Executing [v2 (41-check)] notebook...  (this may take ~60 s)
  -> Log4\outputs\gnss_quality_analysis_v2_Log4.ipynb
Executing [ref (Google original)] notebook...  (this may take ~60 s)
  -> Log4\outputs\gnss_quality_analysis_ref_Log4.ipynb

Done. All notebooks saved to Log4/outputs/
```

### What the script does automatically

| Step | What happens |
|------|-------------|
| Header parse | Reads `Manufacturer`, `Model`, `Platform`, `GNSS Hardware Model Name` from the `.txt` file's first comment line |
| Device label | Builds `"<Manufacturer> <Model> (Android <version>)"` from parsed fields |
| Threshold choice | `MPSS.HI` chipsets → 200 ns (reports 75–129 ns); all others → 40 ns |
| Notebook clone | Copies the master notebook to a temp file (master is never modified) |
| Config patch | Replaces `LOG_DIR`, `DEVICE_NAME`, `BIAS_UNC_THRESH` in the temp copy |
| Execution | Runs all cells via `jupyter nbconvert --execute` |
| Save | Moves the executed notebook to `Log4/outputs/` |
| Cleanup | Deletes the temp copy |

The ref notebook uses `--allow-errors` so it always saves even if some cells fail due to data quality issues (errors are shown inline in the notebook).

The **master notebooks** (`scripts/gnss_quality_analysis_v2.ipynb` and `scripts/gnss_analysis_ref.ipynb`) are **never modified**.

---

## Step 5 — View the Results

Open the executed notebook:

```bash
jupyter notebook Log4/outputs/gnss_quality_analysis_v2_Log4.ipynb
```

Or open it directly in **VS Code** (with the Jupyter extension).

The notebook contains all plots inline — no separate PNG files to manage.

### What the notebooks produce

**v2 notebook** (`gnss_quality_analysis_v2_Log4.ipynb`):

| Output | Description |
|--------|-------------|
| CN0 over time | Carrier-to-noise density per constellation |
| Sky plot | Polar satellite sky view coloured by CN0 |
| Satellite counts | Tracked vs used per constellation |
| Fix scatter | Position fixes coloured by provider |
| Quality scorecard | PASS / FAIL / N/A table for all 41 checks |
| Quality radar | Inverted radar chart (centre = PASS) |
| Summary bar chart | Per-section pass rate |
| PNGs | Saved to `Log4/outputs/` alongside the notebook |

**ref notebook** (`gnss_quality_analysis_ref_Log4.ipynb`):

| Output | Description |
|--------|-------------|
| Conformance scorecard | 32-check Google framework results |
| Spider plot | Radar chart of all conformance metrics |
| C/N0 analysis | Per-epoch and per-satellite CN0 plots |
| Clock bias | Delta clock bias over time |
| PR / ADR / PRR residuals | Pseudorange, phase, and Doppler residual plots |
| Time-sync analysis | GPS time vs ElapsedRealtime offset |

> If the ref notebook encounters a data quality issue (duty cycling, poor WLS convergence), the error is shown inline and the notebook is still saved with all successfully-executed cells.

---

## Optional — Override Auto-detection

If the auto-detected device label is wrong, or you want to force a different
threshold:

```bash
# Override device label
python scripts/run_analysis.py Log4 --device "Pixel 9 Pro (Tensor G4)"

# Override BiasUncertaintyNanos threshold
python scripts/run_analysis.py Log4 --threshold 200

# Run only one notebook
python scripts/run_analysis.py Log4 --notebook v2

# All options combined
python scripts/run_analysis.py Log4 --device "Custom Label" --threshold 100 --notebook both
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
# Analyse a new log (runs both notebooks)
python scripts/run_analysis.py LogN

# With overrides
python scripts/run_analysis.py LogN --device "Label" --threshold 200 --notebook v2

# Standalone radar (after manually updating CHECKS in the script)
python scripts/gnss_radar.py

# View results
jupyter notebook LogN/outputs/gnss_quality_analysis_v2_LogN.ipynb
jupyter notebook LogN/outputs/gnss_quality_analysis_ref_LogN.ipynb
```

---

## File Reference

| File | Purpose |
|------|---------|
| `scripts/run_analysis.py` | **One-command runner — this is all you need** |
| `scripts/gnss_quality_analysis_v2.ipynb` | Master v2 notebook — 41-check framework (do not edit) |
| `scripts/gnss_analysis_ref.ipynb` | Master ref notebook — Google original (do not edit) |
| `scripts/gnss_analysis_original_reference.ipynb` | Original Google reference notebook (read-only) |
| `scripts/gnss_radar.py` | Standalone radar chart (edit manually if needed) |
| `parameters/thresholds.json` | All 41 quality thresholds — edit to change pass/fail criteria |
| `LogN/outputs/gnss_quality_analysis_v2_LogN.ipynb` | Executed v2 notebook with all results |
| `LogN/outputs/gnss_quality_analysis_ref_LogN.ipynb` | Executed ref notebook with Google conformance results |
| `docs/00_overview.md` | Project structure and device comparison table |
| `docs/01_gnsslogger_txt.md` | GnssLogger `.txt` format reference |
| `docs/02_nmea.md` | NMEA 0183 format reference |
| `docs/03_rinex.md` | RINEX 4.01 format reference |
| `docs/LogN/04_data_summary.md` | Physical interpretation of LogN (manual writeup) |
| `docs/LogN/05_gnss_quality_report.md` | Detailed quality report for LogN (manual writeup) |
