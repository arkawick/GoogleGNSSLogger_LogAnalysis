# GNSS Quality Framework — Parameters Reference

Complete record of all quality thresholds: their origin, history, and current values.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `thresholds.json` | Active thresholds loaded by the v2 notebook at runtime |
| `thresholds.csv` | Same data in CSV format for readability |
| `parameters_reference.md` | This file — full reference and history |

To change a threshold: edit `thresholds.json`, then rerun `python scripts/run_analysis.py LogN`.

---

## Framework overview

The v2 notebook (`gnss_quality_analysis_v2.ipynb`) implements a 41-check quality
framework derived from the **Google Android Bootcamp GNSS Quality Framework**.
The reference implementation is `scripts/gnss_analysis_original_reference.ipynb`
(Google internal tool, version **2026.01.29**, 32 checks).

Checks are grouped into 4 sections:

| Section | Checks | What it tests |
|---------|:------:|--------------|
| BASIC_CHECKS | 14 | Signal count, CN0, measurement state, duplicates |
| TIME | 8 | Clock jitter, time-sync, elapsed realtime stability |
| ADR_PRR_PR | 7 | Carrier phase validity, Doppler consistency, PR noise |
| RESIDUALS | 12 | Pseudorange, ADR, and PRR residual quality |

---

## Reference notebook constants (gnss_analysis_original_reference.ipynb v2026.01.29)

These are the raw values hardcoded in the Google reference notebook.
They are the authoritative source for all thresholds.

### BASE_CONF — Dynamic (open-sky, moving receiver)

```python
BASE_CONF = {
    # Basic Checks
    'USABLE_MSR_MIN_PCT':                        85,
    'TOP_4_SATS_MIN_AVG_ANTENNA_CN0':            40,
    'EPOCH_DELTA_TIME_MAX_SEC':                   2.15,

    # Time-sync (ElapsedRealtime vs GPS time)
    'DELTA_ELAPSED_NANOS_MAX_STD_MILLIS':         2.5,
    'DELTA_ELAPSED_NANOS_MAX_DIFFERENCE_MILLIS':  1,
    'TIME_SYNC_MAX_STD_MILLIS':                   2.5,
    'TIME_SYNC_MAX_DIFFERENCE_MILLIS':            2.2,

    # ADR (Accumulated Delta Range) validity
    'VALID_ADR_MIN_PCT':                          70,
    'USABLE_ADR_MIN_PCT':                         65,
    'MAX_PERCENT_ADR_VARIABILITY':                5.0,

    # Rate Bias (PRR - Delta(ADR))
    'RATE_BIASE_MAX_ABS_MEDIAN_MPS':              0.07,
    'RATE_BIASE_MAX_STD_MPS':                     0.25,

    # PR Noise (Delta(PR) - Delta(ADR))
    'MAX_RMS_L1_DELTA_PR_MINUS_DELTA_ADR_M':      7.0,
    'MAX_RMS_L5_DELTA_PR_MINUS_DELTA_ADR_M':      0.85,

    # Pseudorange (PR) residuals — center 94% of data
    'L1_PR_RESIDUAL_MAX_CENTER_STD_M':            6.5,
    'L5_PR_RESIDUAL_MAX_CENTER_STD_M':            4.0,
    'L1_NORMALIZED_PR_RESIDUAL_MAX_MEDIAN_M':     5.0,
    'L5_NORMALIZED_PR_RESIDUAL_MAX_MEDIAN_M':     4.5,
    'MAX_PERCENT_PR_RESIDUAL_OUTLIERS':           5.0,
    'CLOCK_BIAS_MAX_CENTER_STD_MPS':              2.0,

    # ADR residuals
    'ADR_RESIDUAL_MAX_CENTER_STD_M':              0.015,
    'NORMALIZED_ADR_RESIDUAL_MAX_MEDIAN_M':       0.025,
    'ADR_RESIDUAL_MAX_ABS_RESIDUAL_BAD_EPOCH_M':  0.15,
    'ADR_RESIDUAL_MAX_PCT_BAD_EPOCHS':            5,
    'ADR_RESIDUAL_MIN_EPOCHS_FOR_SUFFICIENT_STATS': 30,
    'MIN_ADR_SIGNALS_FOR_EPOCH_YES_GT':           3,
    'MIN_ADR_SIGNALS_FOR_EPOCH_NO_GT':            6,

    # PRR (Pseudorange Rate) residuals — center 94% of data
    'PRR_RESIDUAL_MAX_CENTER_STD_MPS':            0.21,
    'NORMALIZED_PRR_RESIDUAL_MAX_MEDIAN_MPS':     0.2,
    'PRR_RESIDUAL_MAX_ABS_RESIDUAL_BAD_EPOCH_MPS': 1.5,
    'PRR_RESIDUAL_MAX_PCT_BAD_EPOCHS':            28,

    # Time tag jitter
    'JITTER_MAX_STD_SEC':                         1e-3,
    'MAX_GPS_MILLIS_JUMP_NO_DISCONTINUITY_SEC':   0.1,

    # Required signal types (must each average >= 1/epoch)
    'SIG_TYPE_REQUIRED': ['GPS_L1', 'GAL_E1', 'GLO_G1', 'GPS_L5', 'GAL_E5A'],

    # Per-epoch signal count minimums
    'SIG_TYPE_PER_EPOCH_MIN_AVG': {
        'GPS_L1':  7.5,
        'GPS_L5':  3.5,
        'GLO_G1':  4.0,
        'QZS_J1':  1.0,
        'QZS_J5':  1.0,
        'BDS_B1C': 4.0,
        'BDS_B1I': 5.0,
        'BDS_B2A': 4.0,
        'GAL_E1':  5.0,
        'GAL_E5A': 4.5,
        'GAL_E5B': 4.5,
    },
}
```

### STATIC_CONF_OVERRIDES — Static trace (stricter)

Applied on top of BASE_CONF when `IS_STATIC_TRACE = True`:

```python
STATIC_CONF_OVERRIDES = {
    'VALID_ADR_MIN_PCT':               90,    # vs 70
    'USABLE_ADR_MIN_PCT':              86,    # vs 65
    'ADR_RESIDUAL_MAX_PCT_BAD_EPOCHS':  2,    # vs 5
    'PRR_RESIDUAL_MAX_CENTER_STD_MPS': 0.1,  # vs 0.21
    'PRR_RESIDUAL_MAX_PCT_BAD_EPOCHS':  2,   # vs 28
}
```

### Other reference constants

```python
# Filtering
MIN_CN0_ALLOWED_DBHZ               = 20      # minimum C/N0 for any analysis
MIN_CN0_ALLOWED_ADR_ANALYSIS_DBHZ  = 20      # minimum C/N0 for ADR analysis
MIN_EL_ALLOWED_CN0_ANALYSIS_DEG    = 5       # minimum elevation for CN0 analysis
MIN_ELEV_ALLOWED_FOR_ADR_ANALYSIS  = 20      # minimum elevation for ADR analysis
MIN_ELEV_DEG_FOR_RESIDUALS         = 20      # minimum elevation for WLS residuals

# WLS solver
MAX_ITERATIONS                     = 100
MAX_DEL_POS_FOR_NAV_M_WITH_TAU     = 10      # convergence threshold (m)
RAW_TO_FIX_TOL_MILLIS             = 30000    # match Fix rows to Raw epochs (ms)

# Duty-cycling rejection (PHONE only)
# If unique(HardwareClockDiscontinuityCount) / num_epochs > 0.10 → reject log
DUTY_CYCLE_RATIO_THRESHOLD         = 0.10

# CN0 quality bands
CNO_GOOD_DB                        = 38.0
CNO_MED_DB                         = 33.0
GPSGLO_DELTA_DB                    = 2.5     # expected GPS vs GLONASS CN0 difference
CNO_DEL_ANT_BB_DB                  = 4.0     # expected antenna vs baseband CN0 diff
```

---

## Threshold history

### v1 — Initial (project start, Log1 analysis)

First version of thresholds, set during initial project setup before alignment
with the Google reference notebook. Applied to: Log1, Log2, Log3 (initial runs).

| Key | Value | Op | Unit |
|-----|------:|:--:|------|
| cn0_top4 | 40.0 | >= | dBHz |
| max_epoch_gap | 2000.0 | <= | ms |
| avg_gps_l1 | 7.0 | >= | signals/epoch |
| avg_gps_l5 | 4.0 | >= | signals/epoch |
| avg_glo_g1 | 4.0 | >= | signals/epoch |
| avg_gal_e1 | 5.0 | >= | signals/epoch |
| avg_gal_e5a | 4.0 | >= | signals/epoch |
| avg_gal_e5b | 4.0 | >= | signals/epoch |
| avg_bds_b1i | 4.0 | >= | signals/epoch |
| avg_bds_b2a | 4.0 | >= | signals/epoch |
| avg_bds_b1c | 4.0 | >= | signals/epoch |
| req_sig_types | 1.0 | >= | of each required type |
| usable_pct | 85.0 | >= | % |
| dup_signals | 0 | == | count |
| large_jumps | 0 | == | count |
| jitter_std_ms | 10.0 | <= | ms std |
| timesync_max_ms | 5.0 | <= | ms |
| timesync_std_ms | 3.0 | <= | ms std |
| elapsed_range_ms | 10.0 | <= | ms |
| elapsed_std_ms | 3.0 | <= | ms std |
| clkbias_mps_std | 1.0 | <= | m/s |
| ls_pr_res_std_m | 5.0 | <= | m |
| pct_valid_adr | 50.0 | >= | % |
| pct_usable_adr | 80.0 | >= | % |
| adr_var_cyc | 0.5 | <= | cycles |
| prr_dadr_med | 0.1 | <= | m/s |
| prr_dadr_std | 0.5 | <= | m/s |
| l1_dpr_dadr | 0.5 | <= | m |
| l5_dpr_dadr | 0.5 | <= | m |
| l1_pr_res_std_m | 5.0 | <= | m |
| l5_pr_res_std_m | 3.0 | <= | m |
| l1_norm_rms | 3.0 | <= | dimensionless |
| l5_norm_rms | 3.0 | <= | dimensionless |
| pct_pr_outliers | 5.0 | <= | % |
| n_adr_epochs | 1 | >= | epochs |
| adr_res_std_cyc | 0.05 | <= | cycles |
| norm_adr_rms | 3.0 | <= | dimensionless |
| pct_high_adr_ep | 10.0 | <= | % |
| prr_res_std_mps | 0.5 | <= | m/s |
| pct_high_prr_ep | 20.0 | <= | % |
| norm_prr_rms | 3.0 | <= | dimensionless |

**Scores under v1:** Log1: 9/26 (35%), Log2: 18/27 (67%), Log3: 17/26 (65%)

---

### v2 — Aligned to Google reference v2026.01.29 (March 2026)

24 thresholds updated to match `gnss_analysis_original_reference.ipynb`.
Applied to: Log1, Log2, Log3 (rerun), Log4 (first run).

Changes from v1 (bold = current active value):

| Key | v1 | **v2 (current)** | Source (BASE_CONF key) | Direction |
|-----|---:|---:|---|:---:|
| avg_gps_l1 | 7.0 | **7.5** | `SIG_TYPE_PER_EPOCH_MIN_AVG['GPS_L1']` | stricter |
| avg_gps_l5 | 4.0 | **3.5** | `SIG_TYPE_PER_EPOCH_MIN_AVG['GPS_L5']` | looser |
| avg_gal_e5a | 4.0 | **4.5** | `SIG_TYPE_PER_EPOCH_MIN_AVG['GAL_E5A']` | stricter |
| avg_gal_e5b | 4.0 | **4.5** | `SIG_TYPE_PER_EPOCH_MIN_AVG['GAL_E5B']` | stricter |
| avg_bds_b1i | 4.0 | **5.0** | `SIG_TYPE_PER_EPOCH_MIN_AVG['BDS_B1I']` | stricter |
| timesync_max_ms | 5.0 | **2.2** | `TIME_SYNC_MAX_DIFFERENCE_MILLIS` | stricter |
| timesync_std_ms | 3.0 | **2.5** | `TIME_SYNC_MAX_STD_MILLIS` | stricter |
| elapsed_range_ms | 10.0 | **1.0** | `DELTA_ELAPSED_NANOS_MAX_DIFFERENCE_MILLIS` | stricter |
| elapsed_std_ms | 3.0 | **2.5** | `DELTA_ELAPSED_NANOS_MAX_STD_MILLIS` | stricter |
| clkbias_mps_std | 1.0 | **2.0** | `CLOCK_BIAS_MAX_CENTER_STD_MPS` | looser |
| pct_valid_adr | 50.0 | **70.0** | `VALID_ADR_MIN_PCT` | stricter |
| pct_usable_adr | 80.0 | **65.0** | `USABLE_ADR_MIN_PCT` | looser |
| prr_dadr_med | 0.1 | **0.07** | `RATE_BIASE_MAX_ABS_MEDIAN_MPS` | stricter |
| prr_dadr_std | 0.5 | **0.25** | `RATE_BIASE_MAX_STD_MPS` | stricter |
| l1_dpr_dadr | 0.5 | **7.0** | `MAX_RMS_L1_DELTA_PR_MINUS_DELTA_ADR_M` | looser |
| l5_dpr_dadr | 0.5 | **0.85** | `MAX_RMS_L5_DELTA_PR_MINUS_DELTA_ADR_M` | looser |
| l1_pr_res_std_m | 5.0 | **6.5** | `L1_PR_RESIDUAL_MAX_CENTER_STD_M` | looser |
| l5_pr_res_std_m | 3.0 | **4.0** | `L5_PR_RESIDUAL_MAX_CENTER_STD_M` | looser |
| l1_norm_rms | 3.0 | **5.0** | `L1_NORMALIZED_PR_RESIDUAL_MAX_MEDIAN_M` | looser |
| l5_norm_rms | 3.0 | **4.5** | `L5_NORMALIZED_PR_RESIDUAL_MAX_MEDIAN_M` | looser |
| adr_res_std_cyc | 0.05 | **0.079** | `ADR_RESIDUAL_MAX_CENTER_STD_M`=0.015 m ÷ 0.1903 m/cycle | looser |
| pct_high_adr_ep | 10.0 | **5.0** | `ADR_RESIDUAL_MAX_PCT_BAD_EPOCHS` | stricter |
| prr_res_std_mps | 0.5 | **0.21** | `PRR_RESIDUAL_MAX_CENTER_STD_MPS` | stricter |
| pct_high_prr_ep | 20.0 | **28.0** | `PRR_RESIDUAL_MAX_PCT_BAD_EPOCHS` | looser |

Unchanged from v1 (14 checks): `cn0_top4`, `max_epoch_gap`, `avg_glo_g1`, `avg_gal_e1`,
`avg_bds_b2a`, `avg_bds_b1c`, `req_sig_types`, `usable_pct`, `dup_signals`, `large_jumps`,
`jitter_std_ms`, `ls_pr_res_std_m`, `adr_var_cyc`, `pct_pr_outliers`, `n_adr_epochs`,
`norm_adr_rms`, `norm_prr_rms`

**Scores under v2:** Log1: 10/26 (38%), Log2: 17/27 (63%), Log3: 17/26 (65%), Log4: 15/26 (58%)

---

## Notes on unit differences (v2 notebook vs reference notebook)

Some checks exist in both but use different units or computation methods:

| Check | v2 notebook | Reference notebook | Note |
|-------|------------|-------------------|------|
| ADR residual std | `adr_res_std_cyc` in **cycles** | `ADR_RESIDUAL_MAX_CENTER_STD_M` in **metres** | Converted: 0.015 m ÷ 0.1903 m/cycle ≈ 0.079 cycles (GPS L1 wavelength) |
| Normalized ADR RMS | dimensionless (ratio to std) | in metres | Different normalization — not directly comparable |
| Normalized PRR RMS | dimensionless (ratio to std) | in m/s | Different normalization — not directly comparable |
| LS PR residuals | TIME section (clock-only LS fit) | RESIDUALS section (full position+clock) | Different computation — kept at 5.0 m |

---

## Checks present in v2 but not in the reference notebook (41 vs 32)

The v2 notebook has 9 additional checks not in the 32-check reference:

| Key | Name | Why added |
|-----|------|-----------|
| `ls_pr_res_std_m` | LS-Freq PR Residuals Std (TIME section) | Clock-only LS fit as a time quality proxy |
| `avg_bds_b2a` | Avg Valid Per Epoch (BDS_B2A) | BDS second frequency coverage |
| `avg_bds_b1c` | Avg Valid Per Epoch (BDS_B1C) | BDS B1C (newer signal type) |
| `avg_gal_e5b` | Avg Valid Per Epoch (GAL_E5B) | Galileo E5B coverage |
| `n_adr_epochs` | Num Epochs for ADR Residual Analysis | Guard check before ADR residual computation |
| `norm_adr_rms` | Median Normalized ADR Residual RMS | ADR uncertainty calibration check |
| `norm_prr_rms` | Median Normalized PRR Residual RMS | PRR uncertainty calibration check |
| `adr_var_cyc` | ADR Variability (cycles) | Epoch-level ADR consistency |
| `pct_pr_outliers` | Percent PR Residuals Outliers | Large pseudorange error detection |
