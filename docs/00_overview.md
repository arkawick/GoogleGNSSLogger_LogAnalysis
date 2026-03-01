# GNSS Log Analysis — Documentation Overview

## Project Structure

```
GoogleGNSSLogger_LogAnalysis/
│
├── Log1/                          # Recording 1 — 25 Feb 2026, 23:25 IST
│   ├── gnss_log_2026_02_25_*.txt/nmea/26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log1.ipynb   ← executed notebook (all plots inside)
│
├── Log2/                          # Recording 2 — 27 Feb 2026, 12:49 IST
│   ├── gnss_log_2026_02_27_*.txt/nmea/26o
│   └── outputs/
│       └── gnss_quality_analysis_v2_Log2.ipynb   ← executed notebook (all plots inside)
│
├── docs/
│   ├── 00_overview.md             ← this file
│   ├── 01_gnsslogger_txt.md       ← GnssLogger .txt format reference (all logs)
│   ├── 02_nmea.md                 ← NMEA 0183 format reference (all logs)
│   ├── 03_rinex.md                ← RINEX 4.01 format reference (all logs)
│   ├── Log1/
│   │   ├── 04_data_summary.md     ← Log1 physical interpretation
│   │   └── 05_gnss_quality_report.md  ← Log1 detailed quality report
│   └── Log2/
│       ├── 04_data_summary.md     ← Log2 physical interpretation
│       └── 05_gnss_quality_report.md  ← Log2 detailed quality report
│
├── scripts/
│   ├── gnss_quality_analysis_v2.ipynb  ← MAIN NOTEBOOK — change LOG_DIR at top
│   ├── gnss_radar.py                   ← standalone inverted radar
│   ├── gnss_analysis.py                ← legacy exploratory script (Log1)
│   ├── gnss_analysis.ipynb             ← legacy exploratory notebook (Log1)
│   └── gnss_quality_analysis.ipynb     ← legacy quality notebook (Log1, 35-metric)
│
├── README.md
└── requirements.txt
```

---

## Recordings at a Glance

| | Log 1 | Log 2 |
|--|-------|-------|
| **Device** | Xiaomi 13 (2201116PI) | Sony XQ-GE54 |
| **Chipset** | Qualcomm MPSS.HI.4.3.1 | Qualcomm MPSS.DE.9.0 |
| **Android** | 13 | 16 |
| **Date / Time (IST)** | 25 Feb 2026, 23:25–23:26 | 27 Feb 2026, 12:49–12:51 |
| **Duration** | 44 s | 129 s |
| **Epochs** | 45 | 130 |
| **Location** | 13.0667°N 77.5917°E | 13.0682°N 77.5918°E |
| **Altitude MSL** | 921.7 m | 958.7 m |
| **Raw measurements** | 311 | 7181 |
| **Constellations** | GPS GLO BDS GAL QZSS | GPS GLO BDS(B1I+B1C) GAL QZSS |
| **BiasUncNanos** | 75–129 ns | 4.6–6.5 ns |
| **Mean CN0** | 23.4 dBHz | 38.1 dBHz |
| **Reported GPS Hacc** | 10.9 m | 3.8 m |
| **HDOP** | 0.7 | 0.4 |
| **ADR (carrier phase)** | 0% (state=0) | 0% valid (state=16, half-cycle) |
| **GPS L5** | Absent | Absent |
| **Quality score (v2)** | 9/26 (35%) | 18/27 (67%) |

---

## How to Analyse a New Log

1. Open **`scripts/gnss_quality_analysis_v2.ipynb`** in Jupyter
2. In the first code cell, change **two lines**:
   ```python
   LOG_DIR     = r"../Log2"               # ← point to the log folder
   DEVICE_NAME = "Your Device Name"       # ← update label
   BIAS_UNC_THRESH = 40.0                 # ← relax to 200 for Qualcomm MPSS.HI
   ```
3. Run all cells — all outputs save automatically to `<LOG_DIR>/outputs/`
4. To save a notebook copy to outputs: copy the executed `.ipynb` to `<LOG_DIR>/outputs/`

For the standalone radar (standalone, must be updated manually with check results):
```
python scripts/gnss_radar.py
```
Change `LOG_DIR_NAME`, `DEVICE`, `SCORE`, and `CHECKS` at the top.

---

## Format Reference Docs (general — apply to all logs)

| File | Contents |
|------|----------|
| `01_gnsslogger_txt.md` | Every row type in the GnssLogger `.txt` CSV, all field meanings |
| `02_nmea.md` | Every NMEA 0183 sentence type in the `.nmea` file |
| `03_rinex.md` | RINEX 4.01 structure, observation codes, column meanings |

---

## Log-Specific Docs

| File | Contents |
|------|----------|
| `Log1/04_data_summary.md` | Physical interpretation: location, sky, signals, Doppler, ionosphere |
| `Log1/05_gnss_quality_report.md` | 41-check Google framework quality report for Log1 |
| `Log2/04_data_summary.md` | Physical interpretation: location, sky, signals, RINEX dual-BDS |
| `Log2/05_gnss_quality_report.md` | 41-check Google framework quality report for Log2 |

---

## Critical Format Notes (GnssLogger quirks)

| Topic | Detail |
|-------|--------|
| CSV header lines | Start with `# Raw,`, `# Fix,`, `# Status,` — data lines start with `Raw,` etc. |
| BiasUncertaintyNanos (Qualcomm MPSS.HI) | Reports 75–129 ns; relax analysis threshold to 200 ns |
| BiasUncertaintyNanos (Qualcomm MPSS.DE) | Reports 4.6–6.5 ns; standard 40 ns threshold fine |
| BeiDou time offset | `ReceivedSvTimeNanos` for BDS = BDS TOW = GPS TOW − 14 s |
| GLONASS time | `ReceivedSvTimeNanos` for GLO = GLONASS TOD; offset from GPS = +10782 s |
| SvClockBiasMeters sign | Must be **added** (not subtracted) to raw pseudorange |
| Constellation codes | 1=GPS, 3=GLO, 4=QZSS, 5=BDS, 6=GAL, 7=NavIC |
| ADR state=0 | No carrier phase at all (Xiaomi 13 / MPSS.HI) |
| ADR state=16 | Half-cycle reported, not valid (Sony XQ-GE54 / MPSS.DE) |
