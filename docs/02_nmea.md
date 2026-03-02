# File 2 — NMEA 0183 Log (`gnss_log_*.nmea`)

## What Is This File?

This file contains **NMEA 0183** sentences — the universal human-readable standard for
GPS/GNSS receivers, maintained by the National Marine Electronics Association (NMEA).
NMEA 0183 v4.11 extends the original GPS-only format to support all modern constellations.

GnssLogger wraps each sentence with a timestamp:
```
NMEA,<sentence>,<utcTimeMillis>
```

- `NMEA,` — literal prefix added by GnssLogger
- `<sentence>` — the standard NMEA sentence (starting with `$`)
- `<utcTimeMillis>` — Unix timestamp in milliseconds appended by GnssLogger for correlation with Raw rows

One complete "epoch" of NMEA output is emitted approximately **every 1 second** and
contains one sentence of each navigational type plus one or more GSV sentences per
visible constellation.

---

## Sentence Type Overview

| Sentence | Purpose |
|----------|---------|
| `$GNGGA` | Global fix data — primary position sentence (lat, lon, altitude, quality, HDOP) |
| `$GNRMC` | Recommended minimum navigation data (position, speed, course, date) |
| `$GNGNS` | Multi-constellation fix data (mode indicator per constellation, DOP) |
| `$GNVTG` | Speed and course over ground |
| `$GNGSA` | Active satellites and dilution of precision (one per active constellation) |
| `$GPGSV` | GPS satellites in view (azimuth, elevation, CN0) |
| `$GLGSV` | GLONASS satellites in view |
| `$GAGSV` | Galileo satellites in view |
| `$GBGSV` | BeiDou satellites in view |
| `$GQGSV` | QZSS satellites in view |
| `$GIGSV` | NavIC satellites in view (when NavIC is tracked) |
| `$GNDTM` | Datum reference (normally WGS-84) |

---

## Talker ID Prefix

Every NMEA sentence begins with `$` followed by a two-letter **talker ID** indicating
the source:

| Prefix | Talker |
|--------|--------|
| `GP` | GPS only |
| `GL` | GLONASS only |
| `GA` | Galileo only |
| `GB` | BeiDou only |
| `GQ` | QZSS only |
| `GI` | NavIC only |
| `GN` | Combined / multiple GNSS constellations |

---

## Sentence Format and Checksum

Every sentence ends with `*XX` where `XX` is a two-digit hexadecimal checksum:

```
$GNGGA,175538.00,1304.004606,N,07735.500621,E,1,12,0.7,921.7,M,-84.0,M,,*53
                                                                            ^^^
```

The checksum is the XOR of all bytes between `$` and `*` (exclusive). To verify:
```python
sentence = "GNGGA,175538.00,..."   # everything between $ and *
checksum = 0
for c in sentence:
    checksum ^= ord(c)
assert f"{checksum:02X}" == "53"
```

---

## Coordinate Format

NMEA encodes coordinates as **DDDMM.MMMMM** (degrees and decimal minutes):

```
1304.004606,N   →   13° 04.004606' N
                →   13 + 04.004606/60  =  13.066743° N

07735.500621,E  →   077° 35.500621' E
                →   77 + 35.500621/60  =  77.591677° E
```

**Conversion formula:**
```
decimal_degrees = floor(DDDMM.MMMMM / 100) + (DDDMM.MMMMM % 100) / 60
```

Latitude uses 2-digit degrees (00–90); longitude uses 3-digit degrees (000–180).

---

## `$GNGGA` — Global Positioning System Fix Data

This is the **most important NMEA sentence** for position analysis. It provides the
full position fix with altitude and quality indicators, emitted once per epoch.

### Format

```
$GNGGA,hhmmss.ss,LLLL.LLLLL,a,YYYYY.YYYYY,a,q,NN,H.H,AAA.A,M,GGG.G,M,D.D,RRRR*CS
```

### Field Reference

| Field | Example | Description |
|-------|---------|-------------|
| Talker + type | `$GNGGA` | GN = multi-constellation; GGA = fix data |
| UTC time | `175538.00` | hhmmss.ss — time of fix. Note: this is UTC time, not GPS time. |
| Latitude | `1304.004606` | DDMM.MMMMM format |
| N/S | `N` | N = North, S = South |
| Longitude | `07735.500621` | DDDMM.MMMMM format |
| E/W | `E` | E = East, W = West |
| Fix quality | `1` | See Fix Quality table below |
| Satellites used | `12` | Number of satellites used in this fix |
| HDOP | `0.7` | Horizontal Dilution of Precision |
| Altitude | `921.7` | Altitude above **mean sea level (MSL)** in metres |
| Altitude unit | `M` | Always "M" for metres |
| Geoid separation | `-84.0` | Height of the EGM2008 geoid above the WGS-84 ellipsoid, in metres. **Negative = geoid is below ellipsoid.** WGS-84 ellipsoidal altitude = MSL altitude + geoid separation. |
| Geoid unit | `M` | Always "M" |
| DGPS age | `` | Age of differential corrections in seconds (blank if no DGPS) |
| DGPS station | `` | Reference station ID (blank if no DGPS) |
| Checksum | `*53` | XOR checksum |

### Fix Quality Codes

| Code | Meaning |
|------|---------|
| 0 | No fix |
| 1 | GPS fix (standard GNSS, autonomous) |
| 2 | DGPS fix (differential corrections applied) |
| 3 | PPS fix (precise positioning service) |
| 4 | RTK fixed integer |
| 5 | RTK float |
| 6 | Estimated / dead reckoning |
| 7 | Manual input |
| 8 | Simulation mode |

### Altitude Interpretation

The two altitude fields together define the full vertical datum:

```
MSL altitude   = from GGA "Altitude" field (above Earth's geoid)
Geoid sep (N)  = from GGA "Geoid separation" field
Ellipsoidal h  = MSL altitude + N   (altitude above WGS-84 ellipsoid)
```

The geoid separation depends on location and is provided by the EGM2008 model embedded
in the GNSS chipset's firmware. Typically ranges from −107 m (India Ocean minimum) to
+85 m (Iceland maximum). For the Indian subcontinent, values are approximately −50 to −90 m.

---

## `$GNRMC` — Recommended Minimum Navigation Data

Contains the minimum data needed for navigation. Used by simple chartplotters and
tracking systems that need speed and date alongside position.

### Format

```
$GNRMC,hhmmss.ss,A,LLLL.LLLLL,a,YYYYY.YYYYY,a,sss.s,DDD.D,DDMMYY,V.V,a,M,N*CS
```

### Field Reference

| Field | Example | Description |
|-------|---------|-------------|
| UTC time | `175538.00` | Time of fix (hhmmss.ss UTC) |
| Status | `A` | A = Active (valid fix); V = Void (invalid) |
| Latitude | `1304.004606,N` | Position (DDMM.MMMMM + N/S) |
| Longitude | `07735.500621,E` | Position (DDDMM.MMMMM + E/W) |
| Speed over ground | `0.0` | Speed in **knots** (1 knot = 0.5144 m/s) |
| Course over ground | `` | True bearing in degrees from North; blank when stationary |
| Date | `250226` | DDMMYY — day, month, year (two-digit year) |
| Magnetic variation | `1.1,W` | Local magnetic declination in degrees; W = west (compass reads high), E = east (compass reads low) |
| Mode indicator | `A` | A=Autonomous, D=Differential, E=Estimated, N=No fix |
| Nav status | `V` | V = Non-precise (no RAIM); A = RAIM active; S = Safe; C = Caution; U = Unsafe |
| Checksum | `*65` | XOR checksum |

**Date format note:** The two-digit year (e.g., `26` for 2026) requires century inference
based on context. GnssLogger-produced files from 2020+ are unambiguously 21st century.

---

## `$GNGNS` — Multi-Constellation Fix Data

An extension of GGA designed for receivers tracking multiple constellations. The mode
indicator string shows which constellations contributed to the fix.

### Format

```
$GNGNS,hhmmss.ss,LLLL.LLLLL,a,YYYYY.YYYYY,a,MMMMMM,NN,H.H,AAA.A,GGG.G,D.D,RRRR*CS
```

### Field Reference

| Field | Example | Description |
|-------|---------|-------------|
| UTC time | `175538.00` | Time of fix |
| Latitude | `1304.004606,N` | Position |
| Longitude | `07735.500621,E` | Position |
| Mode indicator | `AAAAAN` | One character **per constellation** in a fixed order (see below) |
| Satellites used | `15` | Total satellites used |
| HDOP | `0.7` | Horizontal DOP |
| Altitude | `921.7` | MSL altitude (m) |
| Geoid separation | `-84.0` | Geoid separation (m) |
| DGPS age | `` | Age of differential corrections (blank = none) |
| DGPS station | `` | Reference station ID |
| Nav status | `V` | Same as RMC |
| Checksum | `*0B` | XOR checksum |

### Mode Indicator String

The mode indicator string has one character per position, in this fixed constellation order:

| Position | Constellation |
|----------|--------------|
| 1 | GPS |
| 2 | GLONASS |
| 3 | Galileo |
| 4 | BeiDou |
| 5 | QZSS |
| 6 | NavIC |

| Character | Meaning |
|-----------|---------|
| `N` | Not used / not available |
| `A` | Autonomous fix (GNSS-only, no differential) |
| `D` | Differential fix |
| `P` | Precise positioning |
| `R` | RTK (fixed integer) |
| `F` | RTK (float) |
| `E` | Estimated / dead-reckoning |
| `M` | Manual input |
| `S` | Simulation |

Example `AAAAAN`: GPS, GLONASS, Galileo, BeiDou = Autonomous; QZSS = Autonomous; NavIC = Not used.

---

## `$GNVTG` — Speed and Course Over Ground

Reports ground velocity in both knots and km/h, with both true North and magnetic North
reference.

### Format

```
$GNVTG,DDD.D,T,DDD.D,M,SSS.S,N,SSS.S,K,A*CS
```

### Field Reference

| Field | Example | Description |
|-------|---------|-------------|
| True course | `` | Course over ground relative to true North (degrees). Blank when speed < 0.1 knots (stationary). |
| `T` | `T` | Literal "T" — True reference |
| Magnetic course | `` | Course relative to magnetic North. Blank when stationary. |
| `M` | `M` | Literal "M" — Magnetic reference |
| Speed (knots) | `0.0` | Ground speed in knots |
| `N` | `N` | Literal "N" — Knots |
| Speed (km/h) | `0.0` | Ground speed in km/h (= knots × 1.852) |
| `K` | `K` | Literal "K" — Kilometres per hour |
| Mode | `A` | A=Autonomous, D=Differential, E=Estimated, N=No fix |
| Checksum | `*3D` | XOR checksum |

A speed of `0.0` in both fields confirms a stationary receiver throughout the session.

---

## `$GNGSA` — Active Satellites and DOP

One GSA sentence is emitted **per active constellation** per epoch. With a 5-constellation
receiver, up to 5 GSA sentences appear each epoch.

### Format

```
$GNGSA,A,F,SS,SS,SS,...,SS,P.P,H.H,V.V,SID*CS
```

### Field Reference

| Field | Example | Description |
|-------|---------|-------------|
| Mode | `A` | A = Auto-select 2D/3D mode; M = Manual |
| Fix type | `3` | 1 = No fix; 2 = 2D fix (altitude not computed); 3 = 3D fix |
| SVIDs (×12) | `08,18,23,...` | Up to 12 satellite IDs used in the fix for this constellation. Unused slots are blank. |
| PDOP | `1.0` | Position (3D) Dilution of Precision |
| HDOP | `0.7` | Horizontal Dilution of Precision |
| VDOP | `0.8` | Vertical Dilution of Precision |
| System ID | `1` | 1=GPS, 2=GLONASS, 3=Galileo, 4=BeiDou, 5=QZSS, 6=NavIC |
| Checksum | `*3D` | XOR checksum |

### DOP Interpretation

DOP quantifies how satellite geometry amplifies ranging errors into position errors.
Lower DOP = better geometry = higher accuracy for the same range-error level.

| DOP value | Rating |
|-----------|--------|
| < 1.0 | Ideal — extremely tight constellation geometry |
| 1.0 – 2.0 | Excellent — typical open sky with many satellites |
| 2.0 – 5.0 | Good — acceptable for most applications |
| 5.0 – 10.0 | Moderate — reduced accuracy; avoid for precision work |
| 10.0 – 20.0 | Fair — significant geometry degradation |
| > 20.0 | Poor — very poor satellite visibility |

**Typical values for a multi-constellation open-sky receiver:**
HDOP 0.3–0.8, PDOP 0.5–1.2. HDOP < 1.0 is consistently achievable with ≥20 tracked satellites.

---

## GSV Sentences — Satellites in View

GSV sentences report all satellites visible in the sky, whether tracked or not. They
are used to generate sky plots and signal strength charts.

### General GSV Format

```
$xxGSV,T,N,TT,SS,EE,AAA,CC,...,SS,EE,AAA,CC,SID*CS
```

| Field | Description |
|-------|-------------|
| `T` | Total number of GSV sentences in this epoch for this talker |
| `N` | Sentence number within the sequence (1 to T) |
| `TT` | Total number of satellites in view for this constellation |
| Per-satellite block (×4) | `SS` = SVID; `EE` = elevation (0–90°); `AAA` = azimuth (000–359°); `CC` = CN0 in dB-Hz (blank if not tracked) |
| `SID` | Signal ID (optional in NMEA 4.11) — distinguishes B1I from B1C etc. |
| Checksum | `*XX` |

Up to 4 satellites are packed into one sentence. If there are 12 GPS satellites in view,
3 GSV sentences are required (`ceiling(12/4) = 3`).

### Sentence-by-Sentence Reference

#### `$GPGSV` — GPS Satellites in View

GPS PRN numbers are 1–32 (plus 33–64 for SBAS when prefixed as GP). Signal ID 1 = L1 C/A.

#### `$GLGSV` — GLONASS Satellites in View

GLONASS slot numbers in NMEA range from 65–96 (NMEA adds 64 to the orbital slot number).
GLONASS orbital slots are 1–24. Channel frequency: `f = 1602 + k × 0.5625 MHz` where `k`
is the frequency channel number (−7 to +6), declared in the RINEX header.

#### `$GAGSV` — Galileo Satellites in View

Galileo SVIDs are 1–36. Signal ID 7 = E1 OS; 2 = E5a; 3 = E5b; 6 = E6.

#### `$GBGSV` — BeiDou Satellites in View

BeiDou SVIDs are 1–63 in NMEA. BDS-3 MEO satellites are primarily 19–50; GEO are 1–5,
59–63; IGSO are 6–10, 38–40, 56–58. BeiDou has the largest constellation for Asia-Pacific
coverage — GEO/IGSO satellites are quasi-stationary and provide high-elevation signals.
When BDS tracks both B1I and B1C, two GSV entries may appear for the same SVID, or
separate sentences with different Signal IDs.

#### `$GQGSV` — QZSS Satellites in View

QZSS SVIDs are 193–202 in NMEA (satellites J01–J07). QZSS provides GPS L1/L2/L5
augmentation for Japan with good visibility throughout the Asia-Pacific region due to
the highly inclined (quasi-zenith) orbit.

#### `$GIGSV` — NavIC Satellites in View

NavIC (IRNSS) SVIDs are 1–14 in GnssLogger. NavIC provides regional coverage over
India and surrounding areas (±40° latitude around 83° East longitude).

---

## `$GNDTM` — Datum Reference

Reports the geodetic datum of the output coordinates relative to WGS-84.

### Format

```
$GNDTM,LLL,XXX,dlat,a,dlon,a,alt,RRR*CS
```

| Field | Example | Description |
|-------|---------|-------------|
| Local datum | `P90` | Local datum code (P90 = PZ-90 Russian, W84 = WGS-84, etc.) |
| Local datum subdivision | `` | Optional sub-division code |
| Lat offset | `0000.000011,S` | Latitude offset from local datum to WGS-84 (DDMM.MMMMM + N/S) |
| Lon offset | `00000.000001,W` | Longitude offset (DDDMM.MMMMM + E/W) |
| Alt offset | `0.999` | Altitude offset (metres) |
| Reference datum | `W84` | The reference datum — almost always `W84` (WGS-84) |
| Checksum | `*44` | XOR checksum |

When all offsets are effectively zero (< 0.01°, < 1 m), the receiver is outputting
positions directly in WGS-84 with no datum transformation. Modern GNSS chipsets always
output WGS-84.

---

## NMEA Time Format

NMEA time fields use **UTC** in `hhmmss.ss` format:
- `175538.00` = 17 hours, 55 minutes, 38.00 seconds UTC
- Fractional seconds are to 2 decimal places (10 ms resolution)
- No timezone offset — always UTC; convert to local time using the known UTC offset

The GnssLogger-appended `utcTimeMillis` at the end of each line is in Unix milliseconds
and provides millisecond-precision timestamp for correlation with Raw rows.

---

## Elevation and Azimuth in GSV

| Field | Range | Description |
|-------|-------|-------------|
| Elevation | 0–90° | 0° = on the horizon; 90° = directly overhead (zenith). Satellites with elevation < 5° are usually too noisy to use. |
| Azimuth | 000–359° | Clockwise from geographic North. 0°/360° = North, 90° = East, 180° = South, 270° = West. |

High-elevation satellites (> 45°) have shorter ionospheric path and generally stronger
signals. Low-elevation satellites (< 15°) have longer atmospheric path and are more
susceptible to multipath.

---

## Signal ID (NMEA 4.11)

The Signal ID field (last field before checksum in GSV) distinguishes frequency bands:

| Constellation | Signal ID | Signal |
|--------------|-----------|--------|
| GPS | 1 | L1 C/A |
| GPS | 5 | L2 CL |
| GPS | 6 | L2 CM |
| GPS | 7 | L5 I |
| GPS | 8 | L5 Q |
| GLONASS | 1 | G1 C/A |
| GLONASS | 3 | G2 C/A |
| Galileo | 7 | E1 OS |
| Galileo | 2 | E5a |
| Galileo | 3 | E5b |
| Galileo | 6 | E6 |
| BeiDou | 1 | B1I |
| BeiDou | 4 | B1C |
| BeiDou | 2 | B2I |
| BeiDou | 8 | B2a |
| QZSS | 1 | L1 C/A |
| QZSS | 7 | L5 I |
| NavIC | 5 | L5 SPS |

Older NMEA versions (< 4.11) omit the Signal ID field. When parsing, check whether the
field count matches 4.11 expectations before reading Signal ID.

---

## Annotated Examples

### Complete One-Second Epoch

The following block is a representative single epoch from a 5-constellation
open-sky session. Each sentence is annotated below.

```
NMEA,$GNGGA,083012.00,1304.08720,N,07735.50990,E,1,14,0.4,958.7,M,-85.8,M,,*4A,1772048698424
NMEA,$GNRMC,083012.00,A,1304.08720,N,07735.50990,E,0.0,,100326,1.1,W,A,V*62,1772048698424
NMEA,$GNGNS,083012.00,1304.08720,N,07735.50990,E,AAAAAN,20,0.4,958.7,-85.8,,,V*1D,1772048698424
NMEA,$GNVTG,,T,,M,0.0,N,0.0,K,A*3D,1772048698424
NMEA,$GNGSA,A,3,23,18,14,08,10,27,,,,,,,0.6,0.4,0.5,1*3D,1772048698424
NMEA,$GNGSA,A,3,09,16,75,82,,,,,,,,,0.6,0.4,0.5,2*32,1772048698424
NMEA,$GNGSA,A,3,19,07,28,36,24,,,,,,,0.6,0.4,0.5,3*31,1772048698424
NMEA,$GNGSA,A,3,06,14,22,36,38,08,07,,,,0.6,0.4,0.5,4*1A,1772048698424
NMEA,$GNGSA,A,3,193,194,,,,,,,,,,,0.6,0.4,0.5,5*34,1772048698424
NMEA,$GPGSV,3,1,12,08,12,287,34,10,38,012,41,18,47,139,45,23,31,059,42,1*6B,1772048698424
NMEA,$GPGSV,3,2,12,14,62,034,48,27,23,201,38,32,18,095,32,05,08,341,28,1*5F,1772048698424
NMEA,$GPGSV,3,3,12,24,55,178,44,16,11,222,29,,,,,,,,,1*5A,1772048698424
NMEA,$GLGSV,2,1,06,09,28,213,35,16,41,095,40,75,52,031,43,82,19,277,37,1*72,1772048698424
NMEA,$GLGSV,2,2,06,76,07,156,22,83,34,112,38,1*44,1772048698424
NMEA,$GAGSV,3,1,11,01,55,315,42,07,48,088,41,14,29,183,37,19,12,247,33,7*7B,1772048698424
NMEA,$GAGSV,3,2,11,24,71,044,46,28,38,123,39,36,22,290,35,08,05,052,25,7*72,1772048698424
NMEA,$GAGSV,3,3,11,21,16,199,30,,,,,,,,,7*4E,1772048698424
NMEA,$GBGSV,5,1,18,06,43,172,47,07,61,088,49,08,29,214,43,14,17,283,38,4*76,1772048698424
NMEA,$GBGSV,5,2,18,19,52,318,46,22,34,127,41,24,44,063,44,28,08,351,32,4*7B,1772048698424
NMEA,$GBGSV,5,3,18,36,31,211,40,38,72,015,51,01,39,004,45,03,21,099,37,4*74,1772048698424
NMEA,$GBGSV,5,4,18,59,06,156,23,02,85,000,52,04,47,290,46,11,29,215,39,4*7D,1772048698424
NMEA,$GBGSV,5,5,18,60,15,334,30,,,,,,,,,4*48,1772048698424
NMEA,$GQGSV,1,1,02,193,62,050,48,194,45,215,45,1*73,1772048698424
NMEA,$GNDTM,W84,,0000.00000,N,00000.00000,E,0.000,W84*6F,1772048698424
```

---

### Sentence-by-Sentence Annotation

#### `$GNGGA` — Position Fix

```
$GNGGA,083012.00,1304.08720,N,07735.50990,E,1,14,0.4,958.7,M,-85.8,M,,*4A
        ||||||||  ||||||||||| |||||||||||||  | || ||| ||||| |  ||||| |
        |         |           |              | |  |   |     |  |     Checksum
        |         |           |              | |  |   |     |  Geoid sep unit (M)
        |         |           |              | |  |   |     Geoid separation: -85.8 m
        |         |           |              | |  |   MSL altitude: 958.7 m
        |         |           |              | |  HDOP: 0.4 (outstanding)
        |         |           |              | Satellites used: 14
        |         |           |              Fix quality: 1 (standard GPS fix)
        |         |           Longitude: 077°35.50990'E = 77.5918°E
        |         Latitude: 13°04.08720'N = 13.0682°N
        UTC time: 08:30:12.00
```

Altitude interpretation:
```
MSL altitude    =  958.7 m    (above geoid / mean sea level)
Geoid sep (N)   = −85.8 m     (EGM2008 at this location; geoid below WGS-84 ellipsoid)
Ellipsoidal h   =  958.7 + (−85.8) =  872.9 m   (above WGS-84 ellipsoid)
```

---

#### `$GNRMC` — Minimum Navigation

```
$GNRMC,083012.00,A,1304.08720,N,07735.50990,E,0.0,,100326,1.1,W,A,V*62
                 |                            |   ||       ||| |  | Nav status
                 |                            |   ||       ||| |  Mode: A=Autonomous
                 |                            |   ||       ||| Magnetic variation: 1.1°W
                 |                            |   ||       Date: 10 Mar 2026
                 |                            |   |True course: blank (stationary)
                 |                            |   Speed: 0.0 knots
                 |                            Longitude 77.5918°E
                 Status: A = Active (valid fix)
```

Magnetic variation 1.1°W means true North is 1.1° to the right of compass North at
this location. A bearing of 90.0° compass = 90.0 − 1.1 = 88.9° true.

---

#### `$GNGNS` — Multi-Constellation Fix

```
$GNGNS,083012.00,1304.08720,N,07735.50990,E,AAAAAN,20,0.4,958.7,-85.8,,,V*1D
                                             ||||||
                                             |||||+-- NavIC:    N = not used
                                             ||||+--- QZSS:     A = autonomous fix
                                             |||+---- BeiDou:   A = autonomous fix
                                             ||+----- Galileo:  A = autonomous fix
                                             |+------ GLONASS:  A = autonomous fix
                                             +------- GPS:      A = autonomous fix
```

All five active constellations (GPS, GLONASS, Galileo, BeiDou, QZSS) contributing
to a combined autonomous fix using 20 satellites. NavIC not used.

---

#### `$GNVTG` — Speed and Course

```
$GNVTG,,T,,M,0.0,N,0.0,K,A*3D
        ||  ||  ||| |||
        ||  ||  ||| 0.0 km/h
        ||  ||  0.0 knots
        ||  Magnetic course: blank (stationary)
        True course: blank (stationary)
```

Zero speed in both knots and km/h confirms the receiver was stationary.
Course fields are blank because heading is undefined when not moving.

---

#### `$GNGSA` — Active Satellites (5 sentences for 5 constellations)

```
$GNGSA,A,3,23,18,14,08,10,27,,,,,,,0.6,0.4,0.5,1*3D   ← GPS (SysID=1): 6 SVs
$GNGSA,A,3,09,16,75,82,,,,,,,,,0.6,0.4,0.5,2*32        ← GLONASS (SysID=2): 4 SVs
$GNGSA,A,3,19,07,28,36,24,,,,,,,0.6,0.4,0.5,3*31       ← Galileo (SysID=3): 5 SVs
$GNGSA,A,3,06,14,22,36,38,08,07,,,,0.6,0.4,0.5,4*1A    ← BeiDou (SysID=4): 7 SVs
$GNGSA,A,3,193,194,,,,,,,,,,,0.6,0.4,0.5,5*34          ← QZSS (SysID=5): 2 SVs
```

Combined: 6+4+5+7+2 = **24 satellites used in the fix**.
DOP values consistent across all five sentences (PDOP=0.6, HDOP=0.4, VDOP=0.5).
HDOP=0.4 is outstanding — the satellite constellation spans the full sky.

GLONASS SVIDs 75 and 82 = NMEA IDs; convert to orbital slots: 75−64=11, 82−64=18.
QZSS SVIDs 193 and 194 = NMEA IDs for J01 and J02.

---

#### `$GPGSV` — GPS Satellites in View (3 sentences, 12 SVs)

```
$GPGSV,3,1,12,08,12,287,34,10,38,012,41,18,47,139,45,23,31,059,42,1*6B
       | | ||  || || |||  ||  || |||  ||  || |||  ||  || |||  ||  |
       | | ||  |satellite: PRN08, elev=12°, az=287°, CN0=34  | Signal ID=1 (L1 C/A)
       | | ||  |                  satellite: PRN10, elev=38°, az=012°, CN0=41
       | | ||  |                             satellite: PRN18, elev=47°, az=139°, CN0=45
       | | ||  |                                        satellite: PRN23, elev=31°, az=059°, CN0=42
       | | |Total GPS sats in view: 12
       | | Msg 1 of 3
       | 3 total messages
```

PRN08 at 12° elevation has CN0=34 — lower elevation means longer atmospheric path,
hence weaker signal than PRN18 at 47° elevation (CN0=45). This is the expected pattern.
PRN18 and PRN24 (CN0=48, from msg 2) are the strongest signals — both high elevation.

---

#### `$GLGSV` — GLONASS Satellites in View (2 sentences, 6 SVs)

```
$GLGSV,2,1,06,09,28,213,35,16,41,095,40,75,52,031,43,82,19,277,37,1*72
                  ||  ||  |||  ||  ||  |||  ||  ||  |||  ||  ||  |||  ||
                  R09,28°,213°,35 R16,41°, 95°,40 R75→R11,52°,31°,43 R82→R18,19°,277°,37
```

Note GLONASS NMEA IDs: 75 = slot 11, 82 = slot 18. Slot 11 at 52° elevation
has CN0=43, the highest GLONASS signal — consistent with short zenith path length.
Slot 18 at only 19° elevation has CN0=37, weakest of the four shown.

---

#### `$GBGSV` — BeiDou Satellites in View (5 sentences, 18 SVs)

```
$GBGSV,5,3,18,...,38,72,015,51,...,4*74
                   ||  ||  |||  ||
                   BeiDou B38 at elevation 72°, azimuth 015°, CN0=51 dB-Hz
```

BeiDou C38 is an MEO satellite at very high elevation (72°). CN0=51 dB-Hz approaches
the theoretical maximum for L1 C/A (~53–55 dBHz) — this is an exceptionally strong
measurement, confirming open-sky conditions with the satellite nearly overhead.

BeiDou C02 in sentence 4: elevation 85° (nearly zenith), CN0=52 dBHz. GEO/IGSO
satellites remain at quasi-fixed positions, providing stable high-CN0 signals
continuously from Asia-Pacific locations.

Signal ID=4 throughout — BeiDou B1C (1575.42 MHz). A session tracking B1I would
have separate GSV sentences with Signal ID=1.

---

#### `$GQGSV` — QZSS Satellites in View

```
$GQGSV,1,1,02,193,62,050,48,194,45,215,45,1*73
              ||  ||  |||  ||  ||  |||  ||
              J01,62°,050°,48  J02,45°,215°,45
```

QZSS J01 (SVID 193) at 62° elevation, CN0=48 — the quasi-zenith inclined orbit means
J01 is well above the horizon from Asia. J02 (SVID 194) at 45°, CN0=45.
Both used in fix (confirmed by the GSA sentence listing 193 and 194).

---

### Coordinate Conversion Worked Example

```
GGA latitude:   1304.08720,N
GGA longitude:  07735.50990,E
```

**Step 1 — Split degrees from minutes:**
```
Latitude:  DD = floor(1304.08720 / 100) = 13°
           MM = 1304.08720 − 1300 = 04.08720'
Longitude: DDD = floor(07735.50990 / 100) = 77°
           MM  = 07735.50990 − 7700 = 35.50990'
```

**Step 2 — Convert to decimal degrees:**
```
Lat  = 13 + 04.08720 / 60 = 13 + 0.068120 = 13.068120° N
Lon  = 77 + 35.50990 / 60 = 77 + 0.591832 = 77.591832° E
```

**Step 3 — Apply hemisphere sign:**
```
N → positive latitude:   +13.068120°
E → positive longitude:  +77.591832°
```

---

### Checksum Verification Example

Sentence: `$GNGGA,083012.00,...*4A`

The checksum covers everything between `$` and `*` (exclusive of both):
```
data = "GNGGA,083012.00,1304.08720,N,07735.50990,E,1,14,0.4,958.7,M,-85.8,M,,"
chk  = 0
for c in data:
    chk ^= ord(c)
# chk = 0x4A = 74 decimal
assert f"{chk:02X}" == "4A"   # ✓
```

If the computed checksum does not match the transmitted `*XX`, the sentence was
corrupted in transit and should be discarded.
