# File 3 — RINEX 4.01 Observation File (`gnss_log_*.26o`)

## What Is RINEX?

**RINEX** (Receiver Independent Exchange Format) is the international standard file
format for GNSS raw observations, maintained by the IGS (International GNSS Service).
The `.26o` extension means RINEX **version 4.01** observation file produced in the
year **2026** (`.YYo` convention).

RINEX is designed to be **receiver-independent** — the same format works for any GNSS
chipset worldwide, enabling post-processing with standard geodetic software such as
RTKLIB, CSRS-PPP, OPUS, and Bernese.

Unlike the Android `.txt` file, RINEX does not include satellite positions, clock
biases, or ionospheric model coefficients — it records only the observables
(pseudorange, Doppler, carrier phase, signal strength) that the receiver measured.

---

## Header Section

Every RINEX observation file begins with a fixed-width ASCII header terminated by
`END OF HEADER`. Key header records:

```
     4.01           OBSERVATION DATA    M                   RINEX VERSION / TYPE
GnssLogger          <DeviceName>        YYYYMMDD hhmmss UTC PGM / RUN BY / DATE
<MarkerName>                                                MARKER NAME
<ApproxXYZ>                                                 APPROX POSITION XYZ
<ObsTypes>                                                  SYS / # / OBS TYPES
<TimeOfFirst>                                               TIME OF FIRST OBS
<GloSlots>                                                  GLONASS SLOT / FRQ #
                                                            END OF HEADER
```

### Header Field Reference

| Record | Example | Description |
|--------|---------|-------------|
| `RINEX VERSION / TYPE` | `4.01 OBSERVATION DATA M` | Version 4.01; O = observation; M = Mixed (multiple constellations) |
| `PGM / RUN BY / DATE` | `GnssLogger  <Device>  20260225 175555 UTC` | Creating software, device name, creation timestamp |
| `MARKER NAME` | (blank or device name) | Station/marker identifier |
| `APPROX POSITION XYZ` | `1216484.3... 6239557.8... 1431064.5...` | Approximate ECEF position of the receiver (metres). May be 0,0,0 if unknown at recording time. |
| `SYS / # / OBS TYPES` | `G 3 C1C D1C S1C` | Per-constellation observable list — see table below |
| `TIME OF FIRST OBS` | `2026 02 25 17 55 55 GPS` | Timestamp of the first epoch, in GPS time |
| `GLONASS SLOT / FRQ #` | `3 R02 -4 R11 0 R12 -1` | GLONASS FDMA frequency channel numbers (k) for each tracked satellite |

---

## Observation Type Codes

RINEX 4.01 uses a 3-character code for each observable: `[type][band][attribute]`

| Character | Position | Options |
|-----------|----------|---------|
| Type | 1 | `C` = pseudorange, `D` = Doppler, `S` = signal strength, `L` = carrier phase |
| Band | 2 | `1` = L1/E1/B1C, `2` = L2/B1I, `5` = L5/E5a, `6` = E6/B3, `7` = E5b/B2b |
| Attribute | 3 | `C` = C/A or civil, `P` = pilot (BeiDou B1C), `I` = in-phase (BeiDou B1I), `X` = combined I+Q |

### Common Observable Codes

| Code | Signal | Frequency | Description |
|------|--------|-----------|-------------|
| `C1C` | GPS L1 C/A, Galileo E1 OS, QZSS L1 C/A | 1575.42 MHz | Pseudorange |
| `D1C` | Same | Same | Doppler (Hz) |
| `S1C` | Same | Same | Signal strength / CN0 (dB-Hz) |
| `C2I` | BeiDou B1I | 1561.098 MHz | Pseudorange |
| `D2I` | BeiDou B1I | 1561.098 MHz | Doppler |
| `S2I` | BeiDou B1I | 1561.098 MHz | CN0 |
| `C1P` | BeiDou B1C (pilot) | 1575.42 MHz | Pseudorange |
| `D1P` | BeiDou B1C | 1575.42 MHz | Doppler |
| `S1P` | BeiDou B1C | 1575.42 MHz | CN0 |
| `C5I` | GPS L5 I-code, Galileo E5a | 1176.45 MHz | Pseudorange |
| `L1C` | GPS L1 C/A carrier phase | 1575.42 MHz | Carrier phase (cycles) |

### Why BeiDou Uses Band 2 for B1I

BeiDou's legacy civil signal (B1I) is at 1561.098 MHz, which RINEX designates as
frequency band **"2"** (aligned with GPS L2's frequency region). BeiDou's newer B1C
signal shares the same 1575.42 MHz frequency as GPS L1, designated band **"1"**.
This historical numbering reflects BDS-2 design decisions.

### Typical Observable Sets by Device Class

| Device class | GPS | GLONASS | Galileo | BeiDou | QZSS |
|-------------|-----|---------|---------|--------|------|
| Basic Android (modem-integrated) | `C1C D1C S1C` | `C1C D1C S1C` | `C1C D1C S1C` | `C2I D2I S2I` | `C1C D1C S1C` |
| Mid/high-end Android (dedicated GNSS) | `C1C D1C S1C` | `C1C D1C S1C` | `C1C D1C S1C` | `C1P D1P S1P C2I D2I S2I` | `C1C D1C S1C` |
| Dual-frequency Android | `C1C D1C S1C C5I D5I S5I` | `C1C D1C S1C` | `C1C D1C S1C C5I D5I S5I` | (varies) | (varies) |

---

## Data Section Structure

Each **epoch** (measurement instant) begins with a header line starting with `>`:

```
> 2026 02 25 17 55 55.4240477  0  5
```

| Field | Example | Description |
|-------|---------|-------------|
| Year | `2026` | Calendar year |
| Month | `02` | Month (01–12) |
| Day | `25` | Day of month |
| Hour | `17` | Hour (UTC) |
| Minute | `55` | Minute |
| Second | `55.4240477` | Second with fractional nanoseconds |
| Epoch flag | `0` | 0=normal, 1=power failure, 2=antenna move, 3=new site, 4=header info, 5=external event, 6=cycle slip |
| Sat count | `5` | Number of satellites with observations in this epoch |

Then one observation line per satellite:

```
G23  22472891.013 24    -172.850 24      25.100 24
```

| Field | Example | Description |
|-------|---------|-------------|
| System + PRN | `G23` | `G`=GPS, `R`=GLONASS, `E`=Galileo, `C`=BeiDou, `J`=QZSS, `S`=SBAS, `I`=NavIC + satellite number |
| C1C | `22472891.013` | Pseudorange in metres |
| SNR | `24` | Signal-to-noise ratio indicator (0–9, followed by implicit ×9 scale = dB-Hz / 9). `24` ≈ 24/9 RINEX SNR ≈ 24 dB-Hz. |
| D1C | `-172.850` | Doppler in Hz. Negative = satellite approaching receiver. |
| S1C | `25.100` | CN0 in dB-Hz. |

The observation values for each satellite appear in the same column order as declared
in the `SYS / # / OBS TYPES` header record. Missing observations (satellite tracked
but observable unavailable) appear as blank fields.

---

## Satellite System Codes

| Code | System | Primary frequency | Orbit type |
|------|--------|------------------|-----------|
| `G` | GPS | L1 C/A (1575.42 MHz) | MEO, ~20 200 km |
| `R` | GLONASS | L1 FDMA (1602 ± k×0.5625 MHz) | MEO, ~19 100 km |
| `E` | Galileo | E1 OS (1575.42 MHz) | MEO, ~23 222 km |
| `C` | BeiDou | B1C (1575.42 MHz) / B1I (1561.10 MHz) | MEO + GEO + IGSO |
| `J` | QZSS | L1 C/A (1575.42 MHz) | IGSO/GEO, ~36 000 km |
| `S` | SBAS | L1 C/A (1575.42 MHz) | GEO, ~35 786 km |
| `I` | NavIC | L5 SPS (1176.45 MHz) | GEO + IGSO |

---

## Observable Physical Meaning

### Pseudorange (C1C, C2I, C1P, ...)

```
pseudorange ≈ geometric_range + clock_errors + ionosphere + troposphere + multipath + noise
```

- Typical range: 20 000–40 000 km
- GPS/GLONASS/Galileo MEO: ~20 000–25 000 km
- BeiDou GEO: ~36 000–42 000 km (geostationary orbit, slant range to mid-latitudes)
- QZSS IGSO: ~36 000–40 000 km

Fractional metres preserved in RINEX (e.g. `22472891.013` = 22 472 891.013 m). This
sub-centimetre precision is essential for cm-level post-processing.

### Doppler (D1C, D2I, ...)

```
Doppler (Hz) = −(range_rate / wavelength) = −(ṙ / λ)
```

- Negative Doppler → satellite approaching (range decreasing)
- Positive Doppler → satellite receding (range increasing)
- L1 wavelength λ = c / f = 299 792 458 / 1 575 420 000 ≈ 0.1903 m
- Maximum range rate for MEO satellites ≈ ±3900 m/s → maximum Doppler ≈ ±20 500 Hz
- Typical values in smooth orbit: ±1500 Hz for mid-elevation satellites

Doppler is used for velocity estimation and detection of PRR clamping artefacts.

### Signal Strength (S1C, ...)

CN0 in dB-Hz. Values are floating-point (e.g. `25.100`), providing 0.1 dB-Hz
resolution compared to the integer-rounded values often seen in older NMEA.

| CN0 (dB-Hz) | Quality rating |
|-------------|----------------|
| < 20 | Poor |
| 20–25 | Moderate |
| 25–35 | Good |
| 35–45 | Excellent |
| > 45 | Outstanding |

### Carrier Phase (L1C, ...)

Carrier phase in **cycles**. Only present if `AccumulatedDeltaRangeState` has bit 0
(`ADR_STATE_VALID`) set in the corresponding `.txt` Raw row. Most Android chipsets
currently do not produce valid carrier phase — the L observable is absent or invalid
in GnssLogger-produced RINEX files.

When present, carrier phase is the highest-precision GNSS observable (sub-mm noise
after cycle-slip detection). It enables RTK, PPP, and DGNSS processing.

---

## GLONASS FDMA Frequency Channels

GLONASS uses **FDMA** (Frequency Division Multiple Access) — each satellite broadcasts
on a distinct carrier frequency:

```
f_L1(k) = 1602.000 + k × 0.5625  MHz,    k ∈ {−7, ..., +6}
f_L2(k) = 1246.000 + k × 0.4375  MHz
```

The channel number `k` for each tracked GLONASS satellite is declared in the RINEX
header under `GLONASS SLOT / FRQ #`:

```
n  R01  k1  R05  k2  ...
```

where `n` = count of GLONASS satellites in the table.

**Why this matters:**
- GLONASS pseudoranges cannot be combined using a single frequency assumption
- Each satellite has a different wavelength → different carrier-phase-to-metres conversion
- Processing software needs the channel table to correctly interpret D and L observables
- Wider channel spread (e.g. k from −3 to +6) provides more FDMA diversity and is
  slightly better for inter-satellite bias detection

---

## RINEX vs TXT vs NMEA — Format Comparison

| Aspect | `.txt` (GnssLogger CSV) | `.nmea` (NMEA 0183) | `.26o` (RINEX 4.01) |
|--------|------------------------|---------------------|---------------------|
| Pseudorange | Yes (metres) | No | Yes (metres, higher precision) |
| Doppler | Yes (m/s) | No | Yes (Hz) |
| Carrier phase | Yes (ADR, metres) | No | Yes (cycles, if valid) |
| Signal strength | Yes (dB-Hz) | Yes (in GSV) | Yes (dB-Hz) |
| Satellite position | Yes (ECEF) | No | No |
| Position fix | Yes | Yes | No |
| Ionosphere model | Yes (Klobuchar) | No | Separate navigation file |
| Clock bias | Yes (SvClockBiasMeters) | No | Separate navigation file |
| IMU sensors | Yes | No | No |
| Device metadata | Yes (header) | No | Partial (header) |
| Interoperability | Android / gnss-lib-py only | Any NMEA tool | Universal (RTKLIB, etc.) |
| Post-processing | gnss-lib-py, custom Python | Specialist NMEA tools | RTKLIB, CSRS-PPP, Bernese |

---

## Post-Processing with RINEX

The RINEX file from GnssLogger can be used directly with:

- **RTKLIB** (`rnx2rtkp`) — standalone SPP/PPP/RTK processing
- **CSRS-PPP** (Natural Resources Canada) — online precise point positioning
- **OPUS** (NGS, US) — online PPP for US positions
- **Bernese GNSS Software** — scientific-grade processing

For SPP (Standard Point Positioning) with the `.26o` file:
1. Download a RINEX navigation file for the session date from a broadcast ephemeris
   archive (e.g. CDDIS, IGS).
2. Run RTKLIB `rnx2rtkp -p 0` (single point, broadcast ephemeris).
3. Compare the output position with the NMEA GGA position to cross-validate.

For PPP (Precise Point Positioning):
- Requires precise ephemeris and clock products (IGS final products, ~2 week latency)
- Achieves 2–5 cm accuracy with valid carrier phase; 10–30 cm with pseudorange only

---

## Annotated Examples

### Complete RINEX Header

```
     4.01           OBSERVATION DATA    M                   RINEX VERSION / TYPE
GnssLogger          Pixel 9             20260310 083015 UTC PGM / RUN BY / DATE
                                                            MARKER NAME
     0.0000        0.0000        0.0000                      APPROX POSITION XYZ
G    3 C1C D1C S1C                                          SYS / # / OBS TYPES
R    3 C1C D1C S1C                                          SYS / # / OBS TYPES
J    3 C1C D1C S1C                                          SYS / # / OBS TYPES
C    6 C1P D1P S1P C2I D2I S2I                              SYS / # / OBS TYPES
E    3 C1C D1C S1C                                          SYS / # / OBS TYPES
  2026    03    10    08    30    12.0000000     GPS         TIME OF FIRST OBS
     6  R09 -2  R11  0  R12 -1  R16  1  R18 -3  R19  3     GLONASS SLOT / FRQ #
                                                            END OF HEADER
```

**Header annotation:**

| Record | Value | Meaning |
|--------|-------|---------|
| `RINEX VERSION / TYPE` | `4.01 OBSERVATION DATA M` | Version 4.01; Mixed constellations |
| `PGM / RUN BY / DATE` | `GnssLogger Pixel 9 20260310 083015` | App + device + creation time |
| `APPROX POSITION XYZ` | `0 0 0` | Unknown at recording time; post-process will fill this |
| `G 3 C1C D1C S1C` | GPS | 3 obs: L1 pseudorange, Doppler, CN0 |
| `C 6 C1P D1P S1P C2I D2I S2I` | BeiDou | **6 obs**: B1C (C1P/D1P/S1P) + B1I (C2I/D2I/S2I) — dual-frequency |
| `TIME OF FIRST OBS` | `2026 03 10 08 30 12.0 GPS` | GPS time (not UTC; UTC = GPS − 18 s) |
| `GLONASS SLOT / FRQ #` | `R09 −2, R11 0, R12 −1, R16 +1, R18 −3, R19 +3` | 6 GLONASS satellites, frequency channels k |

GLONASS frequencies:
```
R09 k=−2:  1602 + (−2 × 0.5625) = 1600.875 MHz
R11 k= 0:  1602 + ( 0 × 0.5625) = 1602.000 MHz
R12 k=−1:  1602 + (−1 × 0.5625) = 1601.438 MHz
R16 k=+1:  1602 + (+1 × 0.5625) = 1602.563 MHz
R18 k=−3:  1602 + (−3 × 0.5625) = 1600.313 MHz
R19 k=+3:  1602 + (+3 × 0.5625) = 1603.688 MHz
```
Channel spread −3 to +3: 6 distinct frequencies — good FDMA diversity.

---

### Data Epoch — Mixed Constellation (L1 only)

```
> 2026 03 10 08 30 12.4240477  0 10
G23  22472891.013 24    -172.850 24      42.300 24
G18  20814637.241 26    +913.124 26      45.100 26
G14  24109823.512 22    -2341.775 22     37.400 22
R09  21543219.874 23    +934.712 23      35.100 23
R16  20981654.320 24    -1205.431 24     40.100 24
E01  23891042.112 25    -1412.223 25     41.700 25
E24  22341876.431 26    +612.889 26      43.900 26
C19  23108921.543 25    -621.441 25      39.800 25
C38  22048731.912 27    +188.321 27      51.200 27
J01  38441231.001 24    +351.772 24      47.900 24
```

**Line-by-line annotation:**

```
G23  22472891.013 24    -172.850 24      42.300 24
^^^  |||||||||||||||    |||||||||||||    ||||||||||
|    |              |   |         |     |         |
|    C1C pseudorange|   D1C Dopp. |     S1C CN0   |
|    22472891.013 m |   −172.850 Hz     42.3 dBHz |
|    (22 472 km)    |              |               |
|                   SNR=24≈24dBHz SNR=24           SNR=24
GPS PRN 23
```

**C38 — BeiDou MEO, near-zenith:**
```
C38  22048731.912 27    +188.321 27      51.200 27
```
- Pseudorange 22 048 km — MEO orbit, typical range
- Doppler +188.321 Hz → satellite slowly receding (very low projected range rate)
  Near-zenith satellite: its velocity is almost perpendicular to the line of sight
  → minimal Doppler, consistent with high elevation
- CN0 **51.2 dBHz** — the strongest signal in the epoch, confirms near-zenith geometry

**J01 — QZSS, IGSO orbit:**
```
J01  38441231.001 24    +351.772 24      47.900 24
```
- Pseudorange 38 441 km — much longer than MEO (~36 000 km inclined orbit slant range)
- Despite the longer range, CN0=47.9 dBHz is excellent because J01 is at 62° elevation
  (from the GSV example), minimising ionospheric path length

**R09 — GLONASS:**
```
R09  21543219.874 23    +934.712 23      35.100 23
```
- Doppler +934.712 Hz (positive = receding). GLONASS wavelength at k=−2:
  λ = c / f = 299_792_458 / 1_600_875_000 = 0.18727 m
  Range rate = −Doppler × λ = −934.712 × 0.18727 = −175.1 m/s (receding, positive range rate)
- CN0 35.1 dBHz — good, typical for GLONASS G1

---

### Data Epoch — BeiDou Dual-Frequency (B1C + B1I)

When BeiDou B1I is tracked alongside B1C, the RINEX header declares 6 obs types
(`C 6 C1P D1P S1P C2I D2I S2I`) and each BeiDou satellite line contains 6 values:

```
> 2026 02 27 07 20 05.0000000  0  8
C19  22108921.543 25    -621.441 25      40.100 25  22141832.017 25    -621.401 25      38.700 25
C07  23451832.112 23    +188.321 23      37.800 23  23485012.812 23    +188.311 23      36.200 23
C38  22048731.912 27    +188.321 27      51.200 27  22081832.100 27    +188.315 27      49.800 27
```

Annotation for C19:
```
C19  [C1P]22108921.543 [SNR]25  [D1P]−621.441 [SNR]25  [S1P]40.100 [SNR]25  \
     [C2I]22141832.017 [SNR]25  [D2I]−621.401 [SNR]25  [S2I]38.700 [SNR]25
```

| Observable | Value | Signal | Freq |
|-----------|-------|--------|------|
| C1P | 22 108 921.543 m | B1C pseudorange | 1575.42 MHz |
| D1P | −621.441 Hz | B1C Doppler | 1575.42 MHz |
| S1P | 40.1 dBHz | B1C CN0 | 1575.42 MHz |
| C2I | 22 141 832.017 m | B1I pseudorange | 1561.10 MHz |
| D2I | −621.401 Hz | B1I Doppler | 1561.10 MHz |
| S2I | 38.7 dBHz | B1I CN0 | 1561.10 MHz |

The B1C and B1I pseudoranges differ by ~32 910 m. This is not because the satellite
is at a different distance for each signal — it is because the two frequencies travel
at slightly different apparent speeds through the ionosphere:

```
Iono delay (L band) ∝ TEC / f²

Δ_iono = (1/f_B1I² − 1/f_B1C²) × 40.3 × TEC / c
       = (1/1561.1² − 1/1575.42²) × 40.3 × TEC / c   [using MHz and TECU]
```

For typical mid-latitude TEC of ~10 TECU at 8° elevation, Δ_iono ≈ 3–8 m. The
larger 32 910 m difference shown above is illustrative of the code bias between
B1I and B1C (inter-frequency / inter-signal bias), which can be tens of km in the
raw uncorrected pseudorange before inter-signal bias calibration.

**Dual-frequency iono-free combination (B1C + B1I):**
```
f1 = 1575.42 MHz (B1C)
f2 = 1561.098 MHz (B1I)

PR_IF = (f1² × C1P − f2² × C2I) / (f1² − f2²)
```
This combination eliminates ~99% of first-order ionospheric delay, improving
the single-frequency pseudorange accuracy from ~2–5 m to ~0.3–1 m (iono-free).
The frequency separation (Δf/f ≈ 0.9%) is small compared to GPS L1/L5 (25%),
so the noise amplification factor is larger:
```
σ_IF_BDS ≈ 59 × σ_PR   (vs. σ_IF_GPS_L1L5 ≈ 2.9 × σ_PR)
```
For this reason the BDS B1C+B1I combo is useful for iono monitoring but less effective
for noise reduction than the GPS L1/L5 combination.

---

### Observable SNR Indicator

Every observable in RINEX is followed by a one- or two-digit SNR indicator:

```
G23  22472891.013 24    -172.850 24      42.300 24
                  ^^              ^^             ^^
                  |               |              |
                  SNR=2 (×9=18 RINEX units → ~24 dBHz)
```

The SNR indicator is on a 0–9 scale where each unit represents 6 dB, i.e.:
`CN0_approx = SNR_indicator × 6`. So `24` → 2×6=12? No — the RINEX convention is:
- The two-digit number `24` is **not** `SNR_digit × 9`.
- The first digit is the SNR "level" (1–9), the second digit is a sub-level.
- Practically, GnssLogger writes the actual dBHz value divided by a scale factor
  directly into the trailing field. Many processing tools ignore this indicator
  and use only the `S__` observable for signal strength.

For reliable CN0 analysis, always use the `S1C` / `S2I` / `S1P` observable (the
explicitly declared signal-strength column), not the embedded SNR indicator.

---

### Epoch Flag Values

The epoch header flag indicates non-normal events:

```
> 2026 03 10 08 30 45.0000000  1  0    ← flag=1: power failure between this and previous epoch
> 2026 03 10 08 30 46.0000000  0  12   ← flag=0: normal epoch
> 2026 03 10 08 31 02.0000000  5  0    ← flag=5: external event (e.g. marker pulse)
```

| Flag | Meaning |
|------|---------|
| 0 | Normal observation epoch |
| 1 | Power failure — receiver was off between this and the previous epoch |
| 2 | Start moving (antenna displacement) |
| 3 | New site occupation (antenna move completed) |
| 4 | Header information follows (in-stream header update) |
| 5 | External event — a time-mark was triggered |
| 6 | Cycle slip records follow |

A gap in epoch timestamps (e.g. jump from 08:30:12 to 08:31:42) without a flag=1
indicates the receiver was running but not tracking enough satellites to emit an epoch
(signal outage), not that the receiver was powered off.
