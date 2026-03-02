# GNSS Log Analysis — Documentation Overview

## What This Project Does

This project analyses raw GNSS measurements captured by the **Google GnssLogger** app
and evaluates them against the **Google Android Bootcamp GNSS Quality Framework**
(41 checks across 4 sections). It produces:

- A fully executed Jupyter notebook with all plots and a pass/fail scorecard
- An inverted radar chart summarising the 41-check results visually
- Detailed documentation on physical interpretation and signal quality

The goal is to quantify the GNSS capability of any Android device — chipset clock
quality, signal tracking, pseudorange/Doppler noise, carrier-phase availability —
in a reproducible, comparable way.

---

## The Three Log File Formats

Every GnssLogger session produces three files:

| Extension | Format | Contents |
|-----------|--------|---------|
| `.txt` | GnssLogger CSV | Raw GNSS measurements, position fixes, IMU sensors |
| `.nmea` | NMEA 0183 | Human-readable navigation sentences (position, DOP, satellites in view) |
| `.26o` | RINEX 4.01 | International-standard GNSS observation file (pseudorange, Doppler, CN0) |

See the format reference docs in `docs/` for a complete field-by-field explanation of each.

---

## The Analysis Framework — 41 Quality Checks

The notebook implements the **Google Android Bootcamp GNSS Quality Framework**:
41 checks organised into four sections. Each check produces **PASS**, **FAIL**, or **N/A**
(not applicable, because the required signal or data is absent for this device/session).

| Section | Checks | What it tests |
|---------|:------:|--------------|
| Basic Checks | 14 | CN0 strength, epoch continuity, satellite counts per constellation/band, measurement state validity, duplicates |
| Time | 8 | Epoch timing jitter, hardware clock stability, clock-bias drift, pseudorange residual noise |
| ADR / PRR / PR | 7 | Carrier-phase (ADR) validity, Doppler–phase consistency, pseudorange rate noise |
| Residuals | 12 | L1/L5 pseudorange residual std and normalised RMS, PR outlier rate, ADR residuals, PRR residual std and normalised RMS |

**Score** = PASS count / applicable (non-N/A) check count × 100%.

All thresholds are stored in `parameters/thresholds.json` (and mirrored as CSV in
`parameters/thresholds.csv`). Editing that file changes what passes/fails without
touching the notebook.

---

## Project Structure

```
GoogleGNSSLogger_LogAnalysis/
│
├── Log1/                          # Recording 1
│   ├── gnss_log_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log1.ipynb   ← executed notebook (all plots)
│
├── Log2/                          # Recording 2
│   ├── gnss_log_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log2.ipynb
│
├── LogN/                          # Future logs — drop files here, then:
│   └── ...                        #   python scripts/run_analysis.py LogN
│
├── docs/
│   ├── 00_overview.md             ← this file
│   ├── 01_gnsslogger_txt.md       ← GnssLogger .txt format reference (all fields)
│   ├── 02_nmea.md                 ← NMEA 0183 format reference (all sentence types)
│   ├── 03_rinex.md                ← RINEX 4.01 format reference (all observables)
│   ├── 04_data_summary.md         ← generic guide: how to interpret a data summary
│   ├── 05_gnss_observables.md     ← what PR, PRR, and ADR are
│   ├── 06_how_to_run.md           ← full step-by-step guide
│   ├── 07_quality_report_guide.md ← how to read a quality scorecard (all 41 checks explained)
│   ├── 08_gnss_quality_framework.md ← Google tools, 41-check framework, and extended analysis
│   ├── 09_gnsslogger_app_tests.md  ← 14 field tests using only the GnssLogger app
│   └── LogN/
│       ├── 04_data_summary.md     ← LogN physical interpretation
│       └── 05_gnss_quality_report.md  ← LogN detailed quality report
│
├── scripts/
│   ├── run_analysis.py             ← ONE-COMMAND RUNNER: python scripts/run_analysis.py LogN
│   ├── gnss_quality_analysis_v2.ipynb  ← master notebook (do not edit config here)
│   ├── gnss_radar.py                   ← standalone inverted radar chart
│   └── ...                             ← legacy exploratory scripts
│
├── parameters/
│   ├── thresholds.json            ← all 41 quality thresholds (edit to change pass/fail)
│   └── thresholds.csv             ← same data in CSV for readability
│
├── README.md
└── requirements.txt
```

---

## How to Analyse a New Log

```bash
python scripts/run_analysis.py LogN
```

The script auto-detects device name and `BiasUncertaintyNanos` threshold from the
GnssLogger header. The executed notebook is saved to `LogN/outputs/`.

For the full step-by-step guide (record → transfer → setup → run → view → customise):
```
docs/06_how_to_run.md
```

For the standalone radar chart (must be updated manually with check results):
```
python scripts/gnss_radar.py
```
Edit `LOG_DIR_NAME`, `DEVICE`, `SCORE`, and `CHECKS` at the top of the script.

---

## Format Reference Docs

| File | Contents |
|------|----------|
| `01_gnsslogger_txt.md` | Every row type and column in the GnssLogger `.txt` CSV; pseudorange computation; constellation-specific time offsets; ADR/State bitmasks; annotated row examples |
| `02_nmea.md` | Every NMEA 0183 sentence type and field; coordinate format; fix quality codes; DOP interpretation; annotated full-epoch example |
| `03_rinex.md` | RINEX 4.01 structure; observation codes; header fields; GLONASS FDMA channels; format vs TXT/NMEA comparison; annotated header and data examples |
| `04_data_summary.md` | Generic guide to interpreting a log's physical data summary (location, sky, signal quality, accuracy, motion, NMEA inventory, RINEX observables) |
| `05_gnss_observables.md` | What PR, PRR, and ADR are — definitions, formulas, noise levels, units, GnssLogger columns, RINEX codes, and how the quality framework tests each |
| `06_how_to_run.md` | Complete step-by-step guide: record → transfer → run → view → customise thresholds |
| `07_quality_report_guide.md` | How to read a quality scorecard — what each of the 41 checks tests, what PASS/FAIL/N/A means, structural vs environmental failures, application class assessment |
| `08_gnss_quality_framework.md` | Google's quality tools and thresholds (GnssLogger, gnss_analysis, 41 checks, chip/oscillator/antenna roles); extended analysis methods beyond Google's framework |
| `09_gnsslogger_app_tests.md` | 14 field-testable checks using only the GnssLogger app and a text editor — TTFF, ADR state, BiasUncertaintyNanos chipset class, L5 availability, multi-constellation verification, fix scatter, environment comparison, AGC interference spot-check |

---

## Log-Specific Docs

Each log folder under `docs/LogN/` contains two files:

| File | Contents |
|------|----------|
| `04_data_summary.md` | Physical interpretation for that specific log: location, sky environment, constellation details, CN0, BiasUncertaintyNanos, ADR state, position accuracy, motion, NMEA sentence counts, RINEX observables |
| `05_gnss_quality_report.md` | 41-check quality report: overall score, per-section breakdown with measured values vs thresholds, key findings, application class assessment, recommendations |

---

## Critical Format Notes (GnssLogger Parsing Quirks)

These apply regardless of which log is being analysed:

| Topic | Detail |
|-------|--------|
| CSV header lines | Each row type has a comment header starting with `# Raw,`, `# Fix,`, `# Status,` etc. Data lines start without `#`. Parse headers to get column indices. |
| `BiasUncertaintyNanos` — dedicated GNSS chipsets | Modern dedicated modems (e.g. Qualcomm MPSS.DE series) report 2–10 ns. Standard Google threshold of 40 ns is fine. |
| `BiasUncertaintyNanos` — modem-integrated chipsets | Some modem-integrated architectures (e.g. Qualcomm MPSS.HI series) report 75–200+ ns. Relax the analysis threshold to 200 ns or all measurements will be filtered out. |
| `BiasUncertaintyNanos` auto-detection | `scripts/run_analysis.py` automatically sets 200 ns for MPSS.HI chipsets (detected from the GnssLogger header) and 40 ns for all others. |
| BeiDou time offset | `ReceivedSvTimeNanos` for BDS = BDS TOW = GPS TOW − 14 s. Must add 14×10⁹ ns before subtracting from receiver time. |
| GLONASS time | `ReceivedSvTimeNanos` for GLO = GLONASS Time of Day (TOD, not GPS week time). Convert via: `t_mod = (t_rx + 10782×10⁹) mod 86400×10⁹` |
| `SvClockBiasMeters` sign | Must be **added** (not subtracted) to the raw pseudorange to correct for satellite clock error. |
| Constellation codes | 1 = GPS, 2 = SBAS, 3 = GLONASS, 4 = QZSS, 5 = BeiDou, 6 = Galileo, 7 = NavIC |
| ADR state = 0 | No carrier phase tracking at all — chipset does not expose ADR. |
| ADR state = 16 | Bit 4 set (`ADR_STATE_HALF_CYCLE_REPORTED`), bit 0 NOT set (`ADR_STATE_VALID`). Carrier phase is computed internally but the HAL does not certify it. Treat as 0% valid ADR. |
| BDS B1I / B1C variability | Even on the same device and site, BeiDou may report B1I only, B1C only, or both B1I+B1C depending on chipset HAL state at session start. |
| GPS L5 availability | L5 (1176.45 MHz) is absent from many Android GNSS HALs even on hardware-capable devices. Check `CarrierFrequencyHz` rather than assuming availability. |
| `HardwareClockDiscontinuityCount` | This is an **accumulated count since device boot**, not the number of jumps in the current session. A large value does not indicate clock instability within the log. |
| `MultipathIndicator` | Almost always UNKNOWN (0) — most chipset drivers do not compute multipath. Do not use for quality assessment. |
