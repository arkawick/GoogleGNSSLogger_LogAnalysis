# File 1 — GnssLogger CSV (`gnss_log_*.txt`)

## What Is This File?

This is the primary log file produced by the **GnssLogger** app. It is a plain-text
comma-separated file where every data row begins with a **type tag** identifying which
Android sensor or GNSS subsystem produced that measurement. Comment lines (starting
with `#`) contain column headers for each row type — parse these to obtain correct
column indices because GnssLogger may add or remove columns across app versions.

```
# Raw,utcTimeMillis,TimeNanos,LeapSecond,...   ← column header (comment, starts with #)
Raw,1772042137424,6567086705028,...             ← data row
```

---

## Row Types Overview

| Row type | Source | What it contains |
|----------|--------|-----------------|
| `Raw` | GNSS chip | One raw measurement per satellite signal per epoch |
| `Status` | GNSS chip (`GnssStatus` API) | Satellite visibility snapshot: CN0, azimuth, elevation, used-in-fix |
| `Fix` | Android `LocationManager` | Computed position + accuracy from GPS/FLP/NLP providers |
| `UncalAccel` | Accelerometer | 3-axis specific force at ~100 Hz |
| `UncalGyro` | Gyroscope | 3-axis angular velocity at ~100 Hz |
| `UncalMag` | Magnetometer | 3-axis magnetic field at ~100 Hz |
| `OrientationDeg` | Sensor fusion | Fused yaw/roll/pitch in degrees |
| `GameRotationVector` | Sensor fusion | Rotation quaternion (no magnetic north reference) |
| `Nav` | GNSS chip | Raw navigation message frames (not exposed on most chipsets) |
| `Agc` | GNSS chip | Per-constellation AGC (not exposed on most chipsets) |

---

## 1. `Raw` Rows — Chip-Level GNSS Measurements

### What They Represent

`Raw` rows are the **lowest-level GNSS observables** the Android HAL (Hardware
Abstraction Layer) exposes. Each row contains one measurement of one satellite signal
at one moment in time. They are the raw building blocks from which every navigation
solution is derived. All fields come from the Android `GnssMeasurement` API.

---

### 1.1 Receiver Time Fields

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `utcTimeMillis` | int | ms (Unix epoch) | Wall-clock UTC time when the measurement was taken. Derived from the system clock; may have leap-second discontinuities. |
| `TimeNanos` | int | ns | Hardware GNSS clock time since receiver power-on. This is the primary time reference — it does not jump. |
| `LeapSecond` | int | s | Current GPS–UTC leap-second offset. As of 2026 this is 18 s. Used to convert GPS time to UTC. |
| `TimeUncertaintyNanos` | float | ns | 1-sigma uncertainty on `TimeNanos`. 0.0 means the hardware clock is disciplined to the GNSS timescale. |
| `FullBiasNanos` | int | ns | Integer nanosecond offset: `TimeNanos − GPS_time_in_nanoseconds`. This is a large negative number (~−1.77 × 10¹⁸ ns). Must be added to `TimeNanos` to recover GPS epoch time. |
| `BiasNanos` | float | ns | Sub-nanosecond fractional part of the clock bias not captured by `FullBiasNanos`. Typically < 1 ns. |
| `BiasUncertaintyNanos` | float | ns | **1-sigma uncertainty on the combined clock bias** (`FullBiasNanos + BiasNanos`). This is the most important filtering threshold. See note below. |
| `DriftNanosPerSecond` | float | ns/s | Receiver clock frequency drift. Equivalently: clock error rate in ns per second. |
| `DriftUncertaintyNanosPerSecond` | float | ns/s | 1-sigma uncertainty on the drift. |
| `HardwareClockDiscontinuityCount` | int | count | **Accumulated** counter (since device boot) of how many times the hardware clock was reset. This is NOT the number of resets in the current session. Do not use to detect in-session clock jumps. |

**BiasUncertaintyNanos — critical threshold note:**

The Google quality framework filters out measurements where
`BiasUncertaintyNanos > threshold` (default 40 ns). However, different chipset
architectures report very different values:

| Chipset family | Typical BiasUncNanos | Recommended threshold |
|---------------|---------------------|----------------------|
| Dedicated GNSS modem (MPSS.DE, etc.) | 2–10 ns | 40 ns (standard) |
| Modem-integrated GNSS (MPSS.HI, etc.) | 75–200+ ns | 200 ns (relaxed) |
| Qualcomm Tensor / MediaTek | 5–40 ns | 40 ns (standard) |

`scripts/run_analysis.py` auto-detects the chipset from the GnssLogger header and
sets the threshold accordingly.

---

### 1.2 Satellite Identification Fields

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `Svid` | int | — | Satellite vehicle ID within its constellation. For GPS: 1–32 (PRN). For GLONASS: 1–24 (orbital slot). For Galileo: 1–36. For BeiDou: 1–63. For QZSS: 193–202 (or 1–10 in some HALs). |
| `ConstellationType` | int | — | Constellation code: **1=GPS**, 2=SBAS, **3=GLONASS**, **4=QZSS**, **5=BeiDou**, **6=Galileo**, 7=NavIC |
| `CarrierFrequencyHz` | float | Hz | Signal carrier frequency. Used to identify the frequency band: |

**Carrier frequency → band mapping:**

| Frequency (Hz) | Signal | Standard |
|---------------|--------|---------|
| 1 575 420 000 | GPS L1, Galileo E1, QZSS L1, BeiDou B1C | CDMA |
| 1 602 000 000 + k × 562 500 | GLONASS L1 (k = channel number, −7 to +6) | FDMA |
| 1 561 098 000 | BeiDou B1I | CDMA |
| 1 176 450 000 | GPS L5, Galileo E5a, QZSS L5 | CDMA |
| 1 207 140 000 | Galileo E5b, BeiDou B2b | CDMA |
| 1 268 520 000 | Galileo E6, BeiDou B3I | CDMA |

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `CodeType` | string | — | Signal code type within the band. `C` = Civil/C/A. `P` = Precise (P-code). `I` = In-phase (BeiDou B1I). `Q` = Quadrature. `X` = combined I+Q. |
| `TimeOffsetNanos` | float | ns | Sub-sample time offset of this measurement relative to `TimeNanos`. Usually 0.0. |

---

### 1.3 Measurement State (`State` Bitmask)

The `State` field is a bitmask of tracking-lock flags. A measurement is considered
**usable** (valid pseudorange) when at least one of these bits is set:
- **Bit 3** (`STATE_TOW_DECODED = 8`): GPS/BDS/Galileo time-of-week has been decoded
  from the navigation message.
- **Bit 14** (`STATE_TOW_KNOWN = 16384`): TOW is known by other means (e.g. network
  time injection).

Full bitmask reference:

| Bit | Value | Flag name | Meaning |
|-----|------:|-----------|---------|
| 0 | 1 | `STATE_CODE_LOCK` | Code phase tracking locked |
| 1 | 2 | `STATE_BIT_SYNC` | Bit boundary synchronised |
| 2 | 4 | `STATE_SUBFRAME_SYNC` | Subframe/page synchronised |
| 3 | 8 | `STATE_TOW_DECODED` | Time of Week decoded from nav message — **pseudorange usable** |
| 4 | 16 | `STATE_MSEC_AMBIGUOUS` | Millisecond-level ambiguity exists |
| 5 | 32 | `STATE_SYMBOL_SYNC` | Symbol sync achieved |
| 6 | 64 | `STATE_GLO_STRING_SYNC` | GLONASS string boundary synced |
| 7 | 128 | `STATE_GLO_TOD_DECODED` | GLONASS Time of Day decoded — **GLO pseudorange usable** |
| 8 | 256 | `STATE_BDS_D2_BIT_SYNC` | BeiDou D2 bit sync |
| 9 | 512 | `STATE_BDS_D2_SUBFRAME_SYNC` | BeiDou D2 subframe sync |
| 10 | 1024 | `STATE_GAL_E1BC_CODE_LOCK` | Galileo E1BC code locked |
| 11 | 2048 | `STATE_GAL_E1C_2ND_CODE_LOCK` | Galileo E1C secondary code locked |
| 12 | 4096 | `STATE_GAL_E1B_PAGE_SYNC` | Galileo E1B page synced |
| 13 | 8192 | `STATE_SBAS_SYNC` | SBAS message synced |
| 14 | 16384 | `STATE_TOW_KNOWN` | TOW known by injection — **pseudorange usable** |
| 15 | 32768 | `STATE_GLO_TOD_KNOWN` | GLONASS TOD known by injection — **GLO pseudorange usable** |

**Usability rule:** `(State & 8) != 0` OR `(State & 16384) != 0` (for GPS/BDS/GAL/QZSS)
or `(State & 128) != 0` OR `(State & 32768) != 0` (for GLONASS).

---

### 1.4 Satellite Time and Signal Quality Fields

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `ReceivedSvTimeNanos` | int | ns | **Satellite transmit time** as measured by the receiver. Interpretation varies by constellation — see Section 1.7. |
| `ReceivedSvTimeUncertaintyNanos` | float | ns | 1-sigma uncertainty on `ReceivedSvTimeNanos`. Larger values = noisy code phase. |
| `Cn0DbHz` | float | dB-Hz | **Carrier-to-Noise density ratio** at the correlator output. The primary signal quality metric. |
| `BasebandCn0DbHz` | float | dB-Hz | CN0 measured at baseband before correlation processing. Generally 2–5 dB-Hz lower than `Cn0DbHz`. |

**CN0 quality interpretation:**

| CN0 (dB-Hz) | Quality |
|-------------|---------|
| < 20 | Poor — marginal tracking, may lose lock |
| 20–25 | Moderate — basic tracking, noisy pseudorange |
| 25–35 | Good — typical open-sky signal |
| 35–45 | Excellent — clear sky with no obstructions |
| > 45 | Outstanding — rare for L1 C/A; near theoretical ceiling |

---

### 1.5 Pseudorange Rate Fields

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `PseudorangeRateMetersPerSecond` | float | m/s | **Doppler-derived range rate**: rate of change of distance between receiver and satellite. Used for velocity computation. Negative = satellite approaching, positive = receding. |
| `PseudorangeRateUncertaintyMetersPerSecond` | float | m/s | 1-sigma uncertainty on the range rate. Values > 1 m/s indicate poor tracking. |

**Note on PRR clamping:** Some modem-integrated chipsets clamp `PseudorangeRateMetersPerSecond`
at ±500 m/s due to firmware limitations. Rows clamped at exactly ±500.0 m/s should be
excluded from velocity computation.

---

### 1.6 Carrier Phase (ADR) Fields

Accumulated Delta Range (ADR) is the integrated carrier phase in metres. It is only
meaningful if the `AccumulatedDeltaRangeState` bitmask indicates valid tracking.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `AccumulatedDeltaRangeState` | int | bitmask | Carrier-phase tracking status — see bitmask table below. |
| `AccumulatedDeltaRangeMeters` | float | m | Integrated carrier phase change since last reset (metres = cycles × wavelength). Only valid if `ADR_STATE_VALID` is set. |
| `AccumulatedDeltaRangeUncertaintyMeters` | float | m | 1-sigma uncertainty on the ADR. |

**AccumulatedDeltaRangeState bitmask:**

| Bit | Value | Flag name | Meaning |
|-----|------:|-----------|---------|
| 0 | 1 | `ADR_STATE_VALID` | ADR is valid. **Must be set for carrier phase to be usable.** |
| 1 | 2 | `ADR_STATE_RESET` | ADR was reset (cycle count restarted). Phase continuity broken. |
| 2 | 4 | `ADR_STATE_CYCLE_SLIP` | A cycle slip was detected. Phase continuity broken. |
| 3 | 8 | `ADR_STATE_HALF_CYCLE_RESOLVED` | Half-cycle ambiguity has been resolved. |
| 4 | 16 | `ADR_STATE_HALF_CYCLE_REPORTED` | Half-cycle ambiguity is reported but not resolved. |

**ADR usability rule:**
- Bit 0 (`ADR_STATE_VALID`) **must** be set.
- Bits 1 and 2 (`ADR_STATE_RESET`, `ADR_STATE_CYCLE_SLIP`) **must not** be set.
- Bit 4 alone (`ADR_STATE_HALF_CYCLE_REPORTED` = 16, no VALID) → **not valid**.
  Many chipsets (especially Sony/Qualcomm MPSS.DE) report state=16 — the chip
  tracks carrier phase internally but the HAL driver does not certify it as valid.

---

### 1.7 Automatic Gain Control

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `AgcDb` | float | dB | **Automatic Gain Control** level. A proxy for RF interference and jamming. Nominally 0 dB; large negative values indicate the AGC is attenuating the input due to strong interference. |

Not all chipsets expose AgcDb in `Raw` rows; some expose it only through `Agc` rows.
If the column is present and non-zero for most measurements, the RF environment is
stable. All-zero or absent means the chipset does not report AGC here.

---

### 1.8 Satellite Ephemeris Fields

These fields contain the satellite's state vector and clock correction as broadcast
by the satellite's navigation message and decoded by the chipset.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `SvPositionEcefXMeters` | float | m | Satellite X position in Earth-Centred Earth-Fixed (ECEF) frame |
| `SvPositionEcefYMeters` | float | m | Satellite Y position in ECEF |
| `SvPositionEcefZMeters` | float | m | Satellite Z position in ECEF |
| `SvVelocityEcefXMetersPerSecond` | float | m/s | Satellite X velocity in ECEF |
| `SvVelocityEcefYMetersPerSecond` | float | m/s | Satellite Y velocity in ECEF |
| `SvVelocityEcefZMetersPerSecond` | float | m/s | Satellite Z velocity in ECEF |
| `SvClockBiasMeters` | float | m | Satellite clock error in metres (= satellite clock bias × speed of light). **Must be ADDED to the raw pseudorange** (not subtracted) to correct for satellite clock error. |
| `SvClockDriftMetersPerSecond` | float | m/s | Rate of change of satellite clock error in m/s. |

---

### 1.9 Inter-Signal Bias Fields

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `FullInterSignalBiasNanos` | float | ns | Inter-signal bias between this signal and the GPS L1 C/A reference signal. Used for multi-frequency pseudorange alignment. |
| `FullInterSignalBiasUncertaintyNanos` | float | ns | 1-sigma uncertainty on the ISB. |
| `SatelliteInterSignalBiasNanos` | float | ns | Satellite-reported (broadcast) inter-signal bias. |
| `SatelliteInterSignalBiasUncertaintyNanos` | float | ns | 1-sigma uncertainty on the satellite ISB. |

---

### 1.10 Ionospheric Correction Coefficients

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `KlobucharAlpha0` through `KlobucharAlpha3` | float | varies | Alpha coefficients of the GPS Klobuchar ionospheric model (broadcast in GPS LNAV subframe 4). Used to estimate single-frequency ionospheric delay. |
| `KlobucharBeta0` through `KlobucharBeta3` | float | varies | Beta coefficients of the Klobuchar model. |

These are shared across all GPS satellites in the same epoch (identical values per epoch).
Presence indicates the receiver has decoded the ionospheric model from the nav message.

---

### 1.11 Pseudorange Computation Algorithm

The geometric pseudorange (in metres) is computed as:

```
t_rx  = TimeNanos - (FullBiasNanos + BiasNanos)     # receiver time in GPS nanoseconds
sv_t  = ReceivedSvTimeNanos                          # satellite transmit time (ns)

# Constellation-specific adjustments to sv_t:
#   GPS / Galileo / QZSS:  sv_t is already GPS week time (ns within week)
#   BeiDou:                sv_t is BDS TOW = GPS TOW - 14 s
#                          → use  sv_t_gps = sv_t + 14 × 10⁹
#   GLONASS:               sv_t is GLONASS Time of Day (TOD)
#                          → t_mod = (t_rx + 10782 × 10⁹) mod 86400 × 10⁹
#                            then  dt = t_mod - sv_t

dt           = t_rx_mod - sv_t                       # signal travel time (ns)
pseudorange  = dt × 1e-9 × c                         # metres (c = 299 792 458 m/s)

# Apply satellite clock correction:
pseudorange_corrected = pseudorange + SvClockBiasMeters
```

**Note on GPS week rollover:** `t_rx` is in GPS nanoseconds since the GPS epoch.
`ReceivedSvTimeNanos` is within the current GPS week (modulo 604800 × 10⁹ ns).
To avoid week-boundary errors, work with `t_rx mod (604800 × 10⁹)` for GPS/BDS/GAL/QZSS.

**Note on per-constellation clock offsets:** GPS, QZSS, and Galileo share the same
timescale (to within a few ns). BeiDou and GLONASS have independent clocks.
When solving the navigation equations with mixed constellations, use a separate
receiver clock offset per constellation group (GPS+QZSS+GAL, BDS, GLO), or
inter-system biases will appear as ~600 m errors in residuals.

---

## 2. `Status` Rows — Satellite Visibility Status

### What They Represent

One `Status` block is emitted per GNSS epoch (approximately every 1 second). Each
block contains one row per visible satellite signal (regardless of whether that
satellite is tracked or used in the position fix). These rows come from the Android
`GnssStatus` API and provide the sky view for plotting.

### Column Reference

| Column | Type | Description |
|--------|------|-------------|
| `UnixTimeMillis` | int | Epoch timestamp in Unix milliseconds. May be blank on some devices. |
| `SignalCount` | int | Total number of satellite signals in this epoch's snapshot. |
| `SignalIndex` | int | Index of this signal within the epoch block (0 to SignalCount−1). |
| `ConstellationType` | int | 1=GPS, 3=GLONASS, 4=QZSS, 5=BeiDou, 6=Galileo, 7=NavIC |
| `Svid` | int | Satellite vehicle ID (same encoding as Raw rows). |
| `CarrierFrequencyHz` | float | Carrier frequency in Hz (same encoding as Raw rows). |
| `Cn0DbHz` | float | Signal strength in dB-Hz. Same as in Raw rows. |
| `AzimuthDegrees` | float | Satellite azimuth measured clockwise from geographic North (0–360°). |
| `ElevationDegrees` | float | Satellite elevation above the horizon (0–90°). |
| `UsedInFix` | int | 1 = this satellite was used in the current position fix; 0 = tracked but not used. |
| `HasAlmanacData` | int | 1 = receiver has almanac (coarse orbit) data for this satellite. |
| `HasEphemerisData` | int | 1 = receiver has full ephemeris (precise orbit) data — required to use satellite in fix. |
| `BasebandCn0DbHz` | float | Baseband-level CN0. Generally 2–5 dB-Hz lower than `Cn0DbHz`. |

---

## 3. `Fix` Rows — Android Position Fixes

### What They Represent

`Fix` rows come from Android's `LocationManager` API. The OS can fuse GNSS, Wi-Fi,
cell towers, and IMU data into a position estimate. Multiple providers may produce
concurrent fixes.

### Provider Types

| Provider | Description |
|----------|-------------|
| `GPS` | Pure GNSS solution computed from satellite ranging. Most accurate outdoors. |
| `FLP` | Fused Location Provider — Android's sensor-fusion engine combining GNSS, accelerometer, gyroscope, and sometimes barometer. Generally tracks GPS very closely; adds dead-reckoning during GNSS outages. |
| `NLP` | Network Location Provider — position from Wi-Fi AP database lookup or cell-tower triangulation. Accuracy 10–1000 m depending on infrastructure density. |
| `PASSIVE` | Receives fixes produced by other apps without triggering hardware independently. |

### Column Reference

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `Provider` | string | — | Location source (`gps`, `fused`, `network`, `passive`) |
| `LatitudeDegrees` | float | ° | WGS-84 geodetic latitude, positive North |
| `LongitudeDegrees` | float | ° | WGS-84 longitude, positive East |
| `AltitudeMeters` | float | m | **Ellipsoidal altitude above WGS-84 reference ellipsoid**, not above sea level. To get MSL altitude: add the geoid separation (from NMEA GGA). |
| `SpeedMps` | float | m/s | Horizontal ground speed |
| `AccuracyMeters` | float | m | **68th-percentile (1-sigma) horizontal accuracy radius**. 68% of fixes are expected within this radius of the true position. |
| `BearingDegrees` | float | ° | True heading from North (0–360°), clockwise. Meaningful only when moving. |
| `UnixTimeMillis` | int | ms | Fix timestamp in Unix milliseconds (UTC) |
| `SpeedAccuracyMps` | float | m/s | 1-sigma speed accuracy |
| `BearingAccuracyDegrees` | float | ° | 1-sigma bearing accuracy |
| `elapsedRealtimeNanos` | int | ns | Monotonic system time (since boot) when fix was computed — not affected by wall-clock changes |
| `VerticalAccuracyMeters` | float | m | 1-sigma vertical (altitude) accuracy |
| `MockLocation` | int | — | 1 = fake/spoofed location (testing); 0 = genuine |
| `NumberOfUsedSignals` | int | — | Number of satellite signals used in this fix (may be blank on older HALs) |
| `SolutionType` | int | — | 0=GNSS-only, 1=DGNSS, 2=RTK-fixed, 3=RTK-float, 4=PPP. Often blank. |

---

## 4. IMU Rows — Inertial Measurement Unit

IMU sensors log at approximately 100 Hz on most Android devices. They are synchronised
with GNSS time via `utcTimeMillis`.

### `UncalAccel` — Uncalibrated Accelerometer

Measures **specific force** (gravity + linear acceleration) on three body axes.

| Column | Units | Description |
|--------|-------|-------------|
| `UncalAccelXMps2` | m/s² | Raw X-axis specific force (before hard-iron / scale-factor correction) |
| `UncalAccelYMps2` | m/s² | Raw Y-axis specific force |
| `UncalAccelZMps2` | m/s² | Raw Z-axis specific force |
| `BiasXMps2` | m/s² | Estimated accelerometer bias on X (0 until calibrated) |
| `BiasYMps2` | m/s² | Estimated accelerometer bias on Y |
| `BiasZMps2` | m/s² | Estimated accelerometer bias on Z |
| `CalibrationAccuracy` | int | 0=UNCALIBRATED, 1=LOW, 2=MEDIUM, 3=HIGH |

For a stationary device, the magnitude √(X² + Y² + Z²) should equal local gravitational
acceleration (~9.8 m/s²). Deviations indicate non-stationary motion.

### `UncalGyro` — Uncalibrated Gyroscope

Measures **angular velocity** around three body axes.

| Column | Units | Description |
|--------|-------|-------------|
| `UncalGyroXRadPerSec` | rad/s | Raw angular velocity around X axis |
| `UncalGyroYRadPerSec` | rad/s | Raw angular velocity around Y axis |
| `UncalGyroZRadPerSec` | rad/s | Raw angular velocity around Z axis |
| `DriftXRadPerSec` | rad/s | Estimated gyroscope drift (bias) on X |
| `DriftYRadPerSec` | rad/s | Estimated drift on Y |
| `DriftZRadPerSec` | rad/s | Estimated drift on Z |
| `CalibrationAccuracy` | int | 0=UNCALIBRATED to 3=HIGH |

Values near zero confirm a stationary device. Non-zero drift values indicate successful
in-field bias estimation.

### `UncalMag` — Uncalibrated Magnetometer

Measures the **ambient magnetic field** on three body axes.

| Column | Units | Description |
|--------|-------|-------------|
| `UncalMagXMicroT` | µT | Raw magnetic field on X axis |
| `UncalMagYMicroT` | µT | Raw magnetic field on Y axis |
| `UncalMagZMicroT` | µT | Raw magnetic field on Z axis |
| `BiasXMicroT` | µT | Estimated hard-iron bias on X |
| `BiasYMicroT` | µT | Estimated hard-iron bias on Y |
| `BiasZMicroT` | µT | Estimated hard-iron bias on Z |
| `CalibrationAccuracy` | int | 0=UNCALIBRATED to 3=HIGH |

The Earth's field magnitude varies by location (25–65 µT). The Z-component is typically
the largest at mid-latitudes due to the field dip angle. Compare to WMM2025 model values
for the recording location to verify sensor calibration.

### `OrientationDeg` — Fused Orientation

| Column | Units | Description |
|--------|-------|-------------|
| `yawDeg` | ° | Azimuth (compass heading): angle from geographic North, 0–360° clockwise |
| `rollDeg` | ° | Roll: rotation around the front-to-back axis (positive = right side down) |
| `pitchDeg` | ° | Pitch: rotation around the left-right axis (positive = top tilted away from user) |

### `GameRotationVector` — Rotation Quaternion

Orientation expressed as a unit quaternion (x, y, z, w) relative to an arbitrary
initial reference frame. Unlike `OrientationDeg`, this does not use the magnetometer
and therefore has no geographic North reference, but it avoids magnetic disturbances.

---

## 5. `Nav` Rows — Navigation Messages

`Nav` rows contain **raw binary navigation message frames** decoded from the satellite
downlink. Format: `Nav,<constellation>,<svid>,<type>,<status>,<messageId>,<submessageId>,<data>`.

Most modern Android chipsets do not expose Nav rows to the HAL — the driver decodes
the messages internally for ephemeris computation but does not forward them to the app.
If Nav rows are absent, this is normal behaviour, not a data loss.

---

## 6. `Agc` Rows — Per-Constellation AGC

`Agc` rows provide Automatic Gain Control readings per GNSS constellation:
`Agc,<utcTimeMillis>,<constellation>,<carrierFreq>,<agcLevelDb>`.

These are distinct from the `AgcDb` column in `Raw` rows. Not all chipsets expose `Agc`
rows. If both `Agc` rows and `Raw.AgcDb` are present, they measure the same quantity;
use whichever is more complete.

---

## 7. Key Parsing Notes

### Column index vs column name
Always parse column headers from the `# Raw,` comment line — do not hard-code column
indices. The column count changes between GnssLogger versions (the app added several
columns in v3.x).

### Filtering criteria for valid measurements
A measurement should be included in analysis only if **all** of the following hold:
1. `BiasUncertaintyNanos` ≤ threshold (40 ns standard; 200 ns for MPSS.HI chipsets)
2. `State` has `STATE_TOW_DECODED` (bit 3) or `STATE_TOW_KNOWN` (bit 14) set
   — or `STATE_GLO_TOD_DECODED` (bit 7) / `STATE_GLO_TOD_KNOWN` (bit 15) for GLONASS
3. `ReceivedSvTimeUncertaintyNanos` is reasonably small (< 500 ns is a common threshold)

### SvClockBiasMeters sign convention
`SvClockBiasMeters` must be **added** to the raw pseudorange. The value is positive
when the satellite clock is ahead of GPS time; adding it to the pseudorange shortens
it (corrects the overestimated range). This is the opposite of the sign convention in
some textbooks that define the satellite clock error as a subtraction.

### BeiDou time system
BeiDou System Time (BDT) is offset from GPS Time by exactly 14 seconds:
`BDT = GPS_time − 14 s`. When computing BeiDou pseudoranges, the satellite transmit
time (`ReceivedSvTimeNanos`) is in BDT (= GPS TOW − 14 × 10⁹ ns). Adjust accordingly.

### GLONASS time system
GLONASS uses its own time scale (GLONASS Time, offset from UTC by leap seconds but
referenced differently from GPS). `ReceivedSvTimeNanos` for GLONASS is **Time of Day**
in the GLONASS time frame, not GPS week time. Conversion:
```
t_glo_ns = t_rx_gps_ns + 10782 × 10⁹   # approximate constant offset to GLONASS epoch
t_mod    = t_glo_ns mod (86400 × 10⁹)  # GLONASS TOD in nanoseconds
dt       = t_mod - ReceivedSvTimeNanos
```

### Multi-constellation receiver clock
When solving for position with mixed constellations, use a separate receiver clock offset
parameter for each constellation group. GPS/QZSS/Galileo share the same timescale and
can use a common offset. BeiDou and GLONASS each have their own offsets. Forcing a single
receiver clock across all constellations introduces ~600 m errors in the residuals.

---

## 8. Annotated Examples

### 8.1 File Header (first lines of .txt)

```
# GnssLogger Version: 3.1.1.2
# Start: 2026-03-10T08:30:00.000Z
# manufacturer: Google
# model: Pixel 9
# AndroidVersionRelease: 16
# DeviceBuildVersionRelease: 16
# Platform: Tensor G4
# GNSS Hardware Model Name: qcom;MPSS.DE.9.1;...
# Raw,utcTimeMillis,TimeNanos,LeapSecond,TimeUncertaintyNanos,FullBiasNanos, \
#   BiasNanos,BiasUncertaintyNanos,DriftNanosPerSecond,...
```

Key lines to parse:
- `manufacturer` / `model` → build the device label
- `Platform` → chipset family; used for BiasUncNanos threshold selection
- `GNSS Hardware Model Name` → contains the modem identifier (e.g. `MPSS.DE.9.1`)
- `# Raw,` → defines column order for Raw rows (parse this, do not hard-code indices)

---

### 8.2 Raw Row — GPS L1 Satellite (high CN0, TOW decoded)

```
Raw,1772042137424,6567086705028,18,0.0,-1772042131138021376,0.31,5.2,-0.04,0.002,0,
    23,0.0,16431,88233485714286,18,42.3,−1814.2,0.21,1,0.0,0.0,1575420000.0,1,
    0.3,1575420000.0,0.0,...,22472891.013,0.0,0.0,5.6,0.0,0.0,C,
    15234567.1,−21345678.2,10456789.3,...,−3.1,0.04,...
```

Annotated key fields:

| Field value | Column | Interpretation |
|-------------|--------|----------------|
| `1772042137424` | utcTimeMillis | 2026-02-25 17:55:37.424 UTC |
| `6567086705028` | TimeNanos | Hardware clock: ~6 567 s since boot |
| `18` | LeapSecond | GPS ahead of UTC by 18 s |
| `0.0` | TimeUncertaintyNanos | Clock fully disciplined |
| `-1772042131138021376` | FullBiasNanos | Large negative integer; GPS epoch offset |
| `0.31` | BiasNanos | 0.31 ns fractional correction |
| `5.2` | BiasUncertaintyNanos | 5.2 ns — dedicated GNSS modem, well within 40 ns threshold |
| `23` | Svid | GPS PRN 23 |
| `16431` | State | Binary: 100000000101111 — TOW_DECODED (bit 3) set, measurement usable |
| `88233485714286` | ReceivedSvTimeNanos | Satellite transmit time within GPS week |
| `18` | ReceivedSvTimeUncertaintyNanos | 18 ns uncertainty — good code lock |
| `42.3` | Cn0DbHz | 42.3 dB-Hz — excellent signal |
| `−1814.2` | PseudorangeRateMetersPerSecond | Satellite approaching at 1 814 m/s projected rate |
| `0.21` | PseudorangeRateUncertaintyMps | Low uncertainty — reliable Doppler |
| `1` | AccumulatedDeltaRangeState | Bit 0 set: ADR_STATE_VALID — carrier phase usable |
| `1575420000.0` | CarrierFrequencyHz | 1575.42 MHz → GPS L1 C/A confirmed |
| `1` | ConstellationType | GPS |
| `0.3` | AgcDb | AGC near 0 — clean RF environment |
| `C` | CodeType | C/A civil code |

**State bitmask decode for `16431`:**
```
16431 = 0b100000000101111
         |||||||||||||||+-- bit 0: CODE_LOCK        ✓
         ||||||||||||||+--- bit 1: BIT_SYNC          ✓
         |||||||||||||+---- bit 2: SUBFRAME_SYNC     ✓
         ||||||||||||+----- bit 3: TOW_DECODED       ✓  ← usable
         |||||||||||+------ bit 4: MSEC_AMBIGUOUS    ✗
         ||||||||||+------- bit 5: SYMBOL_SYNC       ✗
         ...
         |+----------------- bit 13: (reserved)     ✗
         +------------------ bit 14: TOW_KNOWN       ✓  ← also usable
```
Conclusion: pseudorange is usable (TOW_DECODED set).

---

### 8.3 Raw Row — BeiDou B1C (State with TOW_KNOWN)

```
Raw,1772042137424,6567086705028,18,0.0,-1772042131138021376,0.31,5.2,...,
    19,0.0,49152,70155485714286,22,39.8,−621.4,0.18,0,0.0,0.0,1575420000.0,5,...,C
```

| Field value | Column | Interpretation |
|-------------|--------|----------------|
| `19` | Svid | BeiDou satellite B19 (MEO) |
| `49152` | State | Binary: 1100000000000000 — bits 14 and 15 set (TOW_KNOWN + GLO_TOD_KNOWN) ← usable |
| `70155485714286` | ReceivedSvTimeNanos | BDS TOW — must add 14×10⁹ before pseudorange calculation |
| `39.8` | Cn0DbHz | 39.8 dB-Hz — very good |
| `1575420000.0` | CarrierFrequencyHz | 1575.42 MHz → B1C (not B1I) |
| `5` | ConstellationType | BeiDou |
| `0` | AccumulatedDeltaRangeState | No valid ADR |

---

### 8.4 Raw Row — GLONASS L1 (ADR half-cycle reported)

```
Raw,1772042137424,6567086705028,18,0.0,...,
    9,0.0,128,57443200000000,31,35.1,+934.7,0.25,16,−1843.221,0.003,1602562500.0,3,...
```

| Field value | Column | Interpretation |
|-------------|--------|----------------|
| `9` | Svid | GLONASS orbital slot R09 |
| `128` | State | Bit 7 set: GLO_TOD_DECODED ← usable |
| `57443200000000` | ReceivedSvTimeNanos | GLONASS Time of Day in ns (not GPS week time) |
| `35.1` | Cn0DbHz | 35.1 dB-Hz — good |
| `+934.7` | PseudorangeRateMetersPerSecond | Positive: satellite receding |
| `16` | AccumulatedDeltaRangeState | Bit 4: ADR_STATE_HALF_CYCLE_REPORTED only — NOT valid |
| `−1843.221` | AccumulatedDeltaRangeMeters | Value present but not usable (state not VALID) |
| `1602562500.0` | CarrierFrequencyHz | 1602.5625 MHz = 1602 + (1×0.5625) → GLONASS channel k=+1 |
| `3` | ConstellationType | GLONASS |

GLONASS pseudorange computation requires the TOD-to-GPS-time conversion:
```
t_rx_gps  = TimeNanos - (FullBiasNanos + BiasNanos)          # receiver time (GPS ns)
t_glo_ns  = t_rx_gps + 10782_000_000_000                     # shift to GLONASS epoch
t_mod     = t_glo_ns % 86_400_000_000_000                    # GLONASS TOD (ns)
dt        = t_mod - ReceivedSvTimeNanos                       # signal travel time (ns)
pseudorange = dt * 1e-9 * 299_792_458                        # metres
```

---

### 8.5 Status Row Block (one epoch, four satellites shown)

```
# Status,UnixTimeMillis,SignalCount,SignalIndex,ConstellationType,Svid,
#   CarrierFrequencyHz,Cn0DbHz,AzimuthDegrees,ElevationDegrees,UsedInFix,
#   HasAlmanacData,HasEphemerisData,BasebandCn0DbHz

Status,,37,0,1,23,1575420000.0,42.3,  59.0,31.0,1,1,1,38.1   ← GPS PRN23, 31° elev, used
Status,,37,1,1,18,1575420000.0,45.1, 139.0,47.0,1,1,1,41.2   ← GPS PRN18, 47° elev, used
Status,,37,2,3,9, 1602562500.0,35.1, 213.0,28.0,1,1,1,31.4   ← GLONASS R09, 28° elev
Status,,37,3,5,19,1575420000.0,39.8,  88.0,62.0,1,1,1,36.1   ← BeiDou B19, 62° elev
Status,,37,4,5,6, 1561098000.0,22.4, 172.0, 8.0,0,1,1,18.9   ← BeiDou B06 GEO, 8° elev, NOT used
Status,,37,5,6,1, 1575420000.0,41.7, 315.0,55.0,1,1,1,38.3   ← Galileo E01, 55° elev
...
```

Observations from this block:
- `SignalCount=37` — 37 signals visible this epoch; high for a dedicated GNSS chipset
- BeiDou GEO (B06 at 8° elevation) tracked (`HasEphemerisData=1`) but not used in fix
  (`UsedInFix=0`) — low elevation + poor geometry contribution
- GPS PRN18 at 47° has CN0 45.1 — near-excellent; high elevation, short iono path
- `BasebandCn0DbHz` consistently 3–4 dB-Hz below `Cn0DbHz` — normal correlator processing gain

---

### 8.6 Fix Row — GPS Provider (stationary receiver)

```
# Fix,Provider,LatitudeDegrees,LongitudeDegrees,AltitudeMeters,SpeedMps,AccuracyMeters,
#   BearingDegrees,UnixTimeMillis,SpeedAccuracyMps,BearingAccuracyDegrees,
#   elapsedRealtimeNanos,VerticalAccuracyMeters,MockLocation,...

Fix,gps,13.06812,77.59183,872.94,0.0,3.8,0.0,1772042137000,0.12,45.0,6567086000000,5.2,0
```

| Field | Value | Interpretation |
|-------|-------|----------------|
| Provider | `gps` | Pure GNSS solution |
| Latitude | `13.06812° N` | WGS-84 |
| Longitude | `77.59183° E` | WGS-84 |
| AltitudeMeters | `872.94 m` | Ellipsoidal (WGS-84). Add geoid separation (~−86 m here) to get MSL: 872.94 + (−86) = **~959 m MSL** |
| SpeedMps | `0.0` | Stationary |
| AccuracyMeters | `3.8 m` | 1-sigma horizontal; good for single-frequency open sky |
| BearingDegrees | `0.0` | Meaningless when stationary |
| SpeedAccuracyMps | `0.12` | Very low — chipset confident in zero speed |
| VerticalAccuracyMeters | `5.2 m` | ~1.4× horizontal — typical ratio for good geometry |
| MockLocation | `0` | Genuine fix |

---

### 8.7 IMU Row Examples

**UncalAccel — stationary phone held upright (slight tilt):**
```
UncalAccel,1772042137010,-0.34,5.21,8.04,0.0,0.0,0.0,3
```
X=−0.34, Y=5.21, Z=8.04 m/s²
Magnitude = √(0.34² + 5.21² + 8.04²) = √(0.116 + 27.14 + 64.64) = √91.9 ≈ **9.59 m/s²**
Close to gravity (9.8 m/s²); small deviation from tilt angle. The device is nearly
stationary but held at ~33° from vertical (arctan(5.21/8.04) ≈ 33°).

**UncalGyro — stationary phone:**
```
UncalGyro,1772042137010,0.003,-0.008,0.012,0.001,-0.002,0.003,3
```
All values near zero rad/s — confirms stationary. Drift values (0.001, −0.002, 0.003)
show calibration has converged (CalibrationAccuracy=3=HIGH).

**UncalMag — mid-latitude location:**
```
UncalMag,1772042137010,21.4,-8.3,-43.2,2.1,-1.4,0.8,3
```
Magnitude = √(21.4² + 8.3² + 43.2²) = √(458 + 69 + 1866) = √2393 ≈ **48.9 µT**
Consistent with Earth's field strength at ~13°N latitude. Z-component dominant
(negative = dipping downward), consistent with Southern Hemisphere dip direction
reversal not applying here — India has positive inclination, so Z negative confirms
phone's Z-axis points upward.

---

### 8.8 Pseudorange Worked Example (GPS)

Given a Raw row with:
```
TimeNanos          = 6_567_086_705_028
FullBiasNanos      = -1_772_042_131_138_021_376
BiasNanos          = 0.312
ReceivedSvTimeNanos = 88_233_485_714_286
SvClockBiasMeters  = -3.142
```

Step 1 — Receiver GPS time:
```
t_rx = TimeNanos - (FullBiasNanos + BiasNanos)
     = 6_567_086_705_028 - (-1_772_042_131_138_021_376 + 0.312)
     = 1_772_048_698_224_753_028 - 0.312   ns (absolute GPS time since epoch)
```

Step 2 — GPS time within current week:
```
WEEK_NS = 604_800 × 10⁹ = 604_800_000_000_000
t_rx_tow = t_rx mod WEEK_NS
         ≈ 64_498_000_000_000  ns  = 64 498.0 s into the GPS week
```

Step 3 — Signal travel time:
```
dt = t_rx_tow - ReceivedSvTimeNanos
   = 64_498_000_000_000 - 88_233_485_714_286
```
If negative (due to week-rollover near boundary), add `WEEK_NS`. Here:
```
   = negative → dt = 64_498_000_000_000 - 88_233_485_714_286 + WEEK_NS
   = 580_064_514_285_714 + 604_800_000_000_000  (example showing week rollover handling)
```
Typical dt for GPS ≈ 67–87 ms (20 000–26 000 km / speed of light).

Step 4 — Raw pseudorange:
```
pseudorange_raw = dt × 1e-9 × 299_792_458
               ≈ 0.07734 × 299_792_458 ≈ 23_186_000 m  =  23 186 km
```

Step 5 — Satellite clock correction:
```
pseudorange_corr = pseudorange_raw + SvClockBiasMeters
                 = 23_186_000 + (-3.142)
                 = 23_185_996.858 m
```

The corrected pseudorange still contains ionospheric, tropospheric, and receiver clock
errors — these are removed in the position estimation step.
