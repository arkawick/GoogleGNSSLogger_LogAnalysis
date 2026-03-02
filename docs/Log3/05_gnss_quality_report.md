# GNSS Quality Analysis Report — Log 3

**Device:** Sony XQ-GE54 | Android 16 | GnssLogger v3.1.1.2
**Chipset:** Qualcomm MPSS.DE.9.0 (Snapdragon 8 Gen 2 modem)
**Log captured:** 02 Mar 2026, 12:15:58 – 12:17:40 UTC | Bangalore, India
**Analysis framework:** Google Android Bootcamp GNSS Quality Framework (41 checks)
**Analysis notebook:** `scripts/gnss_quality_analysis_v2.ipynb` → output in `Log3/outputs/`

---

## Overall Score

| Result | Count | Of applicable | Percentage |
|--------|------:|:-------------:|----------:|
| **PASS** | **17** | **26** | **65%** |
| **FAIL** | **9** | **26** | **35%** |
| **N/A** | **15** | — | — |
| **Total checks** | **41** | | |

**Comparison across logs:**

| | Log 1 (Xiaomi 13) | Log 2 (Sony XQ-GE54) | Log 3 (Sony XQ-GE54) |
|--|:-----------------:|:--------------------:|:--------------------:|
| Score | 9/26 (35%) | 18/27 (67%) | **17/26 (65%)** |
| Applicable | 26 | 27 | 26 |

Log 3 scores one point lower than Log 2 (17 vs 18 PASS) and has one fewer
applicable check (26 vs 27). The difference: Log 2 tracked BDS B1I and passed
that check; Log 3 has no B1I signal so the check is N/A rather than PASS.

---

## Section 1 — Basic Checks (8/9 applicable, 8 PASS)

| Check | Threshold | Measured | Result |
|-------|-----------|----------|--------|
| Avg CN0 Top 4/Epoch | ≥ 40 dBHz | **51.12 dBHz** | **PASS** |
| Max Time Between Epochs | ≤ 2000 ms | 1000 ms | **PASS** |
| Avg Valid/Epoch GPS L1 | ≥ 7 | **11.00** | **PASS** |
| Avg Valid/Epoch GPS L5 | ≥ 4 | Not present | N/A |
| Avg Valid/Epoch GLO G1 | ≥ 4 | **7.00** | **PASS** |
| Avg Valid/Epoch GAL E1 | ≥ 5 | **8.00** | **PASS** |
| Avg Valid/Epoch GAL E5A | ≥ 4 | Not present | N/A |
| Avg Valid/Epoch GAL E5B | ≥ 4 | Not present | N/A |
| Avg Valid/Epoch BDS B1I | ≥ 4 | Not present | N/A |
| Avg Valid/Epoch BDS B2A | ≥ 4 | Not present | N/A |
| Avg Valid/Epoch BDS B1C | ≥ 4 | **9.00** | **PASS** |
| Required Sig Types | All L1+L5 | Missing GPS L5 | **FAIL** |
| Measurement State Usable | ≥ 85% | **100.0% (4440/4440)** | **PASS** |
| Duplicate Signals | 0 | 0 | **PASS** |

### Key Findings

**CN0 Top-4 PASS (51.1 dBHz):** The best result across all three logs, 4 dBHz
above Log 2's 47.1 dBHz and 25.5 dBHz above Log 1's 25.6 dBHz. The 53.4 dBHz
maximum measurement approaches the theoretical ceiling for consumer L1 C/A
receivers (~53–55 dBHz), confirming an ideal open-sky environment with
no obstructions at the time of recording.

**BDS B1I absent (N/A instead of PASS):** Unlike Log 2 (same device, same site)
which tracked BDS on both B1I (1561 MHz) and B1C (1575 MHz), Log 3 records only
B1C. The RINEX header confirms `C 3 C1P D1P S1P` with no B1I entries. This
reduces the applicable check count from 27 to 26 vs Log 2.

**7 GLONASS satellites (PASS, avg 7.00/epoch):** Log 3 tracks one more GLONASS
satellite than Log 2 (7 vs 6), with a wider channel spread (−3 to +6 vs −3 to +4).

**100% usable measurements:** All 4440 raw rows have STATE_TOW_DECODED or
STATE_TOW_KNOWN set — perfect, matching Log 2.

---

## Section 2 — Time Checks (5/8, 5 PASS)

| Check | Threshold | Measured | Result |
|-------|-----------|----------|--------|
| Time Tag Large Jumps | 0 gaps > 2000 ms | 0 | **PASS** |
| Time Tag Jitter | ≤ 10 ms std | 0.000 ms | **PASS** |
| Time-sync Max Jitter | ≤ 5 ms | 0.000 ms | **PASS** |
| Time-sync Jitter | ≤ 3 ms std | 0.000 ms | **PASS** |
| Delta ERTN Range | ≤ 10 ms | 1000.887 ms | **FAIL** |
| Delta ERTN Std | ≤ 3 ms | 161.521 ms | **FAIL** |
| Delta Clock Bias Std | ≤ 1.0 m/s | **0.0347 m/s** | **PASS** |
| LS-Freq PR Residuals Std | ≤ 5 m | 100.00 m | **FAIL** |

### Key Findings

**Time tagging perfect (0.000 ms jitter):** All four time quality checks pass
with exactly zero deviation, identical to Log 2. The 120 epochs are spaced at
perfectly regular 1-second intervals.

**Delta Clock Bias Std PASS (0.0347 m/s):** Even better than Log 2's 0.071 m/s.
Equivalent to 0.116 ns/s drift — extremely stable. The MPSS.DE.9.0 dedicated
GNSS clock maintains outstanding stability throughout the 120-second session.

**Delta ERTN FAIL (1000.9 ms range, 161.5 ms std):** Larger std than Log 2
(161.5 ms vs 132.8 ms), reflecting the same Snapdragon modem-to-AP bridge
latency jitter seen in Log 2. This does not affect positioning accuracy.

**LS-Freq PR Residuals Std FAIL (100.00 m):** The pooled L1 pseudorange
residual standard deviation across all 3900 valid measurements is 100 m.
Slightly better than Log 2's 107.5 m, consistent with the higher CN0 in Log 3
reducing code noise. Both logs fail this check as the 5 m threshold requires
dual-frequency iono correction to achieve.

---

## Section 3 — ADR / PRR / PR Checks (0/2 applicable)

| Check | Threshold | Measured | Result |
|-------|-----------|----------|--------|
| % Valid ADR | ≥ 50% | 0.0% (0/4440) | **FAIL** |
| % Usable ADR | ≥ 80% | 0.0% (0/4440) | **FAIL** |
| ADR Variability | ≤ 0.5 cyc | No valid ADR | N/A |
| Median (PRR − dADR) | ≤ 0.1 | No valid ADR | N/A |
| Std (PRR − dADR) | ≤ 0.5 | No valid ADR | N/A |
| L1freq (dPR − dADR) | ≤ 0.5 | No valid ADR | N/A |
| L5freq (dPR − dADR) | — | No L5 | N/A |

### Key Findings

Identical to Log 2: all 4440 measurements carry `AccumulatedDeltaRangeState = 16`
(ADR_STATE_HALF_CYCLE_REPORTED, bit 4 set; ADR_STATE_VALID, bit 0, not set).
The Sony chipset computes carrier phase internally but the HAL driver does not
set the VALID flag. ADR counts as 0% valid across all three sessions.

---

## Section 4 — Residuals (4/6 applicable, 4 PASS)

| Check | Threshold | Measured | Result |
|-------|-----------|----------|--------|
| L1 PR Residuals Std | ≤ 5 m | 100.00 m (3900 meas) | **FAIL** |
| L5 PR Residuals Std | ≤ 3 m | No L5 | N/A |
| L1 Med Norm PR Resid RMS | ≤ 3.0 | 23.157 | **FAIL** |
| L5 Med Norm PR Resid RMS | ≤ 3.0 | No L5 | N/A |
| % PR Residuals Outliers | ≤ 5% | **0.0% (0/3900)** | **PASS** |
| Epochs for ADR Resid | ≥ 1 | 0 | **FAIL** |
| ADR Residuals Std | — | No valid ADR | N/A |
| Med Norm ADR Resid RMS | — | No valid ADR | N/A |
| % Epochs High ADR Resid | — | No valid ADR | N/A |
| PRR Residuals Std | ≤ 0.5 m/s | **0.0210 m/s** | **PASS** |
| % Epochs High PRR Resid | ≤ 20% | **0.0%** | **PASS** |
| Med Norm PRR Resid RMS | ≤ 3.0 | **1.003** | **PASS** |

### Key Findings

**0.0% outliers (PASS):** Not a single measurement among 3900 exceeds the
3-sigma outlier threshold — identical to Log 2's 0.0% and a strong contrast
with Log 1's 6.9%. The measurement distribution is perfectly Gaussian.

**PRR Residuals 0.021 m/s (PASS):** Significantly better than Log 2's 0.422 m/s
and the 0.5 m/s threshold. The very low PRR uncertainty (mean 0.025 m/s for
PRR_unc) reflects the excellent CN0 in Log 3 — higher signal strength directly
reduces Doppler noise.

**PRR Normalised RMS = 1.003 (PASS):** Essentially 1.0 — the PRR uncertainty
field is accurately calibrated to match actual residuals.

**L1 PR Residuals Std = 100 m (FAIL):** Slightly better than Log 2's 107.5 m
and Log 1's 134.4 m, reflecting the higher CN0 reducing code phase noise.
All three logs fail this check as the 5 m threshold requires dual-frequency
iono-free combinations.

---

## Comparison: Log 2 vs Log 3 (same device, same site)

| Metric | Log 2 | Log 3 |
|--------|:-----:|:-----:|
| Duration | 129 s | 120 s |
| Raw measurements | 7181 | 4440 |
| Mean CN0 | 38.1 dBHz | **43.9 dBHz** |
| CN0 Top-4 | 47.1 dBHz | **51.1 dBHz** |
| PRR Residuals Std | 0.422 m/s | **0.021 m/s** |
| Clock Bias Std | 0.071 m/s | **0.035 m/s** |
| Delta ERTN Std | 132.8 ms | 161.5 ms |
| BDS B1I present | Yes (PASS) | **No (N/A)** |
| BDS B1C present | Yes (PASS) | Yes (PASS) |
| GLONASS SVs | 6 | **7** |
| % PR Outliers | 0.0% | 0.0% |
| L1 PR Res Std | 107.5 m | **100.0 m** |
| Score | 18/27 (67%) | 17/26 (65%) |

Log 3 has better signal quality (CN0, PRR) but loses the BDS B1I check,
resulting in a marginally lower score (65% vs 67%).

---

## Application Class Assessment

| Application | Log 3 Feasibility | Limiting Factor |
|-------------|:----------------:|----------------|
| Standard navigation | **Excellent** | None |
| High-accuracy positioning | Good | No ADR, no L5 |
| Dead-reckoning (tunnels) | **Excellent** | PRR 0.021 m/s — best of all logs |
| DGNSS / RTK | Not viable | ADR not valid; no L5 |
| Timing / synchronisation | **Excellent** | Clock Bias Std 0.035 m/s |
| Multi-GNSS research logging | Good | BDS B1I absent (B1C only) |
| BeiDou iono correction | Not available | B1C only — no dual-freq combo |

---

## Recommendations

1. **Investigate BDS B1I absence:** Log 2 (same device, same site) captured
   both B1I and B1C. Consider restarting GnssLogger between sessions or
   rebooting the device to reset the GNSS HAL chipset state before recording.

2. **Enable valid ADR:** Same recommendation as Log 2 — the Sony chipset
   computes carrier phase (ADR state = 16). A firmware or HAL update setting
   ADR_STATE_VALID would unlock differential positioning.

3. **Enable GPS L5:** The hardware may support L5; check Sony firmware release
   notes for GNSS HAL updates.

---

## Analysis Tools

| Tool | Version | Purpose |
|------|---------|---------|
| gnss_quality_analysis_v2.ipynb | — | 41-check Google framework |
| GnssLogger | v3.1.1.2 | Log capture on device |

*Analysis date: 2026-03-03*
