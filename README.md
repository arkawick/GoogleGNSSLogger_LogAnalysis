# GNSS Log Analysis

Raw GNSS measurement analysis using Google's [GnssLogger](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger) app, evaluated against the **Google Android Bootcamp GNSS Quality Framework** (41 checks).

---

## Recordings at a Glance

| | Log 1 | Log 2 |
|--|-------|-------|
| **Device** | Xiaomi 13 (2201116PI) | Sony XQ-GE54 |
| **Chipset** | Qualcomm MPSS.HI.4.3.1 | Qualcomm MPSS.DE.9.0 |
| **Android** | 13 | 16 |
| **Date / Time (IST)** | 25 Feb 2026, 23:25–23:26 | 27 Feb 2026, 12:49–12:51 |
| **Duration** | 44 s | 129 s |
| **Location** | 13.0667°N 77.5917°E, Bangalore | 13.0682°N 77.5918°E, Bangalore |
| **Altitude MSL** | 921.7 m | 958.7 m |
| **Raw measurements** | 311 | 7 181 |
| **Constellations** | GPS GLO BDS GAL QZSS | GPS GLO BDS (B1I+B1C) GAL QZSS |
| **Mean CN0** | 23.4 dBHz | 38.1 dBHz |
| **BiasUncNanos** | 75–129 ns | 4.6–6.5 ns |
| **Reported GPS Hacc** | 10.9 m | 3.8 m |
| **HDOP** | 0.7 | 0.4 |
| **ADR (carrier phase)** | 0% (state = 0) | 0% valid (state = 16, half-cycle) |
| **GPS L5** | Absent | Absent |
| **Quality score (v2)** | **9 / 26 (35%)** | **18 / 27 (67%)** |

---

## Project Structure

```
GoogleGNSSLogger_LogAnalysis/
│
├── Log1/                          # Recording 1 — 25 Feb 2026, 23:25 IST
│   ├── gnss_log_2026_02_25_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log1.ipynb   ← executed notebook (all plots)
│
├── Log2/                          # Recording 2 — 27 Feb 2026, 12:49 IST
│   ├── gnss_log_2026_02_27_*.txt / .nmea / .26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log2.ipynb   ← executed notebook (all plots)
│
├── docs/
│   ├── 00_overview.md             ← full project overview & comparison table
│   ├── 01_gnsslogger_txt.md       ← GnssLogger .txt format reference
│   ├── 02_nmea.md                 ← NMEA 0183 format reference
│   ├── 03_rinex.md                ← RINEX 4.01 format reference
│   ├── Log1/
│   │   ├── 04_data_summary.md     ← Log1 physical interpretation
│   │   └── 05_gnss_quality_report.md  ← Log1 quality report (legacy 35-metric)
│   └── Log2/
│       ├── 04_data_summary.md     ← Log2 physical interpretation
│       └── 05_gnss_quality_report.md  ← Log2 quality report (v2 41-check)
│
├── scripts/
│   ├── gnss_quality_analysis_v2.ipynb  ← MAIN NOTEBOOK — change LOG_DIR at top
│   ├── gnss_radar.py                   ← standalone inverted radar chart
│   ├── gnss_analysis.py                ← legacy exploratory script (Log1)
│   ├── gnss_analysis.ipynb             ← legacy exploratory notebook (Log1)
│   └── gnss_quality_analysis.ipynb     ← legacy quality notebook (Log1, 35-metric)
│
├── README.md
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Usage

### Analyse a Log

1. Open **`scripts/gnss_quality_analysis_v2.ipynb`** in Jupyter
2. In the first code cell, set:
   ```python
   LOG_DIR          = r"../Log1"                         # ← point to log folder
   DEVICE_NAME      = "Xiaomi 13 (Qualcomm MPSS.HI)"    # ← device label
   BIAS_UNC_THRESH  = 200.0                              # ← relax to 200 for MPSS.HI
   ```
   For Log2 use `LOG_DIR = r"../Log2"`, `BIAS_UNC_THRESH = 40.0`.
3. **Run All** — outputs (PNG plots + executed notebook) are saved automatically to `<LOG_DIR>/outputs/`.

### Standalone Radar Chart

```bash
python scripts/gnss_radar.py
```

Edit `LOG_DIR_NAME`, `DEVICE`, `SCORE`, and `CHECKS` at the top of the script to match the log being visualised.

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

---

## Documentation

| File | Contents |
|------|----------|
| `docs/00_overview.md` | Full project overview, device comparison, how-to guide, format quirks |
| `docs/01_gnsslogger_txt.md` | Every field in the GnssLogger `.txt` CSV; Log1 vs Log2 differences |
| `docs/02_nmea.md` | All NMEA 0183 sentence types; Log1 vs Log2 counts |
| `docs/03_rinex.md` | RINEX 4.01 structure, observation codes; Log2 dual-BDS section |
| `docs/Log1/04_data_summary.md` | Log1 physical interpretation |
| `docs/Log1/05_gnss_quality_report.md` | Log1 quality report (35-metric legacy + v2 note) |
| `docs/Log2/04_data_summary.md` | Log2 physical interpretation |
| `docs/Log2/05_gnss_quality_report.md` | Log2 quality report (v2 41-check framework) |

---

## References

- [GnssLogger on Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger)
- [Android Raw GNSS Measurements](https://developer.android.com/develop/sensors-and-location/sensors/gnss)
- [google/gps-measurement-tools](https://github.com/google/gps-measurement-tools)
- [gnss-lib-py documentation](https://gnss-lib-py.readthedocs.io/)
- [RINEX 4.01 specification](https://igs.org/wg/rinex/)
