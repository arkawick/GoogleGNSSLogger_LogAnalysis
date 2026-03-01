# GNSS Quality Analysis Report

**Device:** Xiaomi 2201116PI (Xiaomi 13) | Android 13 | GnssLogger v3.1.1.2
**Chipset:** Qualcomm MPSS.HI.4.3.1 (Snapdragon 8 Gen 1 modem)
**Log captured:** 2026-02-25 17:55–17:56 UTC | Bangalore, India
**Analysis framework:** Google GNSS Quality Thresholds (35 metrics — legacy)
**Analysis notebook:** `scripts/gnss_quality_analysis.ipynb` (legacy) → output in `Log1/outputs/`

> **⚠ Framework note:** This report was produced with an earlier 35-metric framework.
> The current v2 41-check Google Android Bootcamp framework (used for Log2 and all
> future logs) scores Log1 at **9 / 26 applicable = 35%**.
> The lower v2 score reflects stricter thresholds and additional checks (Delta ERTN,
> LS-Freq PR Residuals, PRR Residuals, Normalised RMS) that are all FAIL for this
> chipset. For a like-for-like comparison with Log2, use the v2 scores:
> **Log1 = 9/26 (35%)** vs **Log2 = 18/27 (67%)**.
> See `scripts/gnss_quality_analysis_v2.ipynb` and `Log1/outputs/gnss_quality_analysis_v2_Log1.ipynb`.

---

## Overall Score (35-metric legacy framework)

| Result | Count | Percentage |
|--------|------:|----------:|
| **PASS** | **22** | **63%** |
| **FAIL** | **13** | **37%** |

The device demonstrates **solid basic GNSS capability** with multi-constellation
support and good satellite geometry, but has significant limitations in
carrier-phase support, L5 frequency, and Doppler measurement quality that
prevent it from reaching best-in-class DGNSS performance.

---

## Scorecard — All 35 Metrics

### Category A — Clock Quality (3/5 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| A1 | BiasUncertaintyNanos | < 40 ns | mean=96.3 ns, max=128.6 ns | **FAIL** |
| A2 | Clock discontinuities (session) | 0 new in session | 0 new (counter accumulated=1066 at boot) | **PASS** |
| A3 | LeapSecond reported | non-zero value | 18 s (correct for 2026) | **PASS** |
| A4 | Clock bias stability | No jumps > 1 s | Max jump = 0 ns (perfectly stable) | **PASS** |
| A5 | DriftUncertaintyNanosPerSecond reported | Present | mean = 22.1 ns/s | **FAIL** |

**Findings:**
- **A1 FAIL** — The Qualcomm MPSS.HI.4.3.1 chipset reports BiasUncertaintyNanos of
  75–129 ns, well above Google's 40 ns threshold. This is inherent to the
  dual-architecture (GNSS + cellular) modem clock and cannot be fixed by software.
  At 96 ns average, pseudorange uncertainty from clock alone is ~28.8 m — the
  primary bottleneck for single-frequency ranging accuracy.
- **A2 PASS** — Although the accumulated discontinuity counter reads 1066 (reflecting
  all resets since device boot), **no new clock jumps occurred during this recording
  session**, meaning the session-level clock was stable.
- **A5 FAIL** — DriftUncertaintyNanosPerSecond mean of 22.1 ns/s exceeds what
  high-precision receivers report (typically < 5 ns/s), though this value is
  characteristic of consumer-grade clocks.

---

### Category B — Tracking State Completeness (3/5 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| B1 | GPS STATE_TOW_DECODED rate | ≥ 99% | 100.0% (95/95) | **PASS** |
| B2 | GLONASS GLO_TOD_DECODED rate | ≥ 99% | 100.0% (83/83) | **PASS** |
| B3 | ReceivedSvTimeUncertaintyNanos | < 500 ns | max=181 ns, mean=59.6 ns | **PASS** |
| B4 | IsFullTracking field reported | Present in rows | Not reported (0/311) | **FAIL** |
| B5 | MultipathIndicator useful | Not all UNKNOWN | All UNKNOWN (0/311) | **FAIL** |

**Findings:**
- **B1/B2 PASS** — All GPS and GLONASS measurements have fully decoded time-of-week,
  meaning the receiver has established complete navigation message synchronisation.
  This confirms high-quality tracking of both constellations.
- **B3 PASS** — Satellite time uncertainty peaks at 181 ns and averages 59.6 ns across
  all 5 constellations — well under the 500 ns threshold. Galileo measurements have
  the highest uncertainty (mean 88.3 ns) due to their weaker signal in this environment.
- **B4 FAIL** — The `IsFullTracking` field is not populated by this Qualcomm driver.
  This field indicates whether the chipset is in duty-cycling (power-saving) mode or
  continuously tracking. Not reporting it prevents assessment of duty-cycle-induced
  measurement gaps.
- **B5 FAIL** — `MultipathIndicator` is always reported as UNKNOWN (0), meaning the
  chipset does not compute or expose a multipath detection metric. Urban environments
  such as Bangalore may introduce multipath errors that cannot be flagged automatically.

---

### Category C — Signal Quality / CN0 (4/6 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| C1 | Mean CN0 (all measurements) | ≥ 20 dB-Hz | 23.4 dB-Hz | **PASS** |
| C2 | Top-5 satellites CN0 mean | ≥ 25 dB-Hz | 31.5 dB-Hz | **PASS** |
| C3 | Fraction of meas with CN0 ≥ 25 dB-Hz | ≥ 50% | 33.4% | **FAIL** |
| C4 | Fraction of meas with CN0 ≥ 20 dB-Hz | ≥ 80% | 84.2% | **PASS** |
| C5 | BasebandCn0DbHz reported | 100% | 100% (311/311) | **PASS** |
| C6 | AGC (AgcDb) reported | ≥ 90% of meas | 99.0% (308/311) | **PASS** |

**Per-constellation CN0 breakdown:**

| Constellation | Mean CN0 | Max CN0 | % above 25 dB-Hz |
|--------------|--------:|-------:|------------------:|
| GPS | 22.2 dB-Hz | 31.3 | 24% |
| GLONASS | 25.0 dB-Hz | 31.8 | 45% |
| BeiDou | 24.4 dB-Hz | 29.6 | 51% |
| Galileo | 20.7 dB-Hz | 26.5 | 6% |
| QZSS | 23.3 dB-Hz | 27.2 | 19% |

**Findings:**
- **C3 FAIL** — Only 33% of measurements exceed the 25 dB-Hz quality threshold.
  This indicates **partial sky obstruction** (urban environment, nearby structures,
  or tree cover). The best 5 satellites (31.5 dB-Hz) are fully adequate, but the
  bulk of tracked satellites are weak. Galileo is particularly affected (only 6%
  above threshold), as its signal is weaker at this chipset's antenna.
- **C5 PASS** — BasebandCN0 is available for all measurements. The gap between
  composite CN0 (mean 23.4) and baseband CN0 (mean 19.5) is 3.9 dB, indicating
  ~4 dB of correlator gain — normal for this chipset.
- **C6 PASS** — AGC is reported for 99% of measurements. The AGC range (−1.32 to
  +0.69 dB) is narrow, indicating a stable RF environment with no interference or
  jamming during the recording.

---

### Category D — Pseudorange Rate / Doppler Quality (2/4 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| D1 | PRR available for all measurements | 100% | 100% (311/311) | **PASS** |
| D2 | PRR uncertainty mean ≤ 1 m/s | ≤ 1 m/s | 2.24 m/s | **FAIL** |
| D3 | PRR not clamped at ±500 m/s | < 5% clamped | 6.8% (21/311) | **FAIL** |
| D4 | PRR uncertainty max ≤ 5 m/s | ≤ 5 m/s | 15.3 m/s | **FAIL** |

**Findings:**
- **D2/D3/D4 FAIL** — This is a known limitation of the Qualcomm MPSS.HI
  chipset family. Three issues are present simultaneously:
  1. **PRR clamping at ±500 m/s:** 21 measurements (6.8%) have range rates
     within 5 m/s of the ±500 m/s clamp limit. Real GNSS satellite range rates
     at L1 are typically ±5 km/s projected, so this clamp introduces systematic
     bias for fast-moving satellites.
  2. **High PRR uncertainty:** Mean 2.24 m/s (threshold: 1.0 m/s) and maximum
     15.3 m/s (threshold: 5.0 m/s). This degrades velocity accuracy from the
     Doppler solution — expected velocity error > 2 m/s.
  3. These issues affect GNSS-based velocity estimation used in navigation apps,
     dead-reckoning, and velocity-aided positioning.

---

### Category E — Carrier Phase / ADR Quality (0/4 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| E1 | ADR measurements available | > 0 | 0/311 (0.0%) | **FAIL** |
| E2 | ADR availability rate ≥ 50% | ≥ 50% | 0.0% | **FAIL** |
| E3 | Cycle slip rate < 0.5% | < 0.5% | N/A (no ADR) | **FAIL** |
| E4 | ADR uncertainty ≤ 0.5 m | ≤ 0.5 m | N/A (no ADR) | **FAIL** |

**Findings:**
- **All ADR metrics FAIL** — This device exposes **zero carrier phase
  measurements**. The `AccumulatedDeltaRangeState` field is 0 (UNKNOWN) for
  all 311 measurements, meaning the chipset driver does not expose phase
  observables to Android.
- **Impact:** Without carrier phase (ADR), the device cannot support:
  - Differential GNSS (DGNSS)
  - RTK (Real-Time Kinematic) positioning
  - PPP (Precise Point Positioning)
  - Carrier-smoothed pseudoranges
  - Sub-metre positioning accuracy
- **Google recommendation:** For best DGNSS performance, devices must support
  L1 + L5 AND ADR. This device fails both requirements.
- **Note:** Some Qualcomm chipsets expose ADR in newer Android versions or with
  specific firmware builds. This may be a driver limitation rather than hardware.

---

### Category F — Feature & Frequency Support (6/8 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| F1 | L1 frequency support | Present | 1575.42, 1561.1, 1599.75–1602.0 MHz | **PASS** |
| F2 | L5 frequency support | Present | Not found in any measurement | **FAIL** |
| F3 | SatPvt ECEF position reported | ≥ 80% | 280/311 (90.0%) | **PASS** |
| F4 | SatClockBias reported | ≥ 80% | 280/311 (90.0%) | **PASS** |
| F5 | InterSignalBias reported | ≥ 50% non-zero | 185/311 (59.5%) | **PASS** |
| F6 | GPS constellation | Present | 95 measurements | **PASS** |
| F7 | Non-GPS constellation | ≥ 1 system | GLONASS+BeiDou+Galileo+QZSS | **PASS** |
| F8 | Klobuchar ionosphere model | 100% | 311/311 (100%) | **PASS** |

**Findings:**
- **F2 FAIL** — The device is **L1-only**. No L5 (1176.45 MHz) measurements were
  found for any constellation. L5 is critical for:
  - Iono-free combination (eliminates ~99% of ionospheric error)
  - Improved multipath rejection
  - DGNSS/PPP at cm-level accuracy
  This is the single biggest hardware limitation for precision GNSS applications.
- **F3/F4 PASS** — Satellite ECEF positions and clock biases are fully reported
  (90% of rows), enabling the receiver to compute an independent WLS position
  solution without almanac/ephemeris downloads.
- **F5 PASS** — Inter-signal bias is reported for 60% of measurements. Gaps
  correspond to early-session measurements before the receiver had complete
  calibration data.
- **F7 PASS** — Five constellations simultaneously tracked and used in fixes is
  excellent for a consumer device and greatly improves geometry and robustness.

---

### Category G — Fix Quality (3/3 PASS)

| ID | Metric | Threshold | Measured | Result |
|----|--------|-----------|----------|--------|
| G1 | CEP68 horizontal (stationary, open sky) | ≤ 3 m | CEP68 = 0.945 m | **PASS** |
| G2 | HDOP ≤ 2.0 in ≥ 95% fixes | ≥ 95% | 98% of fixes | **PASS** |
| G3 | Multi-constellation fix | ≥ 2 systems | 5 systems (GPS+GLO+BDS+GAL+QZSS) | **PASS** |

**Fix quality breakdown (stationary receiver, 44-second session):**

| Provider | Fixes | CEP50 | CEP68 | CEP95 | Mean Hacc | Mean Vacc |
|----------|------:|------:|------:|------:|----------:|----------:|
| GPS (raw GNSS) | 45 | 0.54 m | 0.95 m | 1.64 m | 10.9 m | 8.5 m |
| FLP (fused) | 46 | 2.14 m | 2.48 m | — | 11.8 m | 1.7 m |
| NLP (network) | 4 | 0.77 m | — | — | 12.8 m | 1.7 m |

**Findings:**
- **G1 PASS** — Actual position scatter (CEP68 = 0.945 m) is **excellent**, far
  better than the 3 m threshold. This demonstrates that the GNSS chip and
  antenna perform well despite the high clock bias uncertainty. The WLS solution
  effectively mitigates the clock error.
- **G2 PASS** — HDOP exceeded 2.0 in only 2% of fixes (one brief period at
  max HDOP = 2.6), indicating consistently good satellite geometry.
- **G3 PASS** — Up to 5 constellations contribute to each fix — the maximum
  achievable with this chipset's constellation support.
- **Reported vs actual accuracy:** The device reports mean horizontal accuracy of
  10.9 m (GPS provider), which is **10× more conservative** than the actual
  scatter of 0.95 m CEP68. Android's accuracy estimate includes unresolved
  error sources (BiasUncertainty, iono, etc.) — it is a worst-case bound, not
  an achieved-accuracy figure.
- **Altitude noise:** NMEA altitude standard deviation = 0.36 m — excellent for
  a single-frequency L1-only receiver, consistent with the good vertical geometry
  (VDOP = 0.80–0.88).

---

## Key Findings Summary

### Strengths (What Works Well)
1. **Excellent actual position accuracy** — CEP68 < 1 m for stationary test
2. **Full multi-constellation tracking** — All 5 systems active and contributing
3. **Perfect tracking state completeness** — 100% TOW_DECODED for all GPS/GLONASS
4. **SatPvt fully reported** — Satellite positions, velocities, and clock biases available
5. **AGC and BasebandCN0 fully reported** — Good RF environment monitoring
6. **Klobuchar model fully reported** — Iono correction data always available
7. **Clock stable within session** — No intra-session clock discontinuities
8. **Excellent satellite geometry** — HDOP 0.7, PDOP 1.0

### Weaknesses (Critical Fails)
1. **No carrier phase (ADR) — 0%** — Device cannot support DGNSS or sub-metre positioning
2. **No L5 support** — L1-only limits dual-frequency iono correction
3. **High BiasUncertaintyNanos (75–129 ns)** — Structural clock limitation of this chipset
4. **PRR clamping at ±500 m/s** — 6.8% of Doppler measurements saturated
5. **High PRR uncertainty (mean 2.24 m/s)** — Doppler velocity accuracy degraded
6. **Low CN0 fraction above 25 dB-Hz (33%)** — Partial sky obstruction at recording site
7. **MultipathIndicator always UNKNOWN** — No multipath detection

### Impact on Application Classes

| Application | Feasibility | Limiting Factor |
|-------------|:-----------:|----------------|
| Standard navigation (maps/routing) | Excellent | None significant |
| Sports tracking (running/cycling) | Good | PRR uncertainty affects velocity |
| Precision agriculture / survey | Not viable | No ADR, no L5 |
| DGNSS / RTK positioning | Not viable | No ADR, no L5 |
| Dead reckoning (in tunnels) | Moderate | PRR clamping degrades velocity |
| Timing / synchronisation | Good | Clock stable within session |
| Multi-GNSS research logging | Good | All 5 constellations available |

---

## Recommendations

### For This Device
1. **Enable ADR in newer firmware:** Check whether Qualcomm firmware updates or
   Android version upgrades expose carrier phase via the Android GNSS HAL.
2. **Improve recording environment:** Move to a more open-sky location to raise
   mean CN0 above 25 dB-Hz (currently 23.4 dB-Hz).
3. **Use relaxed bias filter (200 ns)** in analysis tools — the default 40 ns
   threshold excludes all measurements from this chipset.

### For Best DGNSS Performance (per Google guidance)
A device should ideally support:
- **L1 + L5 dual-frequency** → removes 99% of ionospheric error
- **ADR (carrier phase)** → enables cm-level differential positioning
- **BiasUncertaintyNanos < 40 ns** → high-quality raw measurements
- **PRR uncertainty < 1 m/s** → accurate velocity from Doppler

The Xiaomi 13 / Qualcomm MPSS.HI.4.3.1 combination currently meets only the
basic performance tier. A device such as the Pixel 6/7/8 (Tensor GNSS) or newer
Snapdragon X/8 Gen 3 platforms with explicit ADR+L5 exposure would meet the
full DGNSS requirement.

---

## Analysis Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| gnss-lib-py | 1.0.4 | Raw measurement parsing and filtering |
| pynmea2 | 1.19.0 | NMEA sentence parsing |
| gnss_quality_analysis.ipynb | — | This analysis (interactive notebook) |
| Google gnss_analysis.ipynb | — | Reference framework for 35 metrics |

*Analysis date: 2026-03-01*
