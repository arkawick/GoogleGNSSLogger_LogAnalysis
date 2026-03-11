# GNSS Log Analysis

Raw GNSS measurement analysis using Google's [GnssLogger](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger) app, evaluated against the **Google Android Bootcamp GNSS Quality Framework** (41 checks).

---

## Recordings at a Glance

| | Log 1 | Log 2 | Log 3 | Log 4 |
|--|-------|-------|-------|-------|
| **Device** | Xiaomi 13 (2201116PI) | Sony XQ-GE54 | Sony XQ-GE54 | Sony SO-51G |
| **Chipset** | Qualcomm MPSS.HI.4.3.1 | Qualcomm MPSS.DE.9.0 | Qualcomm MPSS.DE.9.0 | Qualcomm MPSS.DE.9.0 |
| **Android** | 13 | 16 | 16 | 16 |
| **Date / Time (IST)** | 25 Feb 2026, 23:25–23:26 | 27 Feb 2026, 12:49–12:51 | 02 Mar 2026, 17:45–17:47 | 10 Mar 2026, 17:19–17:22 |
| **Duration** | 44 s | 129 s | 120 s | ~180 s |
| **Location** | 13.0667°N 77.5917°E, Bangalore | 13.0682°N 77.5918°E, Bangalore | 13.0682°N 77.5918°E, Bangalore | Bangalore |
| **Raw measurements** | 311 | 7 181 | 4 440 | 7 018 |
| **Constellations** | GPS GLO BDS GAL QZSS | GPS GLO BDS (B1I+B1C) GAL QZSS | GPS GLO BDS (B1C only) GAL QZSS | GPS GLO BDS (B1C only) GAL QZSS |
| **Mean CN0** | 23.4 dBHz | 38.1 dBHz | **43.9 dBHz** | **51.6 dBHz** |
| **BiasUncNanos** | 75–129 ns | 4.6–6.5 ns | 4.5–5.7 ns | — |
| **Reported GPS Hacc** | 10.9 m | 3.8 m | 3.8 m | — |
| **HDOP** | 0.7 | 0.4 | 0.4 | 0.7 |
| **ADR (carrier phase)** | 0% (state = 0) | 0% valid (state = 16, half-cycle) | 0% valid (state = 16, half-cycle) | 0% (state = 0) |
| **GPS L5** | Absent | Absent | Absent | Absent |
| **Quality score (v2)** | **10 / 26 (38%)** | **17 / 27 (63%)** | **17 / 26 (65%)** | **15 / 26 (58%)** |
| **Ref notebook** | — (poor data quality) | ✓ | ✓ | — (too many clock discontinuities) |

---

## Project Structure

```
GoogleGNSSLogger_LogAnalysis/
│
├── Log1/                          # Recording 1 — 25 Feb 2026, 23:25 IST (Xiaomi 13)
│   ├── gnss_log_2026_02_25_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log1.ipynb     ← v2 41-check notebook
│
├── Log2/                          # Recording 2 — 27 Feb 2026, 12:49 IST (Sony XQ-GE54)
│   ├── gnss_log_2026_02_27_*.txt / .nmea / .26o
│   └── outputs/
│       ├── gnss_quality_analysis_v2_Log2.ipynb     ← v2 41-check notebook
│       └── gnss_quality_analysis_ref_Log2.ipynb    ← Google reference notebook
│
├── Log3/                          # Recording 3 — 02 Mar 2026, 17:45 IST (Sony XQ-GE54)
│   ├── gnss_log_2026_03_02_*.txt / .nmea / .26o
│   └── outputs/
│       ├── gnss_quality_analysis_v2_Log3.ipynb     ← v2 41-check notebook
│       └── gnss_quality_analysis_ref_Log3.ipynb    ← Google reference notebook
│
├── Log4/                          # Recording 4 — 10 Mar 2026, 17:19 IST (Sony SO-51G)
│   ├── gnss_log_2026_03_10_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log4.ipynb     ← v2 41-check notebook
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
│   │   └── 05_gnss_quality_report.md  ← Log1 quality report
│   ├── Log2/
│   │   ├── 04_data_summary.md     ← Log2 physical interpretation
│   │   └── 05_gnss_quality_report.md  ← Log2 quality report
│   └── Log3/
│       ├── 04_data_summary.md     ← Log3 physical interpretation
│       └── 05_gnss_quality_report.md  ← Log3 quality report
│
├── scripts/
│   ├── run_analysis.py                     ← ONE-COMMAND RUNNER: python scripts/run_analysis.py LogN
│   ├── gnss_quality_analysis_v2.ipynb      ← master v2 notebook (41-check framework)
│   ├── gnss_analysis_ref.ipynb             ← master reference notebook (Google original, parameterised)
│   ├── gnss_analysis_original_reference.ipynb  ← original Google reference (read-only)
│   ├── gnss_radar.py                       ← standalone inverted radar chart
│   ├── gnss_analysis.py                    ← legacy exploratory script (Log1)
│   ├── gnss_analysis.ipynb                 ← legacy exploratory notebook (Log1)
│   └── gnss_quality_analysis.ipynb         ← legacy quality notebook (Log1, 35-metric)
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

By default, **both** notebooks are executed (v2 and Google reference). Outputs are saved to `LogN/outputs/`:
- `gnss_quality_analysis_v2_LogN.ipynb` — 41-check v2 analysis
- `gnss_quality_analysis_ref_LogN.ipynb` — Google original reference analysis

> **Note:** The reference notebook requires good-quality data. It will reject logs with too many clock discontinuities (duty-cycling) or insufficient WLS convergence.

**Optional overrides:**
```bash
python scripts/run_analysis.py Log4 --device "Pixel 9 Pro (Tensor G4)"
python scripts/run_analysis.py Log4 --threshold 100
python scripts/run_analysis.py Log4 --notebook v2    # v2 only
python scripts/run_analysis.py Log4 --notebook ref   # reference only
python scripts/run_analysis.py Log4 --notebook both  # both (default)
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

> Thresholds aligned to Google reference notebook v2026.01.29 in March 2026.

### Log 1 — Xiaomi 13 / MPSS.HI.4.3.1 — 10/26 PASS (38%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 5 | 3 | 6 |
| Time (8) | 4 | 4 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 1 | 4 | 7 |

Key fails: CN0 top-4 only 25.6 dBHz, BiasUnc 75–129 ns, PRR clamped at ±500 m/s, no ADR.
Ref notebook: not applicable (WLS fails due to poor signal quality).

> **BiasUncertaintyNanos note:** MPSS.HI reports 75–129 ns — relax the analysis
> threshold to 200 ns, otherwise all 311 measurements are filtered out.

### Log 2 — Sony XQ-GE54 / MPSS.DE.9.0 — 17/27 PASS (63%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 8 | 1 | 5 |
| Time (8) | 3 | 5 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 6 | 0 | 6 |

Key passes: CN0 top-4 47.1 dBHz, BiasUnc 4.9 ns, 0% PR outliers, BDS B1C+B1I dual-frequency.
Key fails: GPS L5 absent, ADR state = 16 (half-cycle, not valid), Delta ERTN jitter (stricter threshold).

### Log 3 — Sony XQ-GE54 / MPSS.DE.9.0 — 17/26 PASS (65%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 8 | 1 | 5 |
| Time (8) | 5 | 3 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 4 | 2 | 6 |

Key passes: CN0 top-4 **51.1 dBHz**, PRR residual **0.021 m/s**, clock bias std 0.035 m/s, 0% PR outliers, BDS B1C.
Key fails: GPS L5 absent, ADR state = 16 (half-cycle, not valid), Delta ERTN jitter, BDS B1I absent.

### Log 4 — Sony SO-51G / MPSS.DE.9.0 — 15/26 PASS (58%)

| Section | Pass | Fail | N/A |
|---------|:----:|:----:|:---:|
| Basic Checks (14) | 7 | 1 | 6 |
| Time (8) | 3 | 5 | 0 |
| ADR / PRR / PR (7) | 0 | 2 | 5 |
| Residuals (12) | 5 | 3 | 4 |

Key passes: CN0 top-4 **51.6 dBHz** (best across all logs), 0% PR outliers, PRR residual 0.037 m/s, clock bias std 0.235 m/s.
Key fails: GPS L5 absent, ADR = 0%, Delta ERTN jitter, LS-PR residuals 99.28 m.
Ref notebook: rejected — too many clock discontinuities (duty-cycling on SO-51G).

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
