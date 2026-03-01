# File 1 — GnssLogger CSV (`gnss_log_*.txt`)

## What Is This File?

This is the main log produced by the GnssLogger app. It is a plain-text
comma-separated file where every row begins with a **type tag** that identifies
which Android sensor or GNSS subsystem produced that measurement.
The file header (lines starting with `#`) lists the column definitions for every
row type.

The examples and statistics in this document are drawn from **Log 1 (Xiaomi 13,
Android 13, 44 seconds, 17:55 UTC 25 Feb 2026)**. See the "Log2 Differences"
section at the end for how Log 2 (Sony XQ-GE54) compares in this format.

---

## Row Types and Record Counts

| Row type | Count | Source |
|----------|------:|--------|
| `Raw` | 311 | GNSS chip — raw pseudorange measurements |
| `Status` | 2 205 | GNSS chip — satellite visibility & signal status |
| `Fix` | 95 | Android location API — computed position fixes |
| `UncalAccel` | 4 841 | Accelerometer (uncalibrated) |
| `UncalGyro` | 4 840 | Gyroscope (uncalibrated) |
| `UncalMag` | 4 523 | Magnetometer (uncalibrated) |
| `OrientationDeg` | 4 838 | Fused orientation sensor |
| `GameRotationVector` | ~4 800 | Rotation vector (no magnetic north) |

---

## 1. `Raw` Rows — Chip-Level GNSS Measurements

### What they represent
These are the **lowest-level GNSS observables** the phone chipset exposes to
Android. Each row is one measurement of one satellite signal at one moment in
time. They are the raw building blocks from which every navigation solution is
ultimately derived.

### Column-by-column explanation

| Column | Example | Meaning |
|--------|---------|---------|
| `utcTimeMillis` | 1772042137424 | Wall-clock time (Unix epoch ms, UTC) when the measurement was taken |
| `TimeNanos` | 6567086... | Hardware clock time in nanoseconds since the receiver was powered on |
| `LeapSecond` | 18 | Current GPS–UTC leap second offset (18 s as of 2026) |
| `TimeUncertaintyNanos` | 0.0 | Uncertainty on the hardware clock (0 = perfectly disciplined) |
| `FullBiasNanos` | –1772... ×10⁹ | Integer-nanosecond offset between hardware clock and GPS time |
| `BiasNanos` | 0.3... | Sub-nanosecond fractional part of the clock bias |
| `BiasUncertaintyNanos` | 75–129 | **1-sigma uncertainty on the clock bias** — this device reports 75–129 ns, which is high for a consumer chipset. The gnss-lib-py default threshold (40 ns) is relaxed to 200 ns to preserve measurements. |
| `DriftNanosPerSecond` | –0.06 | Clock frequency drift (nanoseconds per second) |
| `DriftUncertaintyNanosPerSecond` | 0.002 | 1-sigma uncertainty on the drift |
| `HardwareClockDiscontinuityCount` | 0 | Number of times the hardware clock has reset; non-zero means clock jumps occurred |
| `Svid` | 8 | Satellite vehicle ID within its constellation |
| `TimeOffsetNanos` | 0.0 | Sub-measurement time offset (usually 0) |
| `State` | 16431 | Bitmask of tracking-state flags (e.g., code-lock, bit-sync, sub-frame-sync, TOW-decoded) |
| `ReceivedSvTimeNanos` | 88233... | Satellite transmit time in nanoseconds (within GPS week) |
| `ReceivedSvTimeUncertaintyNanos` | 23–58 | 1-sigma uncertainty on the received satellite time |
| `Cn0DbHz` | 13.6–31.8 | **Carrier-to-Noise density** in dB-Hz. Higher = stronger signal. <25 is poor, 25–35 is typical, >35 is excellent. |
| `PseudorangeRateMetersPerSecond` | –2564 to +2635 | **Doppler-derived range rate** — the rate at which the distance between phone and satellite is changing. Used to compute velocity. |
| `PseudorangeRateUncertaintyMetersPerSecond` | 0.5–2.0 | 1-sigma uncertainty on the range rate |
| `AccumulatedDeltaRangeState` | bitmask | Flags for carrier-phase tracking (ADR valid, reset, cycle slip) |
| `AccumulatedDeltaRangeMeters` | varies | Integrated carrier phase (metres). Non-zero only if ADR is valid. |
| `AccumulatedDeltaRangeUncertaintyMeters` | varies | 1-sigma uncertainty on ADR |
| `CarrierFrequencyHz` | 1575420000 | Signal carrier frequency. 1575.42 MHz = GPS/Galileo/QZSS L1; 1602 MHz ± k×562.5 kHz = GLONASS L1; 1561.098 MHz = BeiDou B1I |
| `ConstellationType` | 1–6 | 1=GPS, 2=SBAS, 3=GLONASS, 4=QZSS, 5=BeiDou, 6=Galileo |
| `AgcDb` | varies | Automatic Gain Control level in dB — a proxy for interference/jamming; large negative = high interference |
| `BasebandCn0DbHz` | 10–29 | CN0 measured at baseband only (before correlator), generally lower than `Cn0DbHz` |
| `FullInterSignalBiasNanos` | varies | Inter-signal bias between this signal and GPS L1 reference |
| `SatelliteInterSignalBiasNanos` | varies | Satellite-reported inter-signal bias |
| `CodeType` | C | Signal code type: C=Civil (C/A), P=Precise, etc. |
| `SvPositionEcefXMeters` | varies | Satellite X position in ECEF frame (metres) |
| `SvPositionEcefYMeters` | varies | Satellite Y position in ECEF frame |
| `SvPositionEcefZMeters` | varies | Satellite Z position in ECEF frame |
| `SvVelocityEcefX/Y/ZMetersPerSecond` | varies | Satellite velocity in ECEF frame |
| `SvClockBiasMeters` | varies | Satellite clock error in metres (= clock bias × speed of light) |
| `SvClockDriftMetersPerSecond` | varies | Satellite clock drift rate in m/s |
| `KlobucharAlpha0–3 / Beta0–3` | varies | Ionospheric correction model coefficients broadcast in the GPS navigation message |

### How a pseudorange is computed

```
pseudorange = (ReceivedTime - SatelliteTransmitTime) × speed_of_light
```

Where:
- `ReceivedTime` = `TimeNanos – (FullBiasNanos + BiasNanos)` (GPS time at receiver)
- `SatelliteTransmitTime` = `ReceivedSvTimeNanos` (GPS time at satellite)

The raw pseudorange is ~20 000–40 000 km — the actual geometric distance plus
clock offsets and atmospheric delays.

### Constellation breakdown in this log

| Constellation | Filtered measurements | Typical CN0 |
|--------------|----------------------:|-------------|
| GPS | ~120 | 19–26 dB-Hz |
| GLONASS | ~60 | 18–25 dB-Hz |
| BeiDou | ~80 | 16–31 dB-Hz |
| Galileo | ~30 | 17–23 dB-Hz |
| QZSS | ~20 | 21–26 dB-Hz |

---

## 2. `Status` Rows — Satellite Visibility Status

### What they represent
One `Status` block is emitted per GNSS epoch (every ~1 second). Each block
contains one row **per visible satellite signal** (regardless of whether that
satellite is tracked or used in the fix). These rows come from the Android
`GnssStatus` API.

### Column explanations

| Column | Example | Meaning |
|--------|---------|---------|
| `UnixTimeMillis` | (often blank) | Epoch timestamp; may be empty if derived from system time |
| `SignalCount` | 49 | Total number of satellite signals in this epoch's snapshot |
| `SignalIndex` | 0–48 | Index of this signal within the epoch block |
| `ConstellationType` | 1 | 1=GPS, 3=GLONASS, 4=QZSS, 5=BeiDou, 6=Galileo |
| `Svid` | 8 | Satellite vehicle ID |
| `CarrierFrequencyHz` | 1575420000 | Signal frequency |
| `Cn0DbHz` | 13.6 | Signal strength (carrier-to-noise ratio) |
| `AzimuthDegrees` | 287.0 | Satellite azimuth from North (0–360°), clockwise |
| `ElevationDegrees` | 12.0 | Satellite elevation above horizon (0–90°) |
| `UsedInFix` | 1 | 1 = this satellite was used in the current position fix, 0 = tracked only |
| `HasAlmanacData` | 1 | Whether the receiver has almanac data for this satellite |
| `HasEphemerisData` | 0 | Whether the receiver has full ephemeris (precise orbit) data |
| `BasebandCn0DbHz` | 10.1 | Baseband-only CN0 |

### Satellite counts in this log

| Constellation | Signals tracked | Signals used in fix |
|--------------|----------------:|--------------------:|
| GPS | 540 epochs-signals | 197 |
| GLONASS | 360 | 113 |
| BeiDou | 765 | 55 |
| Galileo | 495 | 59 |
| QZSS | 45 | 43 |

Up to **49 signals** were tracked in a single epoch, with roughly **10 used in fix**.
Elevation angles ranged from 0° to 76° with a mean of ~30°.

---

## 3. `Fix` Rows — Android Position Fixes

### What they represent
These rows come from Android's `LocationManager` API, not directly from the
chip. The OS fuses multiple sources to produce the best estimate of position.

### Providers observed

| Provider | Count | What it is |
|----------|------:|-----------|
| `GPS` | 45 | Pure GNSS solution computed from satellite ranging — most accurate when sky is open |
| `FLP` | 46 | Fused Location Provider — Android's sensor fusion combining GNSS + accelerometer + gyroscope + barometer |
| `NLP` | 4 | Network Location Provider — Wi-Fi / cell-tower triangulation when GNSS is unavailable or weak |

### Column explanations

| Column | Example | Meaning |
|--------|---------|---------|
| `Provider` | GPS | Location source |
| `LatitudeDegrees` | 13.0667 | WGS-84 latitude |
| `LongitudeDegrees` | 77.5917 | WGS-84 longitude |
| `AltitudeMeters` | 837.4 | Ellipsoidal altitude (WGS-84) |
| `SpeedMps` | 0.0–1.08 | Horizontal speed in m/s |
| `AccuracyMeters` | 6.5–14.6 | 68th-percentile horizontal accuracy radius (1-sigma) |
| `BearingDegrees` | 45.0 | Heading in degrees from North |
| `UnixTimeMillis` | 1772042138000 | Fix timestamp (Unix epoch ms) |
| `SpeedAccuracyMps` | 0.8–1.5 | 1-sigma speed accuracy |
| `BearingAccuracyDegrees` | 45.0 | 1-sigma bearing accuracy |
| `elapsedRealtimeNanos` | 6567087... | Time since boot when fix was computed |
| `VerticalAccuracyMeters` | 1.06–5.79 | 1-sigma vertical accuracy |
| `MockLocation` | 0 | 1 = fake/spoofed location; 0 = genuine |
| `NumberOfUsedSignals` | (blank here) | Number of satellite signals used |
| `SolutionType` | (blank here) | 0=GNSS-only, 1=DGNSS, 2=RTK-fixed, etc. |

### Position statistics

| Provider | Fixes | Lat spread | Lon spread | Mean accuracy |
|----------|------:|-----------|-----------|--------------|
| GPS | 45 | 0.000023° (~2.5 m) | 0.000007° (~0.7 m) | 10.9 m |
| FLP | 46 | 0.000056° (~6.2 m) | 0.000025° (~2.5 m) | 11.8 m |
| NLP | 4 | 0.000015° (~1.7 m) | 0.000009° (~0.9 m) | 12.8 m |

The phone was **stationary** (speeds ≈0 m/s). The position scatter is therefore
a direct measure of fix noise, not true motion.

---

## 4. IMU Rows — Inertial Measurement Unit

### `UncalAccel` — Uncalibrated Accelerometer (4 841 rows, ~100 Hz)

Measures specific force (gravity + motion) on three axes.

| Column | Meaning |
|--------|---------|
| `UncalAccelXMps2` | Raw X-axis acceleration in m/s² |
| `UncalAccelYMps2` | Raw Y-axis acceleration in m/s² |
| `UncalAccelZMps2` | Raw Z-axis acceleration in m/s² |
| `BiasX/Y/ZMps2` | Estimated bias offsets (0 if not yet calibrated) |
| `CalibrationAccuracy` | 3 = HIGH accuracy |

Typical values here: X≈3.8, Y≈4.7, Z≈7.9 m/s² — the device was held at an
angle (not flat), and the magnitude ≈ √(3.8²+4.7²+7.9²) ≈ 9.8 m/s² = gravity.
This confirms the phone was **stationary and tilted**.

### `UncalGyro` — Uncalibrated Gyroscope (4 840 rows, ~100 Hz)

Measures angular velocity around three axes.

| Column | Meaning |
|--------|---------|
| `UncalGyroX/Y/ZRadPerSec` | Raw rotation rate in radians/second |
| `DriftX/Y/ZRadPerSec` | Estimated drift (gyroscope bias). Here ≈ ±0.002 rad/s = very low drift |
| `CalibrationAccuracy` | 3 = HIGH |

Values here are very small (~0.01–0.12 rad/s) consistent with a nearly
stationary phone with minor hand tremor.

### `UncalMag` — Uncalibrated Magnetometer (4 523 rows, ~100 Hz)

Measures ambient magnetic field in micro-Teslas.

| Column | Meaning |
|--------|---------|
| `UncalMagX/Y/ZMicroT` | Raw magnetic field on each axis (µT) |
| `BiasX/Y/ZMicroT` | Hard-iron bias estimated by Android |
| `CalibrationAccuracy` | 3 = HIGH |

Z component is ≈ –230 µT — the strong downward component is the Earth's
magnetic field in Bangalore (inclination ≈ −20°). X≈61, Y≈−22 µT are the
horizontal components. Total magnitude ≈ 239 µT, consistent with Earth's field
at this location.

### `OrientationDeg` — Fused Orientation (4 838 rows, ~100 Hz)

| Column | Meaning |
|--------|---------|
| `yawDeg` | Azimuth (heading) from magnetic North: ~76–79° → phone faces roughly East |
| `rollDeg` | Roll: ~−25° → tilted 25° to the left |
| `pitchDeg` | Pitch: ~−28° → tilted 28° backward |

### `GameRotationVector` — Rotation Quaternion (~4 800 rows)

Quaternion (x, y, z, w) representing device orientation relative to an
arbitrary initial reference (no magnetic north). Used in games / AR. Values
here: w ≈ 0.63, confirming a roughly 52° total rotation from the neutral pose.

---

## 5. `Nav` Rows — Navigation Messages

**Count: 0 in this log.** The `Nav` row type records raw binary navigation
message frames as they are decoded from the satellite downlink. On many modern
Android devices (including this Qualcomm chipset) these are not exposed by the
driver, so no Nav rows appear.

---

## 6. `Agc` Rows — Automatic Gain Control

**Count: 0 in this log.** AGC records interference/jamming indicators per
constellation. Not all chipsets expose these; this device does not.

---

## Key Takeaways from the TXT File

1. **The phone was stationary and tilted** (~25–28° from vertical), held in
   hand, outdoors in Bangalore.
2. **Five GNSS constellations** were tracked simultaneously, with 10 signals
   typically used in each fix.
3. **Clock bias uncertainty of 75–129 ns** is characteristic of mid-range
   Qualcomm modems and requires relaxed filtering thresholds.
4. **IMU data at ~100 Hz** is synchronised with GNSS, enabling tight sensor
   fusion.
5. **Position fixes are stable to within ~2–6 m** in both GPS-only and fused
   modes for a stationary receiver.

---

## Log2 Differences (Sony XQ-GE54, Qualcomm MPSS.DE.9.0)

The same GnssLogger `.txt` format is used for Log2, but several fields differ
significantly due to the different chipset and better environment.

| Field | Log1 (Xiaomi 13) | Log2 (Sony XQ-GE54) |
|-------|:----------------:|:-------------------:|
| `Raw` row count | 311 | 7181 |
| Session duration | 44 s | 129 s |
| `BiasUncertaintyNanos` | 75–129 ns | **4.6–6.5 ns** |
| Analysis threshold | Relax to 200 ns | Standard 40 ns fine |
| `Cn0DbHz` mean | 23.4 dBHz | **38.1 dBHz** |
| `AccumulatedDeltaRangeState` | **0** (nothing) | **16** (half-cycle reported, not valid) |
| BeiDou `CarrierFrequencyHz` | 1561098000 (B1I only) | 1561098000 (B1I) **+ 1575420000 (B1C)** |
| `PseudorangeRateMetersPerSecond` | Clamped at ±500 m/s (6.8% rows) | No clamping |
| GPS L5 (1176450000 Hz) | Absent | Absent |
| IMU rows | Yes (~100 Hz) | Yes (~100 Hz) |
| `Fix` providers | GPS, FLP, NLP | GPS, FLP, NLP |
| Reported GPS Hacc | 10.9 m | **3.8 m** |

**Key Log2 parsing notes:**
- `BiasUncertaintyNanos` of 4.6–6.5 ns: no threshold relaxation needed.
- BeiDou rows have **two distinct `CarrierFrequencyHz` values** per satellite —
  filter by frequency to separate B1I from B1C measurements.
- `AccumulatedDeltaRangeState = 16` = bit 4 set (`ADR_STATE_HALF_CYCLE_REPORTED`)
  but bit 0 NOT set (`ADR_STATE_VALID`) → treat as no valid ADR.
