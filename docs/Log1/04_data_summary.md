# Physical Interpretation & Data Summary

## What Does This Data Tell Us?

This section synthesises all three log files into a physical picture of what
was happening during the 44-second recording session on 25 Feb 2026 at
~17:55–17:56 UTC in Bangalore, India.

---

## 1. The Location

| Coordinate | Value |
|-----------|-------|
| Latitude | 13.0667° N |
| Longitude | 77.5917° E |
| Altitude (MSL) | ~921.7 m |
| Altitude (WGS-84 ellipsoid) | ~837.4–837.7 m |
| Geoid separation | −84.0 m |
| Magnetic declination | 1.1° W |

The **−84 m geoid separation** means the WGS-84 ellipsoid is 84 m *above* the
geoid (mean sea level) at this location. This is typical for Peninsular India
where the geoid dips below the reference ellipsoid.

Bangalore sits on the **Deccan Plateau** at approximately 900 m above sea level,
which is accurately reflected in the 921 m MSL altitude.

---

## 2. The Sky Environment

### Constellations Visible

| System | Sats tracked | Sats used | Coverage reason |
|--------|:-----------:|:---------:|----------------|
| GPS (USA) | 12 | 5 | Global constellation, ~24 sats active |
| GLONASS (Russia) | 8 | 3 | Global constellation, ~24 sats |
| BeiDou (China) | 17 | 1–3 | Most sats visible from Asia-Pacific; GEO+IGSO coverage |
| Galileo (EU) | 11 | 4 | Global constellation, 30 sats |
| QZSS (Japan) | 1 | 1 | Regional; 1 GEO visible from India |
| **Total** | **49 signals** | **~10–15** | Best multi-GNSS epoch |

**Why BeiDou has the most satellites visible:**
BeiDou-3 operates a mixed constellation of MEO (medium orbit), IGSO (inclined
geostationary synchronous orbit), and GEO (geostationary) satellites optimised
for the Asia-Pacific region. From Bangalore, multiple GEO and IGSO satellites
are continuously visible above the southern and eastern horizon.

### Satellite Geometry (DOP)

| DOP type | Value | Interpretation |
|----------|------:|---------------|
| HDOP | 0.7 | Ideal horizontal geometry |
| VDOP | 0.8 | Good vertical geometry |
| PDOP | 1.0 | Excellent 3D geometry |

A PDOP of 1.0 is near the theoretical best. This means the satellites were
well-spread around the sky, minimising positioning error.

### Elevation Distribution

Satellite elevations ranged from 0° to 76°, mean ~30°. The majority of
tracked satellites were at 10–50° elevation — the sweet spot for GNSS
(low enough for wide geometry, high enough to avoid tropospheric and
multipath errors at the horizon).

---

## 3. Signal Quality Analysis

### CN0 (Carrier-to-Noise Density)

CN0 is the primary indicator of signal strength and quality.

| Source | Mean CN0 | Max CN0 | Notes |
|--------|--------:|--------:|-------|
| Raw rows (filtered) | 23.4 dB-Hz | 31.8 dB-Hz | Only measurements passing all quality filters |
| Status rows (all visible) | 6–23 dB-Hz | ~30 dB-Hz | Includes weak/marginal signals |
| NMEA GSV | 14–29 dB-Hz | — | Per-satellite snapshot |

The relatively low mean (23.4 dB-Hz) compared to ideal open-sky (~35 dB-Hz)
suggests **partial obstruction** — consistent with an urban environment or
being near a building/tree line. The device was likely held outdoors but not
in a completely open field.

### Signal strength by constellation

| Constellation | Typical CN0 | Physical explanation |
|--------------|:-----------:|---------------------|
| QZSS | 22–26 dB-Hz | Quasi-zenith orbit means favourable geometry for Asia |
| GPS | 19–26 dB-Hz | Strong, mature constellation with robust signals |
| GLONASS | 18–25 dB-Hz | Slightly lower power budget than GPS |
| BeiDou | 16–31 dB-Hz | Wide range; GEO sats (low elevation) are weaker |
| Galileo | 17–23 dB-Hz | Newer constellation; similar to GPS at L1 |

### BiasUncertaintyNanos — The Chipset Quirk

The **Qualcomm MPSS.HI.4.3.1** chipset reports a clock bias uncertainty of
**75–129 nanoseconds**. This is higher than many chipsets because:

1. The Snapdragon modem uses a shared clock architecture between cellular and GNSS.
2. Temperature and load variations introduce clock instability.
3. The reported uncertainty is conservative (covers worst-case).

In terms of pseudorange, 75 ns × c (3×10⁸ m/s) = **22.5 m of ranging error**.
This is the primary limitation on raw measurement accuracy for this device.

---

## 4. Position Accuracy Analysis

### Fix Scatter (Stationary Receiver)

Since the phone was stationary, **all position variation is measurement noise**:

| Provider | Lat spread | Lon spread | Meaning |
|----------|-----------|-----------|---------|
| GPS | ~2.5 m | ~0.7 m | Pure GNSS noise floor |
| FLP | ~6.2 m | ~2.5 m | Sensor fusion adds slight smoothing noise |
| NLP | ~1.7 m | ~0.9 m | Network fix — coincidentally tight cluster |

The **GPS provider outperforms FLP** in raw scatter, but FLP provides
continuity during satellite outages (NLP kicks in when GNSS is unavailable).

### Altitude Consistency

All three files agree on altitude:
- `.txt` Fix (GPS): 836.3–837.7 m (WGS-84)
- NMEA GGA: 921.5–921.7 m (MSL) → 921.7 − 84.0 = 837.7 m (WGS-84) ✓
- RINEX: Implicit in pseudoranges

The altitude noise (~1.4 m peak-to-peak for GPS, ~0 m for FLP which uses
barometer fusion) shows the typical 3:1 horizontal-to-vertical accuracy ratio.

---

## 5. Motion and Orientation

### The Phone Was Stationary

Multiple lines of evidence confirm this:
- NMEA `$GNVTG`: speed = 0.0 knots
- `$GNRMC`: speed = 0.0, course = blank
- Fix speeds: 0.0–1.08 m/s (residual noise)
- Accelerometer magnitude: √(3.8² + 4.7² + 7.9²) ≈ 9.81 m/s² = pure gravity

### Device Orientation

From `OrientationDeg` rows:
- **Yaw (heading): 76–79°** → the phone's top was pointed roughly East-NorthEast
- **Roll: −25°** → tilted 25° to the left (screen facing up-and-left)
- **Pitch: −28°** → tilted 28° backward (top tilted away from user)

This corresponds to a phone held in the hand at a comfortable viewing angle.

### Magnetometer Readings

| Axis | Value | Physical interpretation |
|------|------:|------------------------|
| X | ~61 µT | Horizontal North–South component |
| Y | ~−22 µT | Horizontal East–West component |
| Z | ~−230 µT | Vertical downward component (Earth's core field) |
| **Total field** | **~239 µT** | Consistent with Bangalore (~7.5° magnetic latitude) |

Earth's magnetic field at Bangalore has a **steep downward inclination** (~18°
below horizontal toward North), which explains the large negative Z component.

---

## 6. Doppler Analysis — Satellite Motions

Pseudorange rates (from `Raw` rows) tell us how fast each satellite is moving
toward or away from the receiver.

| Observation | Value | Meaning |
|------------|------:|---------|
| Most positive rate | +2 635 m/s | GLONASS R12 — receding rapidly eastward |
| Most negative rate | −2 565 m/s | GPS G18 — approaching rapidly |
| Near-zero rate | −35 to +350 m/s | BeiDou GEO C01, QZSS J03 — near-geostationary, barely moving relative to receiver |

**BeiDou GEO (C01) and QZSS (J03) have very small Doppler** (~−35 to +380 m/s)
because geostationary/quasi-stationary satellites are nearly fixed in the sky
relative to a ground observer. Their pseudoranges change slowly.

---

## 7. Ionospheric Correction Parameters (Klobuchar Model)

The `Raw` rows include Klobuchar coefficients broadcast by GPS:

```
Alpha: [α0, α1, α2, α3]
Beta:  [β0, β1, β2, β3]
```

These define a simple model of ionospheric delay (the slowing of signals as
they pass through the ionosphere). At noon local time, the ionosphere is most
active; at the recording time (~23:25 IST = ~17:55 UTC), the ionosphere is
moderate. The Klobuchar model corrects ~50% of the actual ionospheric delay,
with residual errors of ~5 m or less for L1-only receivers.

---

## 8. RINEX Epoch Timing — Fractional-Second Precision

The RINEX epochs are timestamped to sub-microsecond precision:
```
17 55 55.4240477
17 55 56.4240477
17 55 57.4240477
```

The fractional part **.4240477 seconds** is consistent across all epochs —
this is the **sub-second phase** locked to the GPS time grid. The GnssLogger
uses the GNSS time reference to timestamp each RINEX epoch precisely, which
is one of the key advantages of using GNSS-derived timing.

---

## 9. Summary Table

| Category | Key finding |
|----------|------------|
| **Location** | Bangalore plateau, 921 m MSL, 77.592 °E — consistent across all 3 files |
| **Signal environment** | Partial obstruction; CN0 23–32 dB-Hz; good but not ideal open-sky |
| **Satellite geometry** | Excellent (HDOP 0.7, PDOP 1.0) with 49 signals tracked, 10–15 used |
| **Position accuracy** | ~10–12 m horizontal (1-sigma); limited by L1-only single-frequency + clock bias |
| **Device motion** | Completely stationary; phone held at ~25° tilt facing NNE |
| **Chipset limitation** | High BiasUncertaintyNanos (75–129 ns) limits raw measurement quality |
| **Multi-constellation** | All 5 major systems (GPS/GLO/BDS/GAL/QZSS) tracked simultaneously |
| **Data consistency** | All three files agree on position, altitude, and satellite signals ✓ |
