# GNSS Quality Framework — Google Tools, Thresholds, and Beyond

## Overview

High-quality GNSS performance on an Android device depends on three hardware components
working together:

| Component | Role | Key metric in analysis |
|-----------|------|----------------------|
| **GNSS chip** | Tracks satellites, measures pseudorange/Doppler/phase | CN0, BiasUncertaintyNanos, PRR noise, ADR validity, L5 support |
| **Oscillator** | Provides the time reference the chip uses | BiasUncertaintyNanos, clock bias drift (ΔClockBias std) |
| **Antenna** | Receives the satellite signal | CN0 levels, elevation-dependent signal pattern, multipath susceptibility |

A deficiency in any one component limits the entire chain. A good chip with a poor
antenna cannot achieve high CN0. A good antenna with an unstable oscillator cannot
achieve low BiasUncertaintyNanos.

---

## Google's Analysis Tools

### GnssLogger App

- Records raw GNSS measurements directly from the Android GNSS HAL
- Produces three files per session: `.txt` (raw CSV), `.nmea` (NMEA 0183), `.26o` (RINEX 4.01)
- Available for **Android phones** and **Wear OS 2.0+** watches
- No network connection required for logging; network improves TTFF via SUPL assistance

### gnss_analysis.ipynb (Google Colab Notebook)

- Analyses the GnssLogger `.txt` file against **35 GNSS quality metrics**
- Requires a **network connection** during analysis for:
  - **Assistance data** — to decode satellite ephemeris positions
  - **SatPvt** — satellite position/velocity/time computation (required for residual analysis)
- Availability:
  - Phones: available now
  - Wear OS watches: Q1 2026

### Google Android Bootcamp Quality Framework (41 checks)

The extended framework implemented in `scripts/gnss_quality_analysis_v2.ipynb` in this
project. Adds 6 checks to the original 35:

| Section | Checks | Added vs 35-metric |
|---------|:------:|:-----------------:|
| Basic Checks | 14 | +1 (duplicate signals) |
| Time | 8 | +2 (clock bias std, LS-PR residuals) |
| ADR / PRR / PR | 7 | +1 (L5 delta-PR vs delta-ADR) |
| Residuals | 12 | +2 (normalised RMS checks) |

---

## Quality Thresholds

### What a Threshold Means

Each check compares a measured metric to a threshold. The threshold defines the minimum
acceptable performance for a device to be considered suitable for a given application
class. Thresholds are stored in `parameters/thresholds.json`.

### Requirements for Best DGNSS Performance

For differential GNSS and carrier-phase-based positioning, a device should:

| Requirement | Why | Current status on most Android |
|-------------|-----|-------------------------------|
| Support L1 + L5 | Dual-frequency iono-free combination eliminates ~99% of iono error; required for RTK | L5 absent on most consumer Android (HAL not enabled) |
| Support valid ADR (carrier phase) | Enables RTK, PPP, carrier smoothing; 100× more precise than pseudorange | 0% valid on most devices (state=0 or state=16) |
| Pass all 41 quality tests | Confirms chip, oscillator, and antenna all meet Google's baseline | Most devices fail 6–15 checks |

---

## What Else Can Be Done — Beyond Google's Tools

The Google framework scores a device against fixed thresholds but does not perform
some important categories of analysis. The following methods provide complementary
or deeper insight.

---

### 1. RINEX-Based Post-Processing (Independent Position Solution)

Instead of relying only on the Android-computed position, process the RINEX file
independently with geodetic software:

| Tool | Method | What it gives |
|------|--------|---------------|
| **RTKLIB** (`rnx2rtkp`) | SPP (broadcast ephemeris) | Independent position + residuals, unaffected by chipset firmware |
| **CSRS-PPP** (NRCan, online) | PPP (precise ephemeris) | 2–10 cm accuracy; reveals true pseudorange quality independent of device fix |
| **OPUS** (NGS, online, US only) | PPP | cm-level reference position |
| **RTKLIB RTK mode** | RTK (needs a base station RINEX) | 1–3 cm if ADR is valid |

**Why this matters:** The Android chipset may apply internal filtering, smoothing, or
corrections before reporting Fix row positions. Post-processing the raw RINEX with
broadcast ephemeris gives an unfiltered view of the raw measurement quality.

**How to do it:**
```bash
# Download broadcast navigation file for the session date from CDDIS
# e.g. brdc0660.26n for day 066 of 2026

# Run single-point positioning
rnx2rtkp -p 0 gnss_log.26o brdc0660.26n -o solution.pos

# Compare output lat/lon with NMEA GGA position
```

---

### 2. Position Accuracy Against a Known Reference

The Android-reported `AccuracyMeters` is a self-reported estimate. To measure true
accuracy, compare fixes against an independently known position:

| Method | Accuracy of reference | Effort |
|--------|----------------------|--------|
| Geodetic benchmark (survey mark) | Millimetre-level | Find nearest NGS / GSI mark |
| CORS station (IGS network) | Centimetre-level | Use IGS site database |
| Long-average GNSS position | ~10 cm (static, 24 h) | Average hundreds of fixes |
| Google Maps / OSM known feature | ~1–5 m | Quick approximate check |

**Metrics to compute:**
- **CEP50** — radius containing 50% of fixes (= median 2D error)
- **CEP68** — radius containing 68% of fixes (~1-sigma horizontal)
- **CEP95** — radius containing 95% of fixes (2-sigma)
- **RMS 2D error** — root-mean-square horizontal error
- **Vertical error** — compare altitude with known benchmark altitude

---

### 3. Elevation-Dependent Analysis

The Google framework uses mean metrics across all satellites. Breaking down by
elevation reveals antenna pattern and multipath characteristics:

**CN0 vs elevation fit:**
An ideal antenna in open sky should show CN0 increasing with elevation (shorter
ionospheric and tropospheric path). Plot CN0 against elevation and fit a curve:

```
CN0(el) ≈ CN0_zenith − A × exp(−B × elevation_deg)
```

Deviations from the smooth curve indicate:
- **Below the curve at specific azimuths** → obstructions or multipath from nearby
  structures
- **Flat CN0 regardless of elevation** → antenna gain pattern is non-standard
- **High CN0 at low elevation** → unusual multipath (signal bouncing off a flat surface)

**PR residuals vs elevation:**
Residuals should decrease with elevation (less atmosphere). An elevation-dependent
plot reveals the unmodelled tropospheric and ionospheric error.

---

### 4. Clock and Oscillator Stability Analysis

Beyond the single ΔClockBias std check, oscillator quality can be analysed more deeply:

**Allan Deviation:**
Compute the overlapping Allan deviation (OADEV) of the receiver clock bias time series.
This characterises oscillator noise types:
- **White phase noise** — dominates at short averaging times (< 0.1 s)
- **Flicker phase noise** — intermediate
- **White frequency noise** — random walk; dominates TCXO at > 1 s
- **Flicker frequency noise** — long-term drift

TCXO (typical in phones) has OADEV ~10⁻¹⁰ at 1 s averaging. OCXO (temperature-
controlled, used in geodetic receivers) achieves ~10⁻¹² — 100× more stable.

**HardwareClockDiscontinuityCount:**
While the accumulated count is not meaningful per session, comparing the count at
start vs end of a session reveals whether any resets occurred during logging.

---

### 5. Multipath Analysis

Multipath is signal reflection from nearby surfaces. It inflates pseudorange noise and
creates elevation-dependent CN0 anomalies.

**Methods to detect multipath:**

| Method | What you need | What it reveals |
|--------|--------------|-----------------|
| S-curve / PR noise vs elevation | PR residuals, elevation | Elevation below which multipath dominates |
| CN0 time series per SV | Status rows | Periodic CN0 oscillation = constructive/destructive multipath interference |
| Double-difference residuals | Two receivers at known baseline | Pure multipath after geometry removal |
| MP1 / MP2 linear combination | Dual-frequency PR + carrier | Classic multipath observable |

For a stationary receiver, any time-correlated PR residual that does not follow the
expected tropospheric model is likely multipath.

---

### 6. Interference and Jamming Detection

**AGC monitoring:**
`AgcDb` in Raw rows is a direct interference indicator. In a clean RF environment,
AGC is near 0 dB. Strong interference causes the AGC to attenuate heavily (large
negative values). Plot `AgcDb` over time per constellation to detect:
- Intermittent jamming (pulsed AGC drops)
- Narrowband interference (affects one FDMA channel but not others)
- Wideband jamming (all constellations affected simultaneously)

**CN0 anomalies:**
Sudden CN0 drops across all satellites simultaneously (not elevation-correlated) indicate
RF interference rather than obstruction.

**Spoofing indicators:**
- All satellites suddenly show identical pseudorange residuals (they all "fit" too well)
- Position jumps discontinuously while PRR (Doppler-derived velocity) shows no motion
- BiasUncertaintyNanos drops to near zero (spoofer is feeding a clean synthetic signal)

---

### 7. Time To First Fix (TTFF) Testing

The Google framework analyses only the steady-state quality of an established fix.
TTFF measures the **acquisition phase** — how quickly the device obtains its first
usable fix.

| Fix type | Typical TTFF | Condition |
|----------|-------------|-----------|
| Hot start | 1–3 s | Recent ephemeris + almanac + approximate position cached |
| Warm start | 10–30 s | Almanac known but ephemeris expired |
| Cold start | 30–90 s | No cached data |
| Assisted (SUPL/A-GNSS) | 1–5 s | Network provides ephemeris prediction |

**How to test:**
1. Clear GNSS cache (Settings → Location → developer option, or reboot)
2. Move to a new location (cold start)
3. Log with GnssLogger; note timestamp of first Fix row
4. Subtract app-start timestamp to get TTFF

A device that passes all 41 quality checks at steady state may still have poor TTFF
if its SUPL implementation is broken or its acquisition sensitivity is low.

---

### 8. Environmental Stress Testing

The 41-check framework is evaluated in open sky (best case). Real applications
need performance in challenging environments:

| Environment | What to measure | Expected degradation |
|-------------|----------------|----------------------|
| Urban canyon | CN0 drop, HDOP increase, outlier rate | CN0 −10 to −20 dBHz; HDOP > 3; outliers > 10% |
| Under trees | CN0 drop, multipath | CN0 −5 to −15 dBHz; elevated PR residuals |
| Indoor (near window) | Fix availability, CN0 | CN0 < 20 dBHz; frequent fix loss |
| Moving (walking) | PRR accuracy, ADR continuity | PRR should track actual speed; cycle slips increase |
| Moving (vehicle) | Doppler range, position trail accuracy | PRR up to ±800 m/s; check PRR clamping at ±500 m/s |

---

### 9. Multi-Device Comparison

The framework scores a device in isolation. Comparing multiple devices simultaneously
at the same location reveals **relative** performance:

**Setup:** Record with 2–3 devices simultaneously at the same location (within 1 m).
All devices see the same sky, same ionosphere, same multipath environment.

**What to compare:**
- CN0 difference at the same satellite/epoch → antenna + chip sensitivity difference
- BiasUncertaintyNanos → oscillator quality difference
- PRR residual noise → Doppler chain quality difference
- Fix scatter → position filter and weighting strategy differences
- ADR availability → HAL/firmware difference

This isolates hardware/firmware differences from environmental ones.

---

### 10. Diurnal and Seasonal Variation

GNSS quality metrics vary with time of day and season primarily due to ionospheric
changes:

| Time | Ionospheric condition | Effect on L1-only PR residuals |
|------|-----------------------|-------------------------------|
| Midnight–06:00 local | Low TEC, stable | Best PR residuals (~50–80 m std) |
| 06:00–10:00 | Rising TEC | PR residuals increasing |
| 10:00–14:00 | Peak TEC (especially equatorial) | Worst PR residuals (~100–150 m std) |
| After sunset | Possible scintillation (equatorial) | CN0 fluctuation, cycle slips |

For a comprehensive device assessment, record sessions at multiple times of day
(e.g. pre-dawn, midday, evening) and compare PR residual stds.

---

### 11. NTRIP / DGNSS Correction Testing

If the device supports external NMEA injection or NTRIP client apps:

1. Connect to a free CORS network (e.g. UNAVCO, IGS NTRIP, or national CORS)
2. Enable differential corrections in the GNSS app
3. Log with GnssLogger simultaneously
4. Check `SolutionType` in Fix rows: should change from 0 (GNSS-only) to 1 (DGNSS)
5. Check if `AccuracyMeters` improves

This tests the device's ability to use differential corrections — a key requirement
for sub-metre navigation applications.

---

### 12. RINEX Quality Checking Tools

Before post-processing, check the RINEX file quality with dedicated tools:

| Tool | What it checks |
|------|---------------|
| **TEQC** (UNAVCO) | Multipath indicators MP1/MP2, cycle slip ratio, obs/slip ratio, satellite availability |
| **anubis** (GOP-PECNY) | Comprehensive RINEX QC: cycle slips, SNR, satellite coverage, data gaps |
| **BNC** (BKG) | NTRIP client + RINEX quality monitor |
| **RTKLIB convbin** | Converts and checks raw binary to RINEX |

Running TEQC or anubis on the `.26o` file gives multipath observable values (MP1/MP2
in metres) and cycle slip rate — metrics not available in the Google 41-check framework.

---

### 13. Component-Level Assessment Summary

Each of the three hardware components has specific diagnostic metrics:

#### GNSS Chip

| Metric | Good | Poor |
|--------|------|------|
| CN0 top-4 / epoch | ≥ 40 dBHz | < 30 dBHz |
| % valid ADR | ≥ 50% | 0% (HAL not exposing phase) |
| L5 support | Present | Absent |
| Multi-constellation count | 5+ | ≤ 3 |
| PRR residual std | ≤ 0.1 m/s | > 0.5 m/s |
| % PR outliers | ≤ 1% | > 5% |
| GPS L1 PR residual std (single-freq) | ≤ 80 m | > 150 m |

#### Oscillator

| Metric | Good | Poor |
|--------|------|------|
| BiasUncertaintyNanos | 2–10 ns | > 100 ns |
| ΔClockBias std | ≤ 0.1 m/s | > 1 m/s |
| Time jitter std | 0.000 ms | > 1 ms |
| HardwareClockDiscontinuityCount change | 0 in session | > 0 |

#### Antenna

| Metric | Good | Poor |
|--------|------|------|
| CN0 at zenith | > 45 dBHz | < 30 dBHz |
| CN0 elevation slope | Smooth increase with elevation | Flat or irregular |
| CN0 azimuth variation | ≤ 5 dBHz | > 10 dBHz (obstructions / poor pattern) |
| Multipath MP1 (from RINEX TEQC) | < 0.5 m | > 1.5 m |
| PR outlier rate | 0% | > 5% |
