# File 2 — NMEA 0183 Log (`gnss_log_*.nmea`)

## What Is This File?

This file contains **NMEA 0183** sentences — the universal, human-readable
standard for GPS receivers, developed by the National Marine Electronics
Association. Every line is prefixed with `NMEA,` and ends with a Unix
timestamp (ms) added by GnssLogger.

Format of each line:
```
NMEA,<sentence>,<utcTimeMillis>
```

The examples and statistics below are drawn from **Log 1 (Xiaomi 13, 44 s,
45 epochs, 1 073 sentences)**. See the "Log2 Differences" section at the end
for how Log 2 (Sony XQ-GE54, 129 s, 130 epochs, 3 893 sentences) compares.
One complete "epoch" of NMEA output (all sentence types for one position fix)
is emitted roughly **every 1 second**.

---

## Sentence Type Inventory

| Sentence | Count | Purpose |
|----------|------:|---------|
| `$GBGSV` | 225 | BeiDou satellites in view |
| `$GNGSA` | 218 | Active satellites used in fix (all constellations) |
| `$GPGSV` | 135 | GPS satellites in view |
| `$GAGSV` | 135 | Galileo satellites in view |
| `$GLGSV` | 90 | GLONASS satellites in view |
| `$GQGSV` | 45 | QZSS satellites in view |
| `$GNVTG` | 45 | Speed and course over ground |
| `$GNDTM` | 45 | Datum reference |
| `$GNRMC` | 45 | Recommended minimum navigation data |
| `$GNGNS` | 45 | Multi-constellation fix data |
| `$GNGGA` | 45 | Global fix data (the primary position sentence) |
| **Total** | **1 073** | |

---

## Sentence Prefixes Explained

NMEA 0183 (version 4.11) uses a two-letter talker ID:

| Prefix | Talker |
|--------|--------|
| `GP` | GPS only |
| `GL` | GLONASS only |
| `GA` | Galileo only |
| `GB` | BeiDou only |
| `GQ` | QZSS only |
| `GN` | Multiple constellations (combined) |

---

## Sentence-by-Sentence Reference

### `$GNGGA` — Global Positioning System Fix Data (45 sentences)

This is the **most important NMEA sentence** — it gives the full position fix.

Example:
```
$GNGGA,175538.00,1304.004606,N,07735.500621,E,1,12,0.7,921.7,M,-84.0,M,,*53
```

| Field | Example | Meaning |
|-------|---------|---------|
| Time | `175538.00` | UTC time: 17h 55m 38.00s |
| Latitude | `1304.004606,N` | 13° 04.004606' N = **13.066743° N** |
| Longitude | `07735.500621,E` | 077° 35.500621' E = **77.591677° E** |
| Fix quality | `1` | 1 = GPS fix, 2 = DGPS, 4 = RTK fixed, 5 = RTK float |
| Satellites | `12` | Number of satellites used in this fix |
| HDOP | `0.7` | Horizontal Dilution of Precision (lower = better geometry; <1 excellent) |
| Altitude | `921.7,M` | Altitude above mean sea level in metres |
| Geoid separation | `-84.0,M` | Height of geoid above WGS-84 ellipsoid. **Negative here** means the geoid is 84 m below the ellipsoid at this location. Therefore the WGS-84 ellipsoidal height = 921.7 + (−84.0) = **837.7 m** (matches the `.txt` Fix rows). |
| Checksum | `*53` | XOR checksum for integrity |

**Physical meaning:** The receiver is at 13.0667° N, 77.5917° E at ~922 m AMSL
(~838 m above the WGS-84 ellipsoid) with 12 satellites and excellent geometry
(HDOP 0.7).

---

### `$GNRMC` — Recommended Minimum Navigation Data (45 sentences)

Example:
```
$GNRMC,175538.00,A,1304.004606,N,07735.500621,E,0.0,,250226,1.1,W,A,V*65
```

| Field | Example | Meaning |
|-------|---------|---------|
| Time | `175538.00` | UTC time |
| Status | `A` | A = Active (valid fix), V = Void (invalid) |
| Latitude | `1304.004606,N` | Position |
| Longitude | `07735.500621,E` | Position |
| Speed over ground | `0.0` | Speed in knots (0 = stationary) |
| Course | (blank) | True heading; blank because stationary |
| Date | `250226` | 25 February 2026 |
| Magnetic variation | `1.1,W` | Local magnetic declination = 1.1° West |
| Mode | `A` | A = Autonomous, D = Differential |
| Nav status | `V` | V = non-precise (no RAIM); A = precise |

The **magnetic declination of 1.1° W** at Bangalore means compass North is 1.1°
to the right of true North at this location.

---

### `$GNGNS` — Multi-Constellation Fix Data (45 sentences)

Example:
```
$GNGNS,175538.00,1304.004606,N,07735.500621,E,AAAAAN,15,0.7,921.7,-84.0,,,V*0B
```

| Field | Example | Meaning |
|-------|---------|---------|
| Mode indicator | `AAAAAN` | One character per constellation (GPS/GLONASS/Galileo/BeiDou/QZSS/NavIC). A = Autonomous fix, N = not used. Here GPS, GLONASS, Galileo, BeiDou = Autonomous; QZSS = Autonomous; NavIC = N/A. |
| Satellites | `15` | Total satellites used |
| HDOP | `0.7` | Horizontal DOP |
| Altitude | `921.7` | MSL altitude (m) |
| Geoid sep. | `-84.0` | Geoid separation (m) |

---

### `$GNVTG` — Speed and Course Over Ground (45 sentences)

Example:
```
$GNVTG,,T,,M,0.0,N,0.0,K,A*3D
```

| Field | Meaning |
|-------|---------|
| `T` suffix | True course (blank = unknown because stationary) |
| `M` suffix | Magnetic course (blank) |
| `0.0,N` | Speed in knots = 0 |
| `0.0,K` | Speed in km/h = 0 |
| `A` | Mode = Autonomous |

Confirms the phone was **completely stationary** throughout the recording.

---

### `$GNGSA` — Active Satellites & DOP (218 sentences)

One GSA sentence per constellation per epoch. Example:
```
$GNGSA,A,3,08,18,23,25,27,,,,,,,,1.0,0.7,0.8,1*3D
```

| Field | Example | Meaning |
|-------|---------|---------|
| Mode | `A` | Auto-select 2D/3D |
| Fix type | `3` | 3 = 3D fix (1=no fix, 2=2D, 3=3D) |
| SVs | `08,18,23,25,27` | SVIDs of GPS satellites used |
| PDOP | `1.0` | Position Dilution of Precision |
| HDOP | `0.7` | Horizontal DOP |
| VDOP | `0.8` | Vertical DOP |
| System ID | `1` | 1=GPS, 2=GLONASS, 3=Galileo, 4=BeiDou, 5=QZSS |

**What DOP means:**

| DOP value | Rating |
|-----------|--------|
| < 1 | Ideal |
| 1 – 2 | Excellent |
| 2 – 5 | Good |
| 5 – 10 | Moderate |
| > 10 | Poor |

HDOP of 0.7 here is excellent — wide satellite spread in the sky means the
measurement geometry is very favourable for horizontal accuracy.

---

### GSV Sentences — Satellites in View

GSV sentences list every visible satellite with its signal strength, azimuth,
and elevation. Up to 4 satellites fit per sentence; multiple sentences cover
all visible satellites.

#### `$GPGSV` — GPS Satellites in View (135 sentences = 45 epochs × 3 sentences)

Example:
```
$GPGSV,3,1,12,08,12,287,14,10,37,010,15,18,41,139,21,23,30,059,25,1*6B
```

| Field group | Meaning |
|-------------|---------|
| `3,1,12` | 3 messages total, this is msg 1, 12 GPS sats in view |
| `08,12,287,14` | PRN 8 at elevation 12°, azimuth 287°, CN0 14 dB-Hz |
| `10,37,010,15` | PRN 10 at 37°, 010°, 15 dB-Hz |
| `18,41,139,21` | PRN 18 at 41°, 139°, 21 dB-Hz |
| `23,30,059,25` | PRN 23 at 30°, 059°, 25 dB-Hz |
| `1` | Signal ID (1 = L1 C/A) |

This log tracks **12 GPS satellites** per epoch, with elevations from 5° to 53°
and CN0 from 14 to 26 dB-Hz.

#### `$GLGSV` — GLONASS Satellites in View (90 sentences = 45 × 2)

Uses GLONASS slot numbers (65–88 in NMEA) offset from orbital slot numbers.
**8 GLONASS satellites** tracked per epoch.

#### `$GAGSV` — Galileo Satellites in View (135 sentences = 45 × 3)

**11 Galileo satellites** tracked. Galileo PRNs 1–36 as E-SVID.

#### `$GBGSV` — BeiDou Satellites in View (225 sentences = 45 × 5)

**17 BeiDou satellites** tracked — the most of any constellation. BeiDou (BDS-3)
has an extensive constellation of GEO + IGSO + MEO satellites, especially
well-positioned for Asia-Pacific.

#### `$GQGSV` — QZSS Satellites in View (45 sentences = 45 × 1)

**1 QZSS satellite** tracked (PRN 03, the MICHIBIKI-3 GEO satellite). QZSS is
Japan's regional augmentation system; it is visible from the Indian subcontinent
at low elevation (~22° here) due to its high-inclination quasi-zenith orbit.

---

### `$GNDTM` — Datum Reference (45 sentences)

Example:
```
$GNDTM,P90,,0000.000011,S,00000.000001,W,0.999,W84*44
```

Reports the local geodetic datum relative to WGS-84. `W84` = the output
coordinates are in WGS-84. The tiny offsets (0.000011°S, 0.000001°W, 0.999 m)
are essentially zero — no datum shift is applied.

---

## Summary of NMEA Physical Observations (Log1)

| Observation | Value | Interpretation |
|------------|-------|---------------|
| Fix quality | 1 (GPS fix) | Standard autonomous GNSS, not DGPS |
| Satellites used | 12–15 | Excellent multi-constellation coverage |
| HDOP | 0.7 | Ideal geometry |
| VDOP | 0.8 | Good vertical accuracy |
| Speed | 0.0 knots | Stationary |
| Altitude (MSL) | 921.5–921.7 m | Consistent; Bangalore plateau at ~920 m |
| Geoid separation | −84.0 m | Geoid is 84 m below WGS-84 ellipsoid here |
| Magnetic declination | 1.1° W | Standard for Bangalore in 2026 |
| BeiDou sats visible | 17 | Largest constellation seen — confirms Asia-Pacific benefit |

---

## Log2 Differences (Sony XQ-GE54, 27 Feb 2026, 130 epochs)

| Sentence | Log1 count | Log2 count | Note |
|----------|:----------:|:----------:|------|
| `$GBGSV` | 225 | **1 293** | 25 BDS SVs × 5 msg/epoch × 130 epochs |
| `$GNGSA` | 218 | **650** | 5 sentences/epoch (one per constellation) |
| `$GPGSV` | 135 | **520** | More GPS SVs tracked (12 → ~12–13, 4 msg) |
| `$GAGSV` | 135 | **390** | 3 sentences/epoch |
| `$GLGSV` | 90 | **260** | 6 GLONASS SVs (vs 8 tracked but fewer msgs) |
| `$GQGSV` | 45 | **130** | 2 QZSS SVs (Log1 had 1) |
| `$GNVTG` | 45 | 130 | 0.0 knots throughout |
| `$GNDTM` | 45 | 130 | WGS-84, same datum |
| `$GNRMC` | 45 | 130 | |
| `$GNGNS` | 45 | 130 | |
| `$GNGGA` | 45 | 130 | |
| **Total** | **1 073** | **3 893** | |

**Key Log2 NMEA differences vs Log1:**

- **`$GNGGA` altitude: 958.7 m MSL** (vs 921.7 m) — ~37 m higher recording site.
- **`$GNGGA` geoid separation: −85.8 m** (vs −84.0 m) — small northward shift in EGM2008.
- **`$GNGSA` HDOP: 0.4** (vs 0.7) — outstanding geometry with 55+ signals and 2 QZSS.
- **`$GBGSV`: 1 293 sentences** because 25 BDS SVs need 5 GSV messages per epoch
  (ceiling(25/4) = 7, but GnssLogger groups by frequency — the actual msg count
  is 1 293 / 130 ≈ 9.9 ≈ 10 per epoch for combined B1I+B1C reporting).
- **2 QZSS satellites** in `$GQGSV` vs 1 in Log1 — QZSS-3 (GEO) + QZSS-1 or
  QZSS-4 (quasi-zenith) were both visible during the Log2 session.
- **Fix quality remains 1** (autonomous GPS) — no DGPS correction source applied.
