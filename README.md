# GNSS Log Analysis

Raw GNSS measurement analysis using Google's [GnssLogger](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger) app, evaluated against the **Google Android Bootcamp GNSS Quality Framework** (41 checks).

---

## Recordings at a Glance

| | Log 1 | Log 2 | Log 3 |
|--|-------|-------|-------|
| **Device** | Xiaomi 13 (2201116PI) | Sony XQ-GE54 | Sony XQ-GE54 |
| **Chipset** | Qualcomm MPSS.HI.4.3.1 | Qualcomm MPSS.DE.9.0 | Qualcomm MPSS.DE.9.0 |
| **Android** | 13 | 16 | 16 |
| **Date / Time (IST)** | 25 Feb 2026, 23:25–23:26 | 27 Feb 2026, 12:49–12:51 | 02 Mar 2026, 17:45–17:47 |
| **Duration** | 44 s | 129 s | 120 s |
| **Location** | 13.0667°N 77.5917°E, Bangalore | 13.0682°N 77.5918°E, Bangalore | 13.0682°N 77.5918°E, Bangalore |
| **Altitude MSL** | 921.7 m | 958.7 m | 962.6 m |
| **Raw measurements** | 311 | 7 181 | 4 440 |
| **Constellations** | GPS GLO BDS GAL QZSS | GPS GLO BDS (B1I+B1C) GAL QZSS | GPS GLO BDS (B1C only) GAL QZSS |
| **Mean CN0** | 23.4 dBHz | 38.1 dBHz | **43.9 dBHz** |
| **BiasUncNanos** | 75–129 ns | 4.6–6.5 ns | 4.5–5.7 ns |
| **Reported GPS Hacc** | 10.9 m | 3.8 m | 3.8 m |
| **HDOP** | 0.7 | 0.4 | 0.4 |
| **ADR (carrier phase)** | 0% (state = 0) | 0% valid (state = 16, half-cycle) | 0% valid (state = 16, half-cycle) |
| **GPS L5** | Absent | Absent | Absent |
| **Quality score (v2)** | **9 / 26 (35%)** | **18 / 27 (67%)** | **17 / 26 (65%)** |

---

## Project Structure

```
GoogleGNSSLogger_LogAnalysis/
│
├── Log1/                          # Recording 1 — 25 Feb 2026, 23:25 IST (Xiaomi 13)
│   ├── gnss_log_2026_02_25_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log1.ipynb   ← executed notebook (all plots)
│
├── Log2/                          # Recording 2 — 27 Feb 2026, 12:49 IST (Sony XQ-GE54)
│   ├── gnss_log_2026_02_27_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log2.ipynb   ← executed notebook (all plots)
│
├── Log3/                          # Recording 3 — 02 Mar 2026, 17:45 IST (Sony XQ-GE54)
│   ├── gnss_log_2026_03_02_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log3.ipynb   ← executed notebook (all plots)
│
├── LogN/                          # Future logs — drop files here, then run:
│   └── ...                        #   python scripts/run_analysis.py LogN
│
├── docs/
│   ├── 00_overview.md             ← full project overview & comparison table
│   ├── 01_gnsslogger_txt.md       ← GnssLogger .txt format reference
│   ├── 02_nmea.md                 ← NMEA 0183 format reference
│   ├── 03_rinex.md                ← RINEX 4.01 format reference
│   ├── 06_how_to_run.md           ← complete step-by-step guide
│   ├── Log1/
│   │   ├── 04_data_summary.md     ← Log1 physical interpretation
│   │   └── 05_gnss_quality_report.md  ← Log1 quality report (legacy 35-metric)
│   ├── Log2/
│   │   ├── 04_data_summary.md     ← Log2 physical interpretation
│   │   └── 05_gnss_quality_report.md  ← Log2 quality report (v2 41-check)
│   └── Log3/
│       ├── 04_data_summary.md     ← Log3 physical interpretation
│       └── 05_gnss_quality_report.md  ← Log3 quality report (v2 41-check)
│
├── scripts/
│   ├── run_analysis.py             ← ONE-COMMAND RUNNER: python scripts/run_analysis.py LogN
│   ├── gnss_quality_analysis_v2.ipynb  ← master notebook (do not edit config here)
│   ├── gnss_radar.py                   ← standalone inverted radar chart
│   ├── gnss_analysis.py                ← legacy exploratory script (Log1)
│   ├── gnss_analysis.ipynb             ← legacy exploratory notebook (Log1)
│   └── gnss_quality_analysis.ipynb     ← legacy quality notebook (Log1, 35-metric)
│
├── parameters/
│   ├── thresholds.json            ← all 41 quality thresholds (edit to change pass/fail criteria)
│   └── thresholds.csv             ← same data in CSV format for readability
│
├── README.md
└── requirements.txt
```

---

## Full Guide

For the complete step-by-step walkthrough (record → transfer → run → view → customise):

```
docs/06_how_to_run.md
```

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Usage

### Analyse a New Log (one command)

Drop the three log files (`gnss_log_*.txt`, `.nmea`, `.26o`) into a folder (e.g. `Log4/`) and run:

```bash
python scripts/run_analysis.py Log4
```

The script auto-detects everything from the GnssLogger header:
- **Device name** from `Manufacturer` + `Model` + `Platform` fields
- **BiasUncertaintyNanos threshold** from the chipset name:
  - `MPSS.HI` → 200 ns (Snapdragon Gen 1 modem, reports 75–129 ns)
  - everything else → 40 ns (standard Google threshold)

The executed notebook is saved to `Log4/outputs/gnss_quality_analysis_v2_Log4.ipynb` with all plots embedded.

**Optional overrides:**
```bash
python scripts/run_analysis.py Log4 --device "Pixel 9 Pro (Tensor G4)"
python scripts/run_analysis.py Log4 --threshold 100
```

### Open the Master Notebook Manually

If you prefer to run interactively:

1. Open **`scripts/gnss_quality_analysis_v2.ipynb`** in Jupyter
2. In the first code cell, set `LOG_DIR`, `DEVICE_NAME`, `BIAS_UNC_THRESH`
3. **Run All** — outputs save to `<LOG_DIR>/outputs/`

### Standalone Radar Chart

```bash
python scripts/gnss_radar.py
```

Edit `LOG_DIR_NAME`, `DEVICE`, `SCORE`, and `CHECKS` at the top to match the log.

---

## Key Quality Results

### Log 1 — Xiaomi 13 / MPSS.HI.4.3.1 — 9/26 PASS (35%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 5 | 3 | 6 |
| Time (8) | 4 | 4 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 0 | 4 | 8 |

Key fails: CN0 top-4 only 25.6 dBHz, BiasUnc 75–129 ns, PRR clamped at ±500 m/s, no ADR.

> **BiasUncertaintyNanos note:** MPSS.HI reports 75–129 ns — relax the analysis
> threshold to 200 ns, otherwise all 311 measurements are filtered out.

### Log 2 — Sony XQ-GE54 / MPSS.DE.9.0 — 18/27 PASS (67%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 8 | 1 | 5 |
| Time (8) | 4 | 4 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 6 | 0 | 6 |

Key passes: CN0 top-4 47.1 dBHz, BiasUnc 4.9 ns, PRR residual 0.422 m/s, 0% PR outliers, BDS B1C+B1I dual-frequency.
Key fails: GPS L5 absent, ADR state = 16 (half-cycle reported, not valid), Delta ERTN jitter.

### Log 3 — Sony XQ-GE54 / MPSS.DE.9.0 — 17/26 PASS (65%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 8 | 1 | 5 |
| Time (8) | 5 | 3 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 4 | 2 | 6 |

Key passes: CN0 top-4 **51.1 dBHz** (best of all logs), PRR residual **0.021 m/s**, clock bias std 0.035 m/s, 0% PR outliers, BDS B1C.
Key fails: GPS L5 absent, ADR state = 16 (half-cycle, not valid), Delta ERTN jitter, BDS B1I absent (N/A — reduces denominator vs Log 2).

---

## Documentation

| File | Contents |
|------|----------|
| `docs/00_overview.md` | Full project overview, all-log comparison table, format quirks |
| `docs/01_gnsslogger_txt.md` | Every field in the GnssLogger `.txt` CSV; Log1 vs Log2 differences |
| `docs/02_nmea.md` | All NMEA 0183 sentence types; Log1 vs Log2 counts |
| `docs/03_rinex.md` | RINEX 4.01 structure, observation codes; Log2 dual-BDS section |
| `docs/06_how_to_run.md` | Complete step-by-step guide: record → run → view → customise |
| `docs/Log1/04_data_summary.md` | Log1 physical interpretation |
| `docs/Log1/05_gnss_quality_report.md` | Log1 quality report (35-metric legacy + v2 note) |
| `docs/Log2/04_data_summary.md` | Log2 physical interpretation |
| `docs/Log2/05_gnss_quality_report.md` | Log2 quality report (v2 41-check framework) |
| `docs/Log3/04_data_summary.md` | Log3 physical interpretation |
| `docs/Log3/05_gnss_quality_report.md` | Log3 quality report (v2 41-check framework) |
| `parameters/thresholds.json` | All 41 quality thresholds (edit to change pass/fail criteria) |
| `parameters/thresholds.csv` | Same thresholds in CSV for readability |

---

## References

- [GnssLogger on Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger)
- [Android Raw GNSS Measurements](https://developer.android.com/develop/sensors-and-location/sensors/gnss)
- [google/gps-measurement-tools](https://github.com/google/gps-measurement-tools)
- [gnss-lib-py documentation](https://gnss-lib-py.readthedocs.io/)
- [RINEX 4.01 specification](https://igs.org/wg/rinex/)
