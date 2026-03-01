# File 3 — RINEX 4.01 Observation File (`gnss_log_*.26o`)

## What Is RINEX?

**RINEX** (Receiver Independent Exchange Format) is the international standard
file format for GNSS raw measurements, defined by the IGS (International GNSS
Service). The `.26o` extension means RINEX **version 4.01** observation file
from the year **2026**.

> **Document scope:** Examples and statistics in the main sections below are from
> **Log 1 (Xiaomi 13, 25 Feb 2026, 311 observations)**. The "Log2 Differences"
> section at the end covers the Sony XQ-GE54 RINEX format, which differs
> significantly in BeiDou observables and GLONASS channels.

RINEX is the format used by:
- Geodetic post-processing software (RTKLIB, CSRS-PPP, OPUS)
- Scientific analysis tools
- Precise Point Positioning (PPP) services

Unlike the Android-specific `.txt` file, RINEX is **receiver-independent** —
the same format works for any GNSS chipset worldwide.

---

## Header Section

```
     4.01           OBSERVATION DATA    M                   RINEX VERSION / TYPE
GnssLogger          Xiaomi 13           20260225 175555 UTC PGM / RUN BY / DATE
```

| Header field | Value | Meaning |
|-------------|-------|---------|
| RINEX VERSION | 4.01 | Current RINEX standard (as of 2026) |
| TYPE | OBSERVATION DATA | This is an observation file (as opposed to navigation or meteorological) |
| MARKER TYPE | M | Mixed (geodetic + non-geodetic) |
| PGM | GnssLogger | Software that created the file |
| RUN BY | Xiaomi 13 | Device that ran the software |
| DATE | 20260225 175555 UTC | File creation time |
| TIME OF FIRST OBS | 2026 02 25 17 55 55 GPS | First observation epoch |
| GLONASS SLOT | R02 −4, R11 0, R12 −1 | GLONASS frequency channel numbers |

### Observation Types per System

```
G    3 C1C D1C S1C    (GPS)
R    3 C1C D1C S1C    (GLONASS)
J    3 C1C D1C S1C    (QZSS)
C    3 C2I D2I S2I    (BeiDou)
E    3 C1C D1C S1C    (Galileo)
```

Each system records **3 observables** per satellite per epoch:

| Code | Type | Description |
|------|------|-------------|
| `C1C` | Pseudorange | Code pseudorange on L1 (GPS/GLO/GAL/QZSS) or B1I for BeiDou (C2I) |
| `D1C` | Doppler | Doppler frequency shift on L1/B1 |
| `S1C` | Signal strength | CN0 (carrier-to-noise density) on L1/B1, in dB-Hz |

**Why BeiDou uses C2I / D2I / S2I:** BeiDou's primary civil signal is **B1I at
1561.098 MHz**, which RINEX designates as frequency band "2". GPS/GLONASS/
Galileo/QZSS all use L1 (1575.42 MHz), designated band "1".

---

## Data Section Structure

Each **epoch** (observation instant) starts with a header line beginning with `>`:

```
> 2026 02 25 17 55 55.4240477  0 5
```

| Field | Value | Meaning |
|-------|-------|---------|
| Year Month Day | 2026 02 25 | Calendar date |
| Hour Min Sec | 17 55 55.4240477 | UTC time to nanosecond precision |
| Epoch flag | 0 | 0 = normal, 1–6 = special events |
| Sat count | 5 | Number of satellites observed in this epoch |

Then one observation line per satellite:

```
G23  22472891.01324      -172.85024        25.10024
```

| Field | Example | Meaning |
|-------|---------|---------|
| Sat ID | `G23` | System (G=GPS) + PRN number (23) |
| C1C | `22472891.013` | **Pseudorange in metres** — physical distance + clock/atmosphere errors |
| Suffix `24` | `24` | Signal-to-noise indicator (00–99; 24 ≈ 24/9 ≈ 2.7 RINEX SNR units, maps to ~24 dB-Hz) |
| D1C | `-172.850` | **Doppler in Hz** — negative = satellite approaching |
| S1C | `25.100` | **CN0 in dB-Hz** — signal strength |

---

## Satellite System Codes

| Code | System | Frequency recorded |
|------|--------|--------------------|
| `G` | GPS | L1 C/A (1575.42 MHz) |
| `R` | GLONASS | L1 C/A (1602 + k×0.5625 MHz, where k = channel number) |
| `E` | Galileo | E1 OS (1575.42 MHz) |
| `C` | BeiDou | B1I (1561.098 MHz) |
| `J` | QZSS | L1 C/A (1575.42 MHz) |

---

## Observation Statistics in This Log

| System | Obs count | Typical pseudorange | Typical Doppler | Typical CN0 |
|--------|----------:|--------------------:|----------------:|------------:|
| GPS (G) | 95 | 21 000–24 500 km | −2600 to +1200 Hz | 15–27 dB-Hz |
| GLONASS (R) | 83 | 22 000–23 000 km | +700 to +2660 Hz | 21–28 dB-Hz |
| BeiDou (C) | 71 | 23 000–40 000 km | −60 to +1175 Hz | 22–29 dB-Hz |
| Galileo (E) | 31 | 25 000–27 700 km | −2260 to +685 Hz | 18–23 dB-Hz |
| QZSS (J) | 31 | 37 000–37 400 km | +350–380 Hz | 21–27 dB-Hz |
| **Total** | **311** | | | |

---

## Deep Dive: Physical Meaning of Each Observable

### Pseudorange (C1C / C2I)

```
pseudorange ≈ geometric_range + clock_errors + ionosphere + troposphere + noise
```

- Typical values: 20 000–40 000 km (light travel time ~67–133 ms)
- **BeiDou GEO satellites** (e.g., C01 ≈ 40 217 km) are in geostationary orbit
  at 35 786 km — their larger pseudorange reflects this altitude plus view angle.
- **QZSS** (J03 ≈ 37 384 km) is in quasi-zenith orbit, also at high altitude.
- **MEO satellites** (GPS, GLONASS, Galileo) orbit at ~20 000–24 000 km.

The sub-integer part `.013` in `22472891.013` preserves fractional-meter
precision — important for cm-level positioning.

### Doppler (D1C / D2I)

```
Doppler (Hz) = −(range_rate / wavelength)
```

- **Negative Doppler** → satellite is approaching (range decreasing)
- **Positive Doppler** → satellite is receding (range increasing)
- Typical satellite orbital speed ≈ 3.9 km/s; projected range rate ≈ ±3 km/s
- At L1 (λ ≈ 19 cm), 3 km/s → Doppler ≈ ±15 790 Hz. The values here
  (−2600 to +2660 Hz) represent the projected component toward the receiver,
  which depends on geometry.

A **zero or near-zero Doppler** would indicate the satellite is crossing
the sky perpendicular to the line of sight.

### Signal Strength (S1C)

Same as CN0 in dB-Hz. Values in this log range from **15 to 31 dB-Hz**.

| CN0 (dB-Hz) | Quality |
|-------------|---------|
| < 20 | Poor — marginal tracking, likely to drop |
| 20–25 | Moderate — can maintain lock |
| 25–35 | Good — typical open-sky signal |
| 35–45 | Excellent — unobstructed clear-sky view |
| > 45 | Outstanding — uncommon for L1 C/A |

---

## RINEX vs TXT vs NMEA — What Each Format Adds

| Aspect | TXT (Raw) | NMEA | RINEX |
|--------|-----------|------|-------|
| Pseudorange | Yes (metres) | No | Yes (metres, higher precision) |
| Doppler | Yes (m/s) | No | Yes (Hz) |
| Carrier phase | Yes (ADR, metres) | No | No (this log) |
| Signal strength | Yes (dB-Hz) | Yes (dB-Hz in GSV) | Yes (dB-Hz) |
| Satellite position | Yes (ECEF) | No | No |
| Position fix | Yes | Yes | No |
| Ionosphere model | Yes (Klobuchar) | No | No |
| Interoperability | Android only | Universal | Universal |
| Post-processing | Via gnss-lib-py | Specialist tools | RTKLIB, etc. |

---

## GLONASS Frequency Channels

The header declares:
```
3 R02 -4 R11  0 R12 -1
```

GLONASS uses FDMA (frequency-division multiple access). Each satellite transmits
on a slightly different frequency:

```
f_L1 = 1602 MHz + k × 0.5625 MHz
```

| Sat | Channel k | L1 frequency |
|-----|-----------|--------------|
| R02 | −4 | 1602 − 4×0.5625 = 1599.75 MHz |
| R11 | 0 | 1602.0 MHz |
| R12 | −1 | 1601.4375 MHz |

This is why GLONASS requires its own receiver hardware path — each satellite
is on a different frequency, unlike GPS/Galileo/BeiDou which use CDMA on a
shared frequency.

---

## Log2 Differences (Sony XQ-GE54, 27 Feb 2026)

The Log2 RINEX file has the same RINEX 4.01 structure but reveals two important
chipset upgrades over Log1.

### Header

```
     4.01           OBSERVATION DATA    M                   RINEX VERSION / TYPE
GnssLogger          Sony XQ-GE54        20260227 071934 UTC PGM / RUN BY / DATE
```

### Observation Types — BeiDou Dual-Frequency

```
Log1:  C    3 C2I D2I S2I          (BeiDou — 3 obs types, B1I only)
Log2:  C    6 C1P D1P S1P C2I D2I S2I   (BeiDou — 6 obs types, B1C + B1I)
```

Log2 records **6 observables per BeiDou satellite per epoch** instead of 3:

| Code | Signal | Frequency | Description |
|------|--------|-----------|-------------|
| `C1P` | B1C pilot | 1575.42 MHz | Pseudorange on B1C (CDMA, same freq as GPS L1) |
| `D1P` | B1C | 1575.42 MHz | Doppler on B1C |
| `S1P` | B1C | 1575.42 MHz | CN0 on B1C (dB-Hz) |
| `C2I` | B1I | 1561.098 MHz | Pseudorange on B1I (legacy civil signal) |
| `D2I` | B1I | 1561.098 MHz | Doppler on B1I |
| `S2I` | B1I | 1561.098 MHz | CN0 on B1I (dB-Hz) |

This means the Sony can form a **BeiDou dual-frequency iono-free combination**
using B1C (1575.42 MHz) and B1I (1561.098 MHz), partially correcting BeiDou
ionospheric delay without GPS L5.

All other systems (GPS, GLONASS, Galileo, QZSS) remain at 3 observables per
satellite, same as Log1:

```
G    3 C1C D1C S1C    (GPS, unchanged)
R    3 C1C D1C S1C    (GLONASS, unchanged)
J    3 C1C D1C S1C    (QZSS, unchanged)
E    3 C1C D1C S1C    (Galileo, unchanged)
```

### GLONASS Frequency Channels — 6 Satellites vs 3

```
Log1:  3  R02 -4  R11  0  R12 -1
Log2:  6  R09 -2  R11  0  R12 -1  R21  4  R22 -3  R23  3
```

| Sat | Channel k | L1 frequency |
|-----|-----------|--------------|
| R09 | −2 | 1600.875 MHz |
| R11 | 0 | 1602.000 MHz |
| R12 | −1 | 1601.4375 MHz |
| R21 | +4 | 1604.250 MHz |
| R22 | −3 | 1600.3125 MHz |
| R23 | +3 | 1603.6875 MHz |

The Log2 session tracked 6 GLONASS satellites (vs 3 in Log1) with a wider
spread of frequency channels (−3 to +4 vs −4 to 0). This improves GLONASS
geometry and provides a more diverse FDMA frequency set.

### Observation Statistics (Log2)

| System | Obs count | Typical pseudorange | Typical CN0 |
|--------|----------:|--------------------:|------------:|
| GPS (G) | ~1430 | 21 000–24 500 km | 30–50 dBHz |
| GLONASS (R) | ~690 | 22 000–23 000 km | 32–45 dBHz |
| BeiDou B1I (C2I) | ~2260 | 23 000–40 000 km | 35–50 dBHz |
| BeiDou B1C (C1P) | ~1280 | 23 000–40 000 km | 30–46 dBHz |
| Galileo (E) | ~1268 | 25 000–27 700 km | 30–48 dBHz |
| QZSS (J) | ~258 | 37 000–37 400 km | 35–47 dBHz |
| **Total** | **~7181** | | |
