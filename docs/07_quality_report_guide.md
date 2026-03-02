# Quality Report Guide — How to Read a Quality Scorecard

This document explains how to interpret the `LogN/05_gnss_quality_report.md` file
and the scorecard table produced by the analysis notebook. It covers what each of
the 41 checks tests, why it matters, what a failure means, and whether it can be
fixed.

For per-log results, see:
- `docs/LogN/05_gnss_quality_report.md` — actual check results for that log
- `docs/05_gnss_observables.md` — what PR, PRR, and ADR are
- `docs/08_gnss_quality_framework.md` — the framework context and extended analysis

---

## Understanding the Score

```
Score = PASS count / applicable count × 100%
```

| Term | Meaning |
|------|---------|
| **PASS** | Metric met the threshold |
| **FAIL** | Metric did not meet the threshold |
| **N/A** | Check not applicable — the required signal or feature is absent for this device/session (e.g. no L5, no ADR, no BDS B1I) |
| **Applicable** | PASS + FAIL only (N/A is excluded from the denominator) |

A score of 65% means 65% of the checks that could be evaluated were passed. N/A
checks are not penalised — they reflect hardware or session scope, not failures.

### Two types of failure

| Type | Description | Can be fixed? |
|------|-------------|---------------|
| **Structural fail** | Caused by a hardware or HAL limitation. Same result every session on this device. | Requires firmware/HAL update or different hardware |
| **Environmental fail** | Caused by sky conditions, time of day, or ionosphere. Varies session to session. | Yes — record at better time, location, or duration |

---

## Section 1 — Basic Checks (14 checks)

These verify that the raw measurement data is fundamentally usable.

---

### CN0 Top-4 per Epoch `cn0_top4` ≥ 40 dBHz

**What it measures:** Mean of the 4 highest CN0 values per epoch, averaged across
all epochs. Focuses on the best signals the device can receive.

**Why it matters:** CN0 directly determines pseudorange and Doppler noise. Weak CN0
means noisy measurements, poor residuals, and reduced satellite availability.

**What a FAIL means:**
- < 40 dBHz → obstructed sky, indoor/partial-indoor recording, or weak antenna/chip
- < 30 dBHz → very poor environment; most checks will cascade-fail

**Fix:** Record outdoors with full open-sky view. Time of day matters — mid-elevation
satellites give higher CN0 than low-elevation ones. If it still fails in open sky,
the device's antenna or chip sensitivity is limited.

---

### Max Time Between Epochs `max_epoch_gap` ≤ 2000 ms

**What it measures:** Largest gap between consecutive measurement epochs.

**Why it matters:** Gaps interrupt continuous tracking. > 2 s gaps cause PRR
integration errors and ADR cycle slips.

**What a FAIL means:** The logging session had at least one > 2 s interruption —
app paused, device entered doze mode, or signal was lost briefly.

**Fix:** Keep the screen on during logging, disable battery optimisation for GnssLogger,
record in open sky.

---

### Avg Valid per Epoch — per constellation/band

`avg_gps_l1` ≥ 7 | `avg_glo_g1` ≥ 4 | `avg_gal_e1` ≥ 5 | `avg_bds_b1c` ≥ 4 | etc.

**What it measures:** Average number of satellites with valid (STATE_TOW_DECODED)
measurements per epoch for each constellation and frequency band.

**Why it matters:** More satellites = better geometry = lower DOP = higher position accuracy.
Each threshold represents the minimum for a reliable position solution from that constellation.

**What a FAIL means:**
- GPS L1 < 7 → very restricted sky; GPS alone cannot give a 3D fix reliably
- GLO/GAL/BDS below threshold → partial sky blockage for that constellation

**Fix:** Open-sky environment. Some constellations (e.g. QZSS) are only visible from
certain regions — these checks are N/A automatically if the signal is absent.

---

### Required Signal Types `req_sig_types`

**What it measures:** Whether all required signal types (GPS L1+L5, GAL E1+E5A/E5B,
BDS B1I+B2A+B1C, GLO G1) average at least 1 signal per epoch.

**Why it matters:** Missing signal types (especially L5) prevent dual-frequency iono
correction and reduce positioning capability.

**What a FAIL means:** GPS L5 (1176.45 MHz) is missing — the most common failure.
This is a structural fail on virtually all current Android devices.

**Fix:** Hardware/HAL update required. GPS L5 support is present in some newer chipsets
but often not enabled in the Android HAL.

---

### Measurement State Usable `usable_pct` ≥ 85%

**What it measures:** Percentage of Raw rows where `State` has `STATE_TOW_DECODED`
(bit 3) or `STATE_TOW_KNOWN` (bit 14) set.

**Why it matters:** Only measurements with TOW decoded/known provide a valid pseudorange.
Rows without this flag cannot be used for positioning.

**What a FAIL means:**
- < 85% usable → many measurements are in acquisition phase without completed TOW decode
- Common at session start (first 5–10 s) before the receiver has locked on

**Fix:** Let the receiver run for > 30 s before recording, or increase session length
to dilute the startup phase.

---

### Duplicate Signals `dup_signals` = 0

**What it measures:** Number of epochs where the same satellite SVID + frequency
appears more than once.

**Why it matters:** Duplicates indicate a HAL bug. Processing software that naively
averages or sums duplicates will get incorrect results.

**What a FAIL means:** A HAL or GnssLogger bug on this device/version.

**Fix:** Update GnssLogger or the device firmware.

---

## Section 2 — Time Checks (8 checks)

These verify the receiver's time reference quality — critical for pseudorange accuracy.

---

### Time Tag Large Jumps `large_jumps` = 0

**What it measures:** Number of epoch-to-epoch time gaps > 2000 ms.

Same as `max_epoch_gap` above but as a count rather than maximum.

---

### Time Tag Jitter `jitter_std_ms` ≤ 10 ms

**What it measures:** Standard deviation of the inter-epoch time intervals
(ideally all exactly 1000 ms).

**What a FAIL means:** The hardware clock is not stepping epochs at a regular rate.
This is rare on modern chipsets.

---

### Time-sync Max Jitter `timesync_max_ms` ≤ 5 ms

**What it measures:** Maximum deviation from the 1-second nominal epoch interval
in the hardware clock domain.

---

### Time-sync Jitter `timesync_std_ms` ≤ 3 ms

**What it measures:** Standard deviation of hardware clock epoch jitter.

**Combined time jitter note:** 0.000 ms for all three time jitter checks is
normal and expected for a modern dedicated GNSS chipset — the hardware oscillator
maintains very stable 1-second epoch timing.

---

### Delta ERTN Range `elapsed_range_ms` ≤ 10 ms

**What it measures:** Range (max − min) of the delta-ElapsedRealtimeNanos across
all epochs. `ElapsedRealtimeNanos` is the Android system monotonic clock, separate
from the GNSS hardware clock.

**What a FAIL means:** The latency between the hardware GNSS measurement and the
Android AP (application processor) varies by more than 10 ms. This is a **modem-to-AP
bridge latency** issue, not a GNSS measurement quality issue.

**Fix:** This is a structural fail on Qualcomm Snapdragon devices — the modem and
AP clocks have inherent jitter in the IPC bridge. It does not affect positioning
accuracy.

---

### Delta ERTN Std `elapsed_std_ms` ≤ 3 ms

**What it measures:** Standard deviation of the delta-ElapsedRealtimeNanos jitter.

Same root cause as `elapsed_range_ms`. Both checks fail together on devices with
high modem-to-AP latency variation. Both are structural fails on affected chipsets.

---

### Delta Clock Bias Std `clkbias_mps_std` ≤ 1.0 m/s

**What it measures:** Standard deviation of the receiver clock bias drift, expressed
in metres per second. Computed as `d(FullBiasNanos + BiasNanos)/dt × c`.

**Why it matters:** A stable oscillator has low clock drift variance. High variance
means the receiver is constantly re-estimating its clock, adding noise to pseudoranges.

**What a FAIL means (> 1.0 m/s):**
- Unstable oscillator (modem-integrated chipset, MPSS.HI class)
- Clock reset occurred during the session

**What a good value looks like:** Dedicated GNSS chipsets typically achieve
0.02–0.10 m/s — well inside the threshold.

---

### LS-Freq PR Residuals Std `ls_pr_res_std_m` ≤ 5 m

**What it measures:** Standard deviation of L1 pseudorange residuals from a
least-squares clock-only fit, pooled across all constellations.

**Why it matters:** Should be small (< 5 m) only if iono is corrected. Single-frequency
L1-only receivers have ~5–15 m of uncorrected iono → residuals of 50–150 m.

**What a FAIL means:** Almost always a structural fail on single-frequency devices.
Dual-frequency (L1+L5) iono-free combinations reduce this to < 5 m.

**Fix:** Requires L5 support (hardware + HAL). Currently structural fail on most Android.

---

## Section 3 — ADR / PRR / PR Checks (7 checks)

These test carrier phase (ADR), Doppler (PRR), and pseudorange (PR) cross-consistency.

---

### Percent Valid ADR `pct_valid_adr` ≥ 50%

**What it measures:** Percentage of Raw rows where `AccumulatedDeltaRangeState` bit 0
(`ADR_STATE_VALID`) is set.

**Why it matters:** Valid ADR is the prerequisite for all carrier-phase-based positioning.
Without it, RTK, PPP, and carrier smoothing are not possible.

**What a FAIL means:**
- 0% → either no ADR tracking at all (state=0, older/integrated chipsets) or
  ADR computed but HAL not setting VALID flag (state=16, common on Sony/Qualcomm MPSS.DE)
- Both cases are structural fails — firmware/HAL update required

---

### Percent Usable ADR `pct_usable_adr` ≥ 80%

**What it measures:** Of the valid ADR measurements, what percentage are also free
from resets and cycle slips.

**What a FAIL means:** Even when ADR is valid, too many cycle slips break continuity.
Common in obstructed environments or on devices with marginal phase tracking.

---

### ADR Variability `adr_var_cyc` ≤ 0.5 cycles

**What it measures:** Median absolute deviation of ADR residuals within each epoch,
across all satellites. Tests epoch-to-epoch phase consistency.

**N/A condition:** No valid ADR → automatically N/A.

---

### Median (PRR − ΔADR) `prr_dadr_med` ≤ 0.1 m/s

**What it measures:** The median difference between the Doppler-derived range rate
(PRR) and the carrier-phase-derived range rate (ΔADR). Should be near zero because
both measure the same physical quantity.

**Why it matters:** A systematic offset indicates a half-cycle bias in ADR, a Doppler
scale error, or inter-signal bias.

**N/A condition:** No valid ADR.

---

### Std (PRR − ΔADR) `prr_dadr_std` ≤ 0.5 m/s

**What it measures:** Standard deviation of (PRR − ΔADR). Measures consistency between
Doppler and phase rate.

**N/A condition:** No valid ADR.

---

### L1 ΔPR − ΔADR `l1_dpr_dadr` ≤ 0.5 m

**What it measures:** Median absolute deviation of (epoch-to-epoch pseudorange change
minus epoch-to-epoch ADR change) on L1. Should be near zero if PR and phase are
consistent.

**Why it matters:** Detects large code-phase vs carrier-phase inconsistency that
would prevent carrier smoothing.

**N/A condition:** No valid ADR.

---

### L5 ΔPR − ΔADR `l5_dpr_dadr` ≤ 0.5 m

Same as L1 version but for L5 frequency. **N/A** on virtually all current Android
devices (no L5).

---

## Section 4 — Residuals (12 checks)

Residual checks verify measurement quality after fitting the position/velocity solution.

---

### L1 PR Residuals Std `l1_pr_res_std_m` ≤ 5 m

**What it measures:** Standard deviation of L1 pseudorange residuals after removing
the estimated receiver position and clock.

**Why it matters:** The 5 m threshold requires dual-frequency iono correction. Single-
frequency L1 residuals are 50–150 m (dominated by unmodelled ionosphere).

**What a FAIL means:** Almost always structural (no L5, no iono correction).

---

### L5 PR Residuals Std `l5_pr_res_std_m` ≤ 3 m

**N/A** on almost all current Android devices (no L5 signal).

When L5 is present and the iono-free L1+L5 combination is applied, this checks the
residual noise of the corrected pseudorange. The 3 m threshold reflects the lower
noise of L5 civil signals.

---

### L1 Median Normalised PR Residual RMS `l1_norm_rms` ≤ 3.0

**What it measures:** RMS of L1 PR residuals divided by the reported pseudorange
uncertainty (`ReceivedSvTimeUncertaintyNanos × c`). Should be ~1.0 if the chipset's
uncertainty model is well-calibrated.

**What the values mean:**

| Value | Interpretation |
|-------|----------------|
| ~1.0 | Uncertainty model accurate — reported uncertainty matches actual noise |
| > 3.0 | Uncertainty underestimated — chipset too confident; or residuals inflated by iono |
| < 0.5 | Uncertainty overestimated — chipset too conservative |

**What a FAIL means (> 3.0):** Single-frequency iono inflates the residuals far beyond
the code uncertainty. Structural fail without iono correction.

---

### Percent PR Residuals Outliers `pct_pr_outliers` ≤ 5%

**What it measures:** Percentage of L1 pseudorange residuals exceeding 3-sigma of
the per-epoch residual distribution.

**Why it matters:** Outliers indicate faulty measurements — multipath, cycle slips,
signal interference, or corrupt data rows. A receiver should detect and exclude these.

**What a FAIL means (> 5%):** High multipath, poor environment, or corrupted measurements.

**What a PASS means (0%):** Even if overall residuals are large (iono), their distribution
is Gaussian with no outlier tails. This is typical of a clean open-sky session.

---

### Num Epochs for ADR Residual Analysis `n_adr_epochs` ≥ 1

**What it measures:** Whether there is at least one epoch with enough valid ADR
measurements to compute ADR residuals.

**What a FAIL means:** No valid ADR at all → 0 usable epochs. Structural fail.

**N/A condition:** The ADR residual, normalised RMS, and high-epoch-rate checks below
are all N/A when this check fails.

---

### ADR Residuals Std `adr_res_std_cyc` ≤ 0.05 cycles

**What it measures:** Standard deviation of carrier-phase residuals after removing
geometry (position + satellite motion). 0.05 cycles at L1 = ~9.5 mm.

**N/A condition:** No valid ADR.

**What a PASS means:** Carrier phase is tracking continuously with sub-centimetre noise —
the precondition for RTK.

---

### Median Normalised ADR Residual RMS `norm_adr_rms` ≤ 3.0

Same interpretation as `l1_norm_rms` but for carrier phase. Should be ~1.0 when the
chipset's ADR uncertainty is well-calibrated.

**N/A condition:** No valid ADR.

---

### Percent Epochs with High ADR Residuals `pct_high_adr_ep` ≤ 10%

**What it measures:** Percentage of epochs where the ADR residual RMS exceeds 3×
the median. Detects intermittent cycle-slip epochs.

**N/A condition:** No valid ADR.

---

### PRR Residuals Std `prr_res_std_mps` ≤ 0.5 m/s

**What it measures:** Standard deviation of Doppler residuals after removing the
estimated receiver velocity and clock drift.

**Why it matters:** PRR residuals are the cleanest noise indicator in GNSS — unaffected
by integer ambiguity and only weakly affected by ionosphere. Low PRR std confirms
both the Doppler measurement quality and the velocity solution accuracy.

**What the values mean:**

| PRR std | Quality |
|---------|---------|
| < 0.05 m/s | Outstanding — dedicated chipset, high CN0 |
| 0.05–0.2 m/s | Good — typical open-sky MPSS.DE chipset |
| 0.2–0.5 m/s | Acceptable — passes threshold |
| > 0.5 m/s | FAIL — noisy Doppler, weak signals, or PRR clamping at ±500 m/s |

**What a FAIL means:**
- Low CN0 → noisy Doppler
- PRR clamped at ±500 m/s (modem-integrated chipset firmware limit)
- Device was moving rapidly during the session

---

### Percent Epochs with High PRR Residuals `pct_high_prr_ep` ≤ 20%

**What it measures:** Percentage of epochs where PRR residual RMS exceeds 3× the
session median. Detects intermittent Doppler spikes.

**What a FAIL means:** Intermittent noise bursts in Doppler — possible signal interference,
rapid motion episodes, or ±500 m/s clamping artefacts.

---

### Median Normalised PRR Residual RMS `norm_prr_rms` ≤ 3.0

**What it measures:** PRR residuals divided by `PseudorangeRateUncertaintyMetersPerSecond`.
Should be ~1.0 if the chipset's uncertainty model is calibrated.

**What a value near 1.0 means:** The chipset accurately knows its own Doppler noise
level. This is the gold standard for uncertainty calibration.

**What > 3.0 means:** The uncertainty field underestimates actual Doppler noise.
The velocity solution will over-weight these measurements.

---

## Failure Classification Summary

| Check | Structural fail? | Common cause of fail |
|-------|:----------------:|----------------------|
| `cn0_top4` | No | Poor sky environment |
| `max_epoch_gap` | No | Doze mode / obstruction |
| `avg_gps_l1` etc. | No | Sky blockage |
| `req_sig_types` (L5) | **Yes** | HAL does not expose L5 |
| `usable_pct` | No | Short session / indoor |
| `dup_signals` | Maybe | HAL bug |
| Time jitter (3 checks) | No | Rare on modern chips |
| `elapsed_range_ms` | **Yes** | Modem-to-AP bridge latency |
| `elapsed_std_ms` | **Yes** | Same as above |
| `clkbias_mps_std` | Maybe | Modem-integrated oscillator |
| `ls_pr_res_std_m` | **Yes** | No iono correction (no L5) |
| `pct_valid_adr` | **Yes** | HAL does not set VALID flag |
| `pct_usable_adr` | **Yes** | Same |
| ADR consistency (4 checks) | **Yes** | No valid ADR |
| `l1_pr_res_std_m` | **Yes** | No iono correction (no L5) |
| `l1_norm_rms` | **Yes** | Iono inflates vs code uncertainty |
| `pct_pr_outliers` | No | Multipath / poor environment |
| `n_adr_epochs` | **Yes** | No valid ADR |
| ADR residual checks (3) | **Yes** | No valid ADR |
| `prr_res_std_mps` | No | Low CN0 / PRR clamping |
| `pct_high_prr_ep` | No | Intermittent interference |
| `norm_prr_rms` | Maybe | Poorly calibrated PRR uncertainty |

---

## Application Class Interpretation

Based on the check results, assess suitability for each application:

| Application | Minimum requirements | Key checks |
|------------|---------------------|-----------|
| Standard navigation (turn-by-turn) | CN0 top-4 PASS, GPS L1 count PASS | `cn0_top4`, `avg_gps_l1`, `usable_pct` |
| Dead-reckoning (tunnel continuity) | Low PRR std, stable clock | `prr_res_std_mps`, `clkbias_mps_std` |
| High-accuracy (sub-metre) | PASS most checks, low PR outliers | `pct_pr_outliers`, `norm_prr_rms` |
| DGNSS / RTK | Valid ADR + L5 | `pct_valid_adr`, `req_sig_types` — currently structural fails |
| Timing / synchronisation | Stable clock bias | `clkbias_mps_std`, time jitter checks |
| Multi-GNSS research logging | All constellations present | `avg_glo_g1`, `avg_gal_e1`, `avg_bds_b1c` |
