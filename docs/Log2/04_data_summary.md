# Physical Interpretation & Data Summary — Log 2

## Recording at a Glance

| Field | Value |
|-------|-------|
| Device | Sony XQ-GE54, Android 16, GnssLogger v3.1.1.2 |
| Chipset | Qualcomm MPSS.DE.9.0 |
| Date / time | 27 Feb 2026, 07:19:34 – 07:21:43 UTC (12:49:34 – 12:51:43 IST) |
| Duration | ~129 seconds |
| Epochs | 130 |
| Location | ~13.0682° N, 77.5918° E — Bangalore, India |
| Altitude (MSL) | 958.7 m |
| Altitude (WGS-84) | ~872.9 m |
| Geoid separation | −85.8 m |

---

## 1. The Location

The receiver was in Bangalore, India — approximately 160 m north of the Log1 recording
site (same district, slightly different floor/terrain), as seen from the latitude shift
13.0667° → 13.0682° N. The higher MSL altitude (958.7 m vs 921.7 m in Log1) reflects
either a different building floor or a nearby ridge.

| Coordinate | Log2 value | Log1 value |
|-----------|-----------|-----------|
| Latitude | 13.0682° N | 13.0667° N |
| Longitude | 77.5918° E | 77.5917° E |
| Altitude (MSL) | 958.7 m | 921.7 m |
| Altitude (WGS-84) | 872.9 m | 837.7 m |
| Geoid separation | −85.8 m | −84.0 m |

The slightly more negative geoid separation (−85.8 m vs −84.0 m) is consistent with a
small northward displacement; the EGM2008 geoid surface changes smoothly across Bangalore.

---

## 2. Sky Environment

### Constellations

| System | SVs tracked | In raw meas | Avg/epoch |
|--------|:-----------:|:-----------:|:---------:|
| GPS | 12 | 11 | 10.97 |
| GLONASS | 6 | 6 | 5.32 |
| BeiDou (B1I) | 25 | 25 | 17.38 |
| BeiDou (B1C) | (same SVs) | 25 | 9.84 |
| Galileo | 10 | 10 | 9.75 |
| QZSS | 2 | 2 | 1.98 |
| **Total** | **~55 signals** | **56** | **~55** |

**BeiDou dual-signal:** The Sony chipset tracks BeiDou on both B1I (1561.098 MHz,
the legacy civil signal) and B1C (1575.42 MHz, the newer civil pilot channel).
This means each BeiDou satellite contributes two independent measurements, nearly
doubling BeiDou's contribution to the position solution.

**QZSS:** Two QZSS satellites visible (vs one in Log1). QZSS-3 (GEO) and
QZSS-1 or QZSS-4 (quasi-zenith). The quasi-zenith satellite's high-elevation
pass improves vertical geometry over Asia.

### Satellite Geometry (NMEA $GNGSA)

| DOP | Value | Rating |
|-----|------:|--------|
| HDOP | 0.4 | Outstanding — near theoretical minimum |
| PDOP | (not parsed) | Inferred excellent from HDOP |

HDOP of 0.4 is exceptional, better than Log1's 0.7. More satellites at diverse
azimuths and elevations, including the second QZSS satellite near zenith,
dilute the horizontal position error to near-minimum.

### Elevation Distribution

Elevations range from 0° to 81° with a mean of ~32.6°. The higher maximum
(81° vs 76° in Log1) indicates at least one satellite very close to zenith —
likely a QZSS or high-elevation GPS satellite — further improving vertical geometry.

---

## 3. Signal Quality

### CN0 (Carrier-to-Noise Density)

| Metric | Value | vs Log1 |
|--------|------:|--------|
| Mean CN0 (all raw) | 38.1 dBHz | +14.7 dBHz better |
| Max CN0 | 50.9 dBHz | +19.1 dBHz better |
| Top-4 avg per epoch | 47.1 dBHz | +21.5 dBHz better |

The dramatic CN0 improvement (38 vs 23 dBHz mean) indicates the Sony was in
a much more open environment — likely outdoors with unobstructed sky view —
compared to Log1's partially obstructed site. The 50.9 dBHz maximum approaches
the theoretical maximum for consumer L1 C/A receivers (~51–53 dBHz).

### BiasUncertaintyNanos

The Sony MPSS.DE.9.0 chipset reports a clock bias uncertainty of **4.6–6.5 ns**
(mean 4.99 ns). This is:
- 19× smaller than the Xiaomi 13's 75–129 ns
- Well below Google's standard threshold of 40 ns
- Equivalent to only ~1.5 m of pseudorange uncertainty from clock alone

The MPSS.DE architecture (Snapdragon 8 Gen 2 modem) uses a dedicated GNSS
clock architecture with lower thermal noise and better isolation from the
cellular subsystem than the earlier MPSS.HI generation.

### ADR State = 16 — Half-Cycle Reported

All 7181 measurements carry `AccumulatedDeltaRangeState = 16` (0x10), which
decodes as **ADR_STATE_HALF_CYCLE_REPORTED** (bit 4). This means:

- The Sony chipset IS computing carrier phase internally
- The half-cycle ambiguity has been identified and applied to the ADR value
- However, **ADR_STATE_VALID** (bit 0) is not set → the measurement is not certified valid
- The v2 analysis framework therefore counts ADR as 0% valid

This is a step above Log1 (state = 0 = nothing at all). The Sony is on the
boundary: it exposes phase observables but with unresolved ambiguity flags.
A firmware update or different Android HAL version may enable full valid ADR.

---

## 4. Position Accuracy

### Fix Scatter (Stationary Receiver)

| Provider | Fixes | Lat spread | Lon spread | Reported Hacc |
|----------|------:|----------:|----------:|-------------:|
| GPS | 130 | ~0.0 m | ~0.0 m | 3.8 m |
| FLP | 131 | 0.1 m | 0.1 m | — |
| NLP | 17 | — | — | — |

**GPS provider accuracy is 3.8 m reported** — nearly 3× better than Log1's
10.9 m reported accuracy. This reflects the much lower BiasUncertaintyNanos
(4.9 vs 96 ns); Android's accuracy estimate directly incorporates this uncertainty.

FLP spread of 0.1 m is essentially zero — perfect stability over 129 seconds,
consistent with a stationary device and high-confidence sensor fusion.

### Altitude

| Source | Value |
|--------|------:|
| NMEA GGA (MSL) | 958.7 m |
| Geoid separation | −85.8 m |
| WGS-84 (derived) | 872.9 m |
| GPS fix (WGS-84) | 873.2 m ✓ |
| FLP (WGS-84) | 860.5–860.7 m |

The 12m discrepancy between GPS WLS altitude (873.2 m) and FLP altitude (860.6 m)
is normal: FLP uses barometer fusion which is referenced to a different baseline.
The GNSS-only and NMEA values agree to within 0.3 m, confirming consistency.

---

## 5. Motion and Orientation

Speed from all providers: **0.00–0.01 m/s** — the device was completely stationary.
This is confirmed by NMEA $GNVTG showing 0.0 knots and 0.0 km/h.

The slightly higher maximum speed (0.01 vs 0.0 m/s in Log1) is pure
pseudorange noise and not detectable motion.

---

## 6. NMEA Sentence Inventory

| Sentence | Count | Note |
|----------|------:|------|
| $GBGSV | 1293 | BeiDou sats in view (25 SVs × 5 msg/epoch × 130 epochs ≈ 1300 max) |
| $GNGSA | 650 | 5 sentences/epoch (one per constellation) × 130 epochs |
| $GPGSV | 520 | GPS sats in view |
| $GAGSV | 390 | Galileo sats in view |
| $GLGSV | 260 | GLONASS sats in view |
| $GQGSV | 130 | QZSS sats in view (1 msg/epoch since only 2 sats) |
| $GNVTG | 130 | Speed/course — 0.0 knots throughout |
| $GNDTM | 130 | Datum — WGS-84 |
| $GNRMC | 130 | Navigation minimum data |
| $GNGNS | 130 | Multi-constellation fix |
| $GNGGA | 130 | Primary position sentence |
| **Total** | **3893** | |

The 3893 NMEA sentences for 130 epochs (vs 1073 sentences for 45 epochs in Log1)
reflects the longer session and the extra BeiDou GSV messages.

---

## 7. RINEX Differences vs Log1

The Log2 RINEX file reveals an important upgrade in the Sony chipset:

```
C    6 C1P D1P S1P C2I D2I S2I     (BeiDou — 6 obs types)
G    3 C1C D1C S1C                  (GPS — 3 obs types, same as Log1)
```

**BeiDou records 6 observables per satellite per epoch:**

| Code | Signal | Description |
|------|--------|-------------|
| C1P | B1C (pilot) | Pseudorange on 1575.42 MHz (CDMA, same as GPS L1) |
| D1P | B1C | Doppler on B1C |
| S1P | B1C | CN0 on B1C |
| C2I | B1I | Pseudorange on 1561.098 MHz (legacy civil) |
| D2I | B1I | Doppler on B1I |
| S2I | B1I | CN0 on B1I |

This means the Sony can form a **BeiDou dual-frequency combination** (B1C + B1I),
partially reducing BeiDou ionospheric error even without GPS L5.

**GLONASS channels (6 satellites):**
```
R09 -2,  R11  0,  R12 -1,  R21  4,  R22 -3,  R23  3
```
More GLONASS satellites (6 vs 3 in Log1) with a wider spread of frequency
channels (−3 to +4 vs −4 to 0 in Log1), improving GLONASS geometry.

---

## 8. Comparison: Log1 vs Log2

| Metric | Log1 (Xiaomi 13) | Log2 (Sony XQ-GE54) |
|--------|:----------------:|:-------------------:|
| Duration | 44 s | 129 s |
| Raw measurements | 311 | 7181 |
| Epochs | 45 | 130 |
| Mean CN0 | 23.4 dBHz | 38.1 dBHz |
| BiasUncertaintyNanos | 75–129 ns | 4.6–6.5 ns |
| Reported GPS Hacc | 10.9 m | 3.8 m |
| HDOP | 0.7 | 0.4 |
| BDS signals/epoch | ~1.6 (B1I only) | 17.4 B1I + 9.8 B1C |
| ADR state | 0 (none) | 16 (half-cycle, not valid) |
| GPS L5 | Absent | Absent |
| NMEA sentences | 1073 | 3893 |
| Quality score (v2) | 9/26 (35%) | 18/27 (67%) |

---

## 9. Summary

| Category | Key Finding |
|----------|------------|
| **Location** | Same Bangalore plateau, ~37 m higher and ~160 m north of Log1 site |
| **Signal environment** | Excellent open-sky; CN0 38 dBHz mean — no obstruction |
| **Satellite geometry** | Outstanding (HDOP 0.4); 55+ signals tracked including 2 QZSS |
| **Position accuracy** | 3.8 m reported Hacc (GPS); FLP scatter 0.1 m |
| **BeiDou dual-signal** | B1C + B1I both tracked — unique to this Sony chipset version |
| **Clock quality** | BiasUncertNanos 4.9 ns — excellent, 19× better than Log1 |
| **ADR** | Half-cycle reported (state=16) but not valid; no cm-level positioning |
| **L5** | Absent — same limitation as Log1 |
| **Device motion** | Completely stationary throughout 129-second session |
