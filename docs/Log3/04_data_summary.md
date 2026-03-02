# Physical Interpretation & Data Summary — Log 3

## Recording at a Glance

| Field | Value |
|-------|-------|
| Device | Sony XQ-GE54, Android 16, GnssLogger v3.1.1.2 |
| Chipset | Qualcomm MPSS.DE.9.0 |
| Date / time | 02 Mar 2026, 12:15:58 – 12:17:40 UTC (17:45:58 – 17:47:40 IST) |
| Duration | ~120 seconds |
| Epochs | 120 |
| Location | ~13.0682° N, 77.5918° E — Bangalore, India |
| Altitude (MSL) | 962.6 m |
| Altitude (WGS-84) | ~876.8 m |
| Geoid separation | −85.8 m |

---

## 1. The Location

Log 3 was recorded at nearly the same site as Log 2 — same latitude and
longitude to five decimal places — with an MSL altitude of 962.6 m vs 958.7 m
in Log 2, a difference of ~4 m that falls within GNSS vertical noise.

| Coordinate | Log 3 | Log 2 | Log 1 |
|-----------|-------|-------|-------|
| Latitude | 13.0682° N | 13.0682° N | 13.0667° N |
| Longitude | 77.5918° E | 77.5918° E | 77.5917° E |
| Altitude (MSL) | 962.6 m | 958.7 m | 921.7 m |
| Altitude (WGS-84) | 876.8 m | 872.9 m | 837.7 m |
| Geoid separation | −85.8 m | −85.8 m | −84.0 m |

---

## 2. Sky Environment

### Constellations

| System | SVs tracked | In raw meas | Avg/epoch |
|--------|:-----------:|:-----------:|:---------:|
| GPS | ~12 | ~11 | 11.00 |
| GLONASS | 7 | 7 | 7.00 |
| BeiDou (B1C) | ~9 | ~9 | 9.00 |
| Galileo | ~8 | ~8 | 8.00 |
| QZSS | ~2 | ~2 | 2.00 |
| **Total** | **~38–40 signals** | **37** | **37.00** |

**BeiDou B1C only:** Unlike Log 2, which tracked BeiDou on both B1I and B1C,
Log 3 records only the B1C signal (1575.42 MHz). The RINEX header confirms
`C 3 C1P D1P S1P` with no `C2I` entries. This means BDS contributes one
measurement per satellite per epoch rather than two, and the dual-frequency
BeiDou iono combination is not available for this session.

Why BDS B1I is absent in Log 3 despite being present in Log 2 (same device)
is unclear — possible causes include a different chipset mode, GNSS HAL state,
or background interference at the time of recording.

**GLONASS — 7 satellites (more than Log 2):** The RINEX GLONASS slot table
lists seven channels: R03 +5, R04 +6, R05 +1, R09 −2, R16 −1, R18 −3, R19 +3.
Log 2 tracked six. The wider channel spread (−3 to +6) provides a more
diverse FDMA frequency set, improving GLONASS geometry.

### Satellite Geometry (NMEA $GNGSA)

| DOP | Value | Rating |
|-----|------:|--------|
| HDOP | 0.4 | Outstanding — constant across all 120 epochs |

HDOP remained exactly 0.4 for every epoch — identical to Log 2 and consistent
with the same recording site and time-of-day providing similar sky geometry.

---

## 3. Signal Quality

### CN0 (Carrier-to-Noise Density)

| Metric | Log 3 | Log 2 | Log 1 |
|--------|------:|------:|------:|
| Mean CN0 (all raw) | **43.9 dBHz** | 38.1 dBHz | 23.4 dBHz |
| Max CN0 | **53.4 dBHz** | 50.9 dBHz | 31.8 dBHz |
| Top-4 avg per epoch | **51.1 dBHz** | 47.1 dBHz | 25.6 dBHz |

Log 3 shows the highest CN0 of all three sessions. The 53.4 dBHz maximum
approaches the theoretical ceiling for consumer L1 C/A receivers (~53–55 dBHz),
indicating near-ideal open-sky conditions at the time of recording. The
improvement over Log 2 (recorded at the same site) is likely due to more
favourable satellite geometry and time-of-day ionospheric conditions.

### BiasUncertaintyNanos

| Metric | Value |
|--------|------:|
| Mean | 4.96 ns |
| Range | 4.46 – 5.69 ns |

Consistent with Log 2 (4.6 – 6.5 ns). The MPSS.DE.9.0 dedicated GNSS clock
architecture maintains sub-5 ns clock bias uncertainty — 19× better than the
Xiaomi 13's MPSS.HI chipset.

### ADR State = 16 — Half-Cycle Reported

All 4440 measurements carry `AccumulatedDeltaRangeState = 16`
(ADR_STATE_HALF_CYCLE_REPORTED, bit 4 set; ADR_STATE_VALID, bit 0, not set).
Identical behaviour to Log 2 — the Sony chipset computes carrier phase
internally but the HAL driver does not certify it as valid. ADR counts as 0%
valid in the quality framework.

---

## 4. Position Accuracy

### Fix Scatter (Stationary Receiver)

| Provider | Fixes | Reported Hacc |
|----------|------:|-------------:|
| GPS | 120 | 3.8 m |
| FLP | 121 | — |

Reported GPS horizontal accuracy is 3.8 m — constant across all 120 fixes and
identical to Log 2. The FLP (Fused Location Provider) scatter is negligible
(< 0.1 m), confirming the device was completely stationary.

### Altitude

| Source | Value |
|--------|------:|
| NMEA GGA (MSL) | 962.6 m |
| Geoid separation | −85.8 m |
| WGS-84 (derived) | 876.8 m |

The altitude is 4 m higher than Log 2 (958.7 m) and 41 m higher than Log 1
(921.7 m). The 4 m difference from Log 2 at the same lat/lon is within normal
GNSS vertical noise for a single-frequency receiver.

---

## 5. Motion

Speed from all providers: **0.000 m/s** throughout. The device was completely
stationary, confirmed by NMEA $GNVTG showing 0.0 knots and 0.0 km/h for all
120 epochs.

---

## 6. NMEA Sentence Inventory

| Sentence | Count | Note |
|----------|------:|------|
| $GBGSV | 960 | BeiDou sats in view (~8 SVs × ~8 msg/epoch × 120 epochs) |
| $GNGSA | 600 | 5 sentences/epoch × 120 epochs |
| $GPGSV | 480 | GPS sats in view |
| $GLGSV | 240 | GLONASS sats in view (7 SVs, 2 msg/epoch) |
| $GAGSV | 240 | Galileo sats in view |
| $GQGSV | 120 | QZSS sats in view (2 SVs, 1 msg/epoch) |
| $GNVTG | 120 | Speed/course — 0.0 knots throughout |
| $GNDTM | 120 | Datum — WGS-84 |
| $GNRMC | 120 | Navigation minimum data |
| $GNGNS | 120 | Multi-constellation fix |
| $GNGGA | 120 | Primary position sentence |
| **Total** | **3240** | |

3240 sentences for 120 epochs. Fewer than Log 2 (3893 for 130 epochs)
primarily because Log 3 is 10 epochs shorter and has fewer BDS GSV messages
(B1C only, vs B1C + B1I in Log 2).

---

## 7. RINEX Differences vs Log 2

| Observable | Log 2 | Log 3 |
|-----------|-------|-------|
| BDS obs types | `C 6 C1P D1P S1P C2I D2I S2I` (B1C + B1I) | `C 3 C1P D1P S1P` (B1C only) |
| GLONASS channels | 6 (R09 R11 R12 R21 R22 R23) | **7** (R03 R04 R05 R09 R16 R18 R19) |
| Time of first obs | 07:19:34 UTC | 12:15:58 UTC |

The absence of BDS B1I in Log 3 means the dual-frequency BeiDou iono correction
(B1C + B1I combo) that was available in Log 2 is not possible for this session.

---

## 8. Comparison: All Logs

| Metric | Log 1 (Xiaomi 13) | Log 2 (Sony XQ-GE54) | Log 3 (Sony XQ-GE54) |
|--------|:-----------------:|:--------------------:|:--------------------:|
| Duration | 44 s | 129 s | 120 s |
| Raw measurements | 311 | 7181 | 4440 |
| Epochs | 45 | 130 | 120 |
| Mean CN0 | 23.4 dBHz | 38.1 dBHz | **43.9 dBHz** |
| CN0 top-4/epoch | 25.6 dBHz | 47.1 dBHz | **51.1 dBHz** |
| BiasUncertaintyNanos | 75–129 ns | 4.6–6.5 ns | **4.5–5.7 ns** |
| Reported GPS Hacc | 10.9 m | 3.8 m | 3.8 m |
| HDOP | 0.7 | 0.4 | 0.4 |
| BDS signals | B1I only | B1I + B1C | B1C only |
| GLONASS SVs | 3 | 6 | **7** |
| ADR state | 0 (none) | 16 (half-cycle) | 16 (half-cycle) |
| GPS L5 | Absent | Absent | Absent |
| Quality score (v2) | 9/26 (35%) | 18/27 (67%) | **17/26 (65%)** |

---

## 9. Summary

| Category | Key Finding |
|----------|------------|
| **Location** | Same Bangalore site as Log 2 (~4 m higher altitude) |
| **Signal environment** | Best CN0 of all three logs — 43.9 dBHz mean, 53.4 max |
| **Satellite geometry** | Outstanding (HDOP 0.4); 7 GLONASS SVs tracked |
| **Position accuracy** | 3.8 m reported Hacc — identical to Log 2 |
| **BeiDou** | B1C only (no B1I) — dual-freq iono correction not available |
| **Clock quality** | BiasUncertNanos 4.96 ns — consistent with Log 2 |
| **ADR** | Half-cycle reported (state=16) but not valid — same as Log 2 |
| **L5** | Absent — same limitation as Log 1 and Log 2 |
| **Device motion** | Completely stationary throughout 120-second session |
