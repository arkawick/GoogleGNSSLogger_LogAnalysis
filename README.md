# GNSS Log Analysis

Raw GNSS measurement analysis using Google's [GnssLogger](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger) app and the open-source [gnss-lib-py](https://github.com/Stanford-NavLab/gnss_lib_py) library.

## Device & Log

| Field | Value |
|-------|-------|
| Device | Xiaomi 2201116PI (Xiaomi 13) |
| Android | 13 |
| GnssLogger | v3.1.1.2 |
| Chipset | Qualcomm MPSS.HI.4.3.1 |
| Log date | 2026-02-25 17:55 UTC |
| Location | ~13.067 N, 77.592 E (Bangalore, India) |
| Altitude | ~921 m |

## Log Files

| File | Format | Description |
|------|--------|-------------|
| `gnss_log_2026_02_25_23_25_37.txt` | GnssLogger CSV | Raw GNSS measurements + IMU + Fix rows |
| `gnss_log_2026_02_25_23_25_37.nmea` | NMEA 0183 | GSV, GSA, GGA, VTG sentences |
| `gnss_log_2026_02_25_23_25_37.26o` | RINEX 4.01 | Observation file (C1C, D1C, S1C) |

## Key Results

| Metric | Value |
|--------|-------|
| Raw measurements (after filtering) | 311 |
| Constellations | GPS, GLONASS, BeiDou, Galileo, QZSS |
| CN0 mean / max | 23.4 / 31.8 dB-Hz |
| NMEA GGA fixes | 45 |
| RINEX epochs | 45 |
| HDOP average | 1.02 |
| Avg satellites used in fix | 10.1 |

> **Filter note:** The default gnss-lib-py `BiasUncertaintyNanos` threshold (40 ns) rejects all
> measurements from this device (chipset reports 75-129 ns). The analysis relaxes this to 200 ns,
> which is appropriate for mid-range Qualcomm chipsets.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Script
```bash
python gnss_analysis.py
```

### Notebook
Open `gnss_analysis.ipynb` in Jupyter or VS Code:
```bash
jupyter notebook gnss_analysis.ipynb
```

The notebook runs all analysis sections in order and displays plots inline.

## Output Plots

| File | Description |
|------|-------------|
| `cn0_by_constellation.png` | Carrier-to-noise density over time, per constellation |
| `cn0_boxplot.png` | CN0 distribution box plot per constellation |
| `pseudorange_rate.png` | Pseudorange rate (Doppler) over time |
| `raw_pseudorange.png` | Raw pseudorange distances over time |
| `sky_plot.png` | Polar sky plot coloured by CN0 |
| `sats_tracked_vs_used.png` | Satellites tracked vs used in fix per constellation |
| `elevation_histogram.png` | Satellite elevation angle distribution |
| `fix_positions.png` | Fix scatter plot by provider (GNSS / Fused / Network) |
| `accuracy_histogram.png` | Reported horizontal accuracy distribution by provider |
| `nmea_positions.png` | NMEA GGA fix positions coloured by HDOP |
| `nmea_altitude.png` | Altitude over time from NMEA GGA |

## Analysis Sections

1. **Raw GNSS** - Parses `Raw` rows via `gnss-lib-py`; computes CN0 stats, pseudorange, Doppler
2. **Fix** - Compares GNSS / Fused / Network provider positions and accuracy
3. **Status** - Parses `Status` rows for sky plot, per-constellation CN0, tracked vs used
4. **NMEA** - Extracts GGA sentences for position, altitude, HDOP
5. **RINEX** - Summarises RINEX 4.01 observation epochs and systems

## References

- [GnssLogger on Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger)
- [Android Raw GNSS Measurements](https://developer.android.com/develop/sensors-and-location/sensors/gnss)
- [gnss-lib-py documentation](https://gnss-lib-py.readthedocs.io/)
- [google/gps-measurement-tools](https://github.com/google/gps-measurement-tools)
- [RINEX 4.01 specification](https://igs.org/wg/rinex/)
