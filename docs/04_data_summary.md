# Physical Interpretation Guide — How to Read a Data Summary

This document explains how to interpret the `LogN/04_data_summary.md` file produced
for each log. It describes what each section means physically, how the numbers relate
to real-world signal conditions, and what values to expect for a typical open-sky
recording.

For per-log data, see:
- `docs/LogN/04_data_summary.md` — physical interpretation for that specific log
- `docs/LogN/05_gnss_quality_report.md` — 41-check quality scorecard for that log

---

## Section 1 — Recording at a Glance

The summary table at the top captures device metadata and session basics:

| Field | How to interpret |
|-------|-----------------|
| **Device / Chipset** | Identifies the hardware. Two key chipset families appear in this project: Qualcomm MPSS.HI (modem-integrated; higher BiasUncNanos) and Qualcomm MPSS.DE (dedicated; lower BiasUncNanos). |
| **Date / Time (UTC and IST)** | UTC time is from the GNSS timescale; IST = UTC + 5:30. The time determines satellite geometry (which satellites are above the horizon and at what elevation). Same location at different times of day gives different DOP. |
| **Duration** | Longer sessions give more epochs, more measurements, and more statistically robust quality metrics. Google recommends ≥ 60 s; 120–300 s is ideal. |
| **Epochs** | Number of 1-second measurement intervals. Should match duration in seconds. If epochs < duration, there are gaps. |
| **Location** | Latitude/longitude affect visible constellation composition (e.g. BeiDou has more GEO/IGSO satellites visible from Asia; QZSS visible from Asia-Pacific only). |
| **Altitude MSL** | From NMEA GGA. Higher altitude → lower atmospheric pressure → slightly smaller tropospheric delay. |
| **Altitude WGS-84** | Ellipsoidal altitude = MSL altitude + geoid separation. This is what appears in the Fix rows of the `.txt` file. |
| **Geoid separation** | EGM2008 geoid model correction. Varies by location (typical range: −107 to +85 m). For the Indian subcontinent: typically −50 to −90 m (geoid below ellipsoid). |

---

## Section 2 — Location

### Why Location Matters for GNSS

The recording location determines:
1. **Visible satellites** — only satellites above the horizon (~5° elevation minimum)
   contribute measurements.
2. **Ionospheric delay** — latitude affects the TEC (Total Electron Content) and the
   diurnal ionospheric cycle. Low latitudes and daytime hours have higher TEC.
3. **Geoid separation** — affects the relationship between MSL and ellipsoidal altitude.
4. **Constellation visibility** — BeiDou has dense Asia-Pacific coverage; QZSS provides
   Japan/Asia augmentation; Galileo gives good global coverage except high-polar regions.

### Cross-log Comparison

When comparing across logs from the same device at the same site:
- Latitude/longitude differences < 0.001° (< 100 m) indicate essentially the same location.
- MSL altitude differences ≤ 10 m are within expected GNSS vertical noise for a
  stationary single-frequency receiver.
- Geoid separation differences at the same location should be < 0.5 m (model is stable).

---

## Section 3 — Sky Environment

### Constellations Tracked

| Constellation | Expected SVs (mid-latitude open sky) | Notes |
|--------------|--------------------------------------|-------|
| GPS | 8–12 | ~31 active satellites; global coverage |
| GLONASS | 5–8 | ~24 active satellites; polar-orbit emphasis |
| Galileo | 6–10 | ~30 active satellites; global, excellent for Europe/Asia |
| BeiDou | 8–16 | ~50+ active satellites; best Asia-Pacific coverage; includes GEO/IGSO |
| QZSS | 1–4 | Regional augmentation for Japan/Asia-Pacific |
| NavIC | 0–7 | Regional system; visible from Indian subcontinent only |

More constellations = more satellites = better DOP, more redundant measurements, and
greater ability to detect/exclude faulty measurements (RAIM).

### BeiDou Signals (B1I vs B1C)

BeiDou satellites broadcast on two civil L-band frequencies:
- **B1I** — 1561.098 MHz. The original BDS-2/BDS-3 civil signal.
- **B1C** — 1575.42 MHz. New BDS-3 signal on the same frequency as GPS L1/Galileo E1.

Whether a given Android session sees B1I, B1C, or both depends on the chipset HAL
state at session start — it can vary between sessions on the same device at the same
location. When both are present, a dual-frequency BeiDou iono combination is available.

### Satellite Geometry — DOP

HDOP (Horizontal DOP) is reported per epoch in NMEA GSA sentences.

| HDOP | Geometric quality |
|------|------------------|
| < 0.5 | Outstanding — satellites spread uniformly around the sky |
| 0.5 – 1.0 | Excellent — typical best-case open sky |
| 1.0 – 1.5 | Good — acceptable for navigation |
| 1.5 – 2.5 | Moderate — reduced geometry; some sky blockage |
| > 2.5 | Poor — significant obstruction or very few satellites |

Constant HDOP across all epochs (e.g. 0.4 for all 120 epochs) is normal and expected
for a stationary receiver with continuous multi-constellation tracking — the sky geometry
evolves slowly (satellites move ~0.5°/min) and typically does not produce noticeable
HDOP changes over a 2-minute session.

---

## Section 4 — Signal Quality

### CN0 (Carrier-to-Noise Density)

CN0 is the primary per-satellite signal quality metric, in dB-Hz.

| CN0 range | Quality | Typical cause |
|-----------|---------|---------------|
| < 20 dBHz | Poor | Heavy obstruction, severe multipath, or low elevation |
| 20–25 dBHz | Moderate | Partial sky blockage, indoor, or high elevation noise |
| 25–35 dBHz | Good | Open sky, mid-elevation satellite |
| 35–45 dBHz | Excellent | Open sky, high elevation, dedicated GNSS chipset |
| > 45 dBHz | Outstanding | Near-zenith satellite on excellent chipset (≤55 dBHz theoretical limit) |

**Mean CN0:** The average across all raw measurements. Dominated by low-elevation signals
if many satellites are tracked. More informative when broken down by constellation or elevation.

**CN0 Top-4 per epoch:** The Google quality framework uses the mean of the top-4 CN0
values per epoch as the primary signal quality check (threshold ≥ 40 dBHz). This reduces
the influence of weak low-elevation signals and measures the chip's best achievable CN0.

### BiasUncertaintyNanos

The 1-sigma uncertainty on the receiver's hardware clock bias. Critically determines
how accurately the receiver knows its own time reference:

| Value | Chipset class | Impact |
|-------|---------------|--------|
| 2–10 ns | Dedicated GNSS modem (MPSS.DE) | Excellent; standard 40 ns threshold fine |
| 10–40 ns | Tensor G-series, some MediaTek | Good; standard 40 ns threshold fine |
| 40–200 ns | Modem-integrated (MPSS.HI) | Requires relaxed threshold (200 ns) |
| > 200 ns | Very old/integrated chipsets | Effectively no timing reference |

### ADR State (Carrier Phase)

The `AccumulatedDeltaRangeState` bitmask determines whether carrier-phase measurements
are valid. Two common states seen on Android:

| State | Meaning | Impact on positioning |
|-------|---------|----------------------|
| 0 (`ADR_STATE_UNKNOWN`) | No carrier phase tracking at all | Cannot do carrier-phase-based positioning |
| 1 (`ADR_STATE_VALID`) | Carrier phase valid — continuous tracking | Enables RTK, PPP, DGNSS |
| 16 (`ADR_STATE_HALF_CYCLE_REPORTED`) | Chip tracks phase internally; HAL does not certify it | Effectively 0% valid ADR |

State = 16 is common on Sony/Qualcomm MPSS.DE devices — the hardware computes phase
but the HAL driver does not set the VALID flag. A firmware or HAL update would be required
to expose valid carrier phase.

---

## Section 5 — Position Accuracy

### Reported Horizontal Accuracy (Hacc)

The `AccuracyMeters` field in Fix rows is the chipset's own estimate of its 68th-percentile
(1-sigma) horizontal accuracy. This is a **self-reported** value — its reliability depends
on the chipset's internal error model.

| Hacc range | Quality |
|------------|---------|
| < 2 m | Excellent (possible with DGNSS/RTK) |
| 2–5 m | Very good (typical MPSS.DE with good sky) |
| 5–10 m | Good (typical open-sky single-frequency) |
| 10–20 m | Moderate (restricted sky or weaker chipset) |
| > 20 m | Poor |

### Fix Scatter (for Stationary Receiver)

When the receiver is stationary, the spread of position fixes over time directly measures
the noise of the positioning system:
- **GPS scatter** — pure GNSS noise without sensor fusion
- **FLP scatter** — fused solution, often tighter than GPS alone if IMU aids

FLP scatter significantly smaller than GPS scatter → dead-reckoning/IMU aiding is active.
FLP scatter ≈ GPS scatter → minimal sensor fusion.

### Altitude Interpretation

GNSS vertical accuracy is typically 1.5–3× worse than horizontal accuracy due to satellite
geometry (all satellites are above the horizon — no "below" reference). Single-frequency
receivers have additional error from unmodelled ionospheric vertical delay.

---

## Section 6 — Motion

For a stationary receiver:
- `SpeedMps` in Fix rows should be 0.0 m/s (or < 0.1 m/s noise)
- NMEA `$GNVTG` should show 0.0 knots / 0.0 km/h throughout
- UncalAccel magnitude should equal local gravity (~9.8 m/s²) throughout
- UncalGyro values should be near zero

Any sustained speed > 0.5 m/s indicates the receiver was moving during the session.
Speed variations combined with PRR changes provide dead-reckoning capability.

---

## Section 7 — NMEA Sentence Inventory

The sentence count table verifies the completeness of NMEA output.

**Expected counts for a stationary session of N epochs:**

| Sentence | Expected count | Notes |
|----------|---------------|-------|
| `$GNGGA` | N | One per epoch |
| `$GNRMC` | N | One per epoch |
| `$GNGNS` | N | One per epoch |
| `$GNVTG` | N | One per epoch |
| `$GNDTM` | N | One per epoch |
| `$GNGSA` | 4N – 5N | One per active constellation per epoch (4–5 constellations typical) |
| `$GPGSV` | 2N – 4N | Depends on GPS SVs in view (ceiling(nGPS/4) per epoch) |
| `$GLGSV` | 1N – 2N | Depends on GLONASS SVs in view |
| `$GAGSV` | 2N – 3N | Depends on Galileo SVs in view |
| `$GBGSV` | 4N – 10N | BeiDou often has most SVs; may double-count B1I + B1C |
| `$GQGSV` | 1N | Usually 1–2 QZSS SVs → 1 sentence per epoch |

Large discrepancies from expected counts can indicate:
- Fewer epochs than expected → recording stopped early or there are gaps
- Unexpectedly large `$GBGSV` count → both B1I and B1C are being reported per satellite

---

## Section 8 — RINEX Observables

The RINEX header declares which observables are recorded per constellation. Key things
to check:

### Observation types per system

```
G    3 C1C D1C S1C    (GPS: L1 pseudorange, Doppler, CN0)
R    3 C1C D1C S1C    (GLONASS: L1)
J    3 C1C D1C S1C    (QZSS: L1)
C    3 C2I D2I S2I    (BeiDou: B1I only)
C    6 C1P D1P S1P C2I D2I S2I   (BeiDou: B1C + B1I dual-frequency)
E    3 C1C D1C S1C    (Galileo: E1)
```

| Obs code | Signal | Frequency |
|----------|--------|-----------|
| `C1C` | L1 C/A (GPS/GLO/GAL/QZSS) | 1575.42 or 1602+k×0.5625 MHz |
| `C2I` | BeiDou B1I | 1561.098 MHz |
| `C1P` | BeiDou B1C pilot | 1575.42 MHz |
| `D__` | Doppler (Hz, negative = approaching) | Same band as C__ |
| `S__` | Signal strength (CN0 in dB-Hz) | Same band as C__ |

**Dual-frequency combinations:**

| Combination | Purpose |
|-------------|---------|
| GPS L1 + L5 | Iono-free pseudorange (eliminates ~99% of ionospheric error) |
| BeiDou B1C + B1I | Partial iono correction (frequency separation ~14 MHz) |
| Galileo E1 + E5a | Iono-free combination |
| GLONASS L1 only | No second frequency available on most Android HALs |

### GLONASS Frequency Channels

The RINEX header lists each GLONASS satellite's FDMA channel number:
```
GLONASS SLOT / FRQ #
R09 -2  R11  0  R12 -1  ...
```

Channel `k` → L1 frequency = `1602 + k × 0.5625` MHz. More channels → wider frequency
diversity → less susceptibility to frequency-selective interference.

---

## Section 9 — Cross-Log Comparison

When comparing multiple logs (same device, same location, different times):

| Metric | What a difference indicates |
|--------|----------------------------|
| CN0 mean | Sky conditions, time of day, satellite elevation distribution |
| CN0 top-4 | Chipset's best-case tracking performance |
| BiasUncNanos | Should be consistent for the same chipset; large changes may indicate thermal effects |
| HDOP | Satellite geometry at the time of recording |
| BDS B1I presence | Chipset HAL state at session start — can vary session-to-session |
| PRR residual std | Doppler noise; directly tracks CN0 (higher CN0 → lower PRR noise) |
| ADR validity | HAL firmware state — consistent within a chipset family |
| GPS L5 presence | Hardware support + HAL enabling |
| Quality score | Overall GNSS capability; limited by structural fails (no L5, no ADR) |

**Structural fails** (GPS L5 absent, ADR invalid) reflect hardware/HAL limitations that
do not change session-to-session. **Variable metrics** (CN0, HDOP, PRR noise) reflect
sky environment and time of day.
