# GNSS Observables — PR, PRR, and ADR

These are the three fundamental measurable quantities that a GNSS receiver exposes.
Every quality check in the framework ultimately tests one of them.

---

## PR — Pseudorange

The **measured distance** from the receiver to the satellite, in metres.

"Pseudo" because it is not the true geometric distance — it is corrupted by several
error sources:

```
PR = true_range
   + receiver_clock_error × c
   + satellite_clock_error × c
   + ionospheric_delay
   + tropospheric_delay
   + multipath
   + code_noise
```

### How it is computed

The receiver timestamps when it receives the signal and compares that to the timestamp
encoded inside the signal (when the satellite transmitted it):

```
signal_travel_time = receive_time − transmit_time
PR = signal_travel_time × speed_of_light
```

### Typical values

| Quantity | Value |
|----------|-------|
| Range (MEO satellites) | 20 000–26 000 km |
| Range (GEO/IGSO satellites) | 36 000–42 000 km |
| Code noise (L1 C/A, good chipset) | 0.5–3 m (1-sigma) |
| Ionospheric delay (L1, mid-lat) | 2–15 m (single-frequency) |
| Tropospheric delay | 2–25 m (elevation-dependent) |

### What it is used for

- **Position estimation** — 4 pseudoranges give 4 unknowns (X, Y, Z, receiver clock)
- **Differential positioning (DGNSS)** — PR errors largely cancel between nearby receivers
- **Quality checks** — PR residuals (measured PR minus modelled PR) reveal noise, biases, and outliers

### In GnssLogger

Column: `ReceivedSvTimeNanos` (satellite transmit time) combined with `TimeNanos`,
`FullBiasNanos`, `BiasNanos` (receiver time). The computed pseudorange also requires
`SvClockBiasMeters` correction (add, not subtract).

### In RINEX

Observable codes: `C1C` (GPS/GLO/GAL/QZSS L1), `C2I` (BeiDou B1I), `C1P` (BeiDou B1C),
`C5I` (L5/E5a), etc.

---

## PRR — Pseudorange Rate

The **rate of change of the pseudorange**, in m/s. It is derived from the **Doppler
frequency shift** — the apparent change in signal frequency caused by the relative
velocity between the satellite and the receiver.

```
PRR = −Doppler_Hz × wavelength
    = −Doppler_Hz × (c / carrier_frequency)
```

- **Negative PRR** → satellite approaching (range decreasing, signal frequency higher than nominal)
- **Positive PRR** → satellite receding (range increasing, signal frequency lower than nominal)

### Why "pseudo" range rate

Like pseudorange, the measured range rate also includes the receiver clock drift:

```
PRR_measured = true_range_rate + receiver_clock_drift × c
```

However the ionosphere has only a **second-order effect** on Doppler (it affects the
carrier frequency proportionally to its time derivative), making PRR far less sensitive
to ionospheric conditions than PR.

### Typical values

| Quantity | Value |
|----------|-------|
| PRR magnitude (MEO satellite) | 0–6 000 m/s projected |
| PRR noise (dedicated GNSS chipset) | 0.01–0.05 m/s (1-sigma) |
| PRR noise (modem-integrated chipset) | 0.1–2 m/s |
| PRR clamping (some chipsets) | Hard-clamped at ±500 m/s — rows at exactly ±500 must be excluded |

### What it is used for

- **Velocity estimation** — 4 PRR measurements give 4 unknowns (Vx, Vy, Vz, clock drift)
  completely independently of position
- **Dead reckoning** — PRR-derived velocity integrated over time provides position
  between GNSS outages
- **Quality checks** — PRR residuals reveal Doppler noise and clock stability;
  the normalised PRR RMS reveals whether the chipset's uncertainty model is calibrated

### In GnssLogger

Column: `PseudorangeRateMetersPerSecond` and `PseudorangeRateUncertaintyMetersPerSecond`.

### In RINEX

Observable codes: `D1C` (L1 Doppler, Hz), `D2I` (BeiDou B1I Doppler), etc.
Note that RINEX stores Doppler in **Hz**, while GnssLogger stores it in **m/s**.
Convert: `PRR [m/s] = −Doppler_Hz × (c / f_carrier)`.

---

## ADR — Accumulated Delta Range

The **integrated carrier phase**, in metres.

While pseudorange measures distance by timing how long the code chip took to arrive,
ADR measures distance by counting how many carrier wave cycles have accumulated since
the receiver first locked on to the satellite. Because the carrier wavelength is ~19 cm
(compared to the C/A code chip of ~293 m), ADR is roughly **1 000× more precise than
pseudorange**.

```
ADR(t) = ADR(t₀) + Σ Δrange   (continuously integrated, metres)
       = N × λ + fractional_phase × λ   (where N is the unknown integer ambiguity)
```

### The integer ambiguity problem

When the receiver first locks on, it knows the fractional part of the phase (< 1 cycle)
but not how many complete cycles are in the total range. This unknown integer **N** must
be estimated and resolved before ADR becomes useful. Techniques:

| Technique | Ambiguity handling | Achievable accuracy |
|-----------|--------------------|-------------------|
| Float ambiguity PPP | Estimates N as real-valued | 2–10 cm after convergence |
| Fixed ambiguity RTK | Resolves N to integer (with a reference station) | 1–3 cm |
| Differenced ADR (relative) | Integer cancels between receivers at same epoch | mm-level baseline |

### Cycle slips

If the receiver momentarily loses phase lock (obstruction, interference), the cycle
count resets. This is a **cycle slip** — the continuity of the ADR time series is
broken and the ambiguity must be re-estimated. GnssLogger flags this with
`ADR_STATE_CYCLE_SLIP` (bit 2 of `AccumulatedDeltaRangeState`).

### ADR validity states on Android

| State value | Meaning | Usable? |
|-------------|---------|---------|
| 0 | `ADR_STATE_UNKNOWN` — no tracking | No |
| 1 | `ADR_STATE_VALID` (bit 0) — continuous phase tracking | **Yes** |
| 2 | `ADR_STATE_RESET` (bit 1) — cycle count reset | No |
| 4 | `ADR_STATE_CYCLE_SLIP` (bit 2) — slip detected | No |
| 16 | `ADR_STATE_HALF_CYCLE_REPORTED` (bit 4), bit 0 NOT set | No |
| 17 | bits 0+4 — valid + half-cycle resolved | **Yes** |

**State = 16** is the most common failure mode on current Android chipsets (Sony,
Qualcomm MPSS.DE family). The chip tracks carrier phase internally but the HAL driver
does not set `ADR_STATE_VALID`. This means ADR data is present in the file but is
not certifiably valid — the framework scores this as 0% valid ADR.

### Typical values

| Quantity | Value |
|----------|-------|
| ADR noise (when valid) | 0.001–0.01 m (< 0.1 cycle) |
| GPS L1 wavelength | 0.1903 m (= c / 1575.42 MHz) |
| Galileo E1 wavelength | 0.1903 m (same frequency as GPS L1) |
| GLONASS G1 wavelength | 0.1872–0.1876 m (varies per FDMA channel) |
| BeiDou B1C wavelength | 0.1903 m (1575.42 MHz, same as GPS L1) |
| BeiDou B1I wavelength | 0.1921 m (1561.098 MHz) |

### What it is used for

- **RTK (Real-Time Kinematic)** — cm-level relative positioning using a base station
- **PPP (Precise Point Positioning)** — cm-level absolute positioning after ambiguity convergence
- **Carrier-smoothed pseudorange** — PRR or ADR used to reduce PR noise (Hatch filter)
- **Cycle slip detection** — comparing ADR with PR or PRR reveals discontinuities

### In GnssLogger

Columns: `AccumulatedDeltaRangeMeters`, `AccumulatedDeltaRangeUncertaintyMeters`,
`AccumulatedDeltaRangeState`.

### In RINEX

Observable codes: `L1C` (GPS/GAL/QZSS L1 carrier phase, in **cycles**),
`L2I` (BeiDou B1I), `L1P` (BeiDou B1C), etc.
Convert from metres: `ADR_cycles = ADR_metres / wavelength`.

---

## Side-by-Side Comparison

| | PR | PRR | ADR |
|--|----|----|-----|
| **Measures** | Distance | Distance rate of change | Integrated phase |
| **Derived from** | Code chip travel time | Doppler frequency shift | Carrier cycle count |
| **Units** | metres | m/s | metres (or cycles) |
| **Noise (good chipset)** | ~1–3 m | ~0.01–0.05 m/s | ~0.001–0.01 m |
| **Ionosphere sensitivity** | High (~5 m L1) | Minimal (2nd order) | High (but cancels differentially) |
| **Integer ambiguity** | None | None | Yes — must be resolved |
| **Breaks at** | Nothing continuous | Nothing continuous | Cycle slips |
| **Used for** | Position | Velocity / dead-reckoning | High-precision positioning |
| **Android availability** | Always | Always | Rarely valid (HAL limitation) |
| **GnssLogger column** | computed from TimeNanos / ReceivedSvTimeNanos | PseudorangeRateMetersPerSecond | AccumulatedDeltaRangeMeters |
| **RINEX code** | `C__` | `D__` | `L__` |

---

## How the Quality Framework Tests Each Observable

### PR checks (Section 4 — Residuals)

After estimating the receiver position and clock, the **PR residual** for each satellite
is `PR_measured − PR_predicted`. A well-functioning receiver should have:

- **Small residual std** (≤ 5 m for L1 after iono correction, ≤ 3 m for L5)
- **Low outlier rate** (≤ 5% of residuals beyond 3-sigma)
- **Normalised RMS ≈ 1.0** — means the reported pseudorange uncertainty is well-calibrated

Single-frequency receivers typically show L1 PR residual std of 50–150 m because the
ionospheric delay is not removed. Dual-frequency (L1+L5 or B1C+B1I) can reduce this
to < 5 m.

### PRR checks (Section 4 — Residuals)

After estimating velocity and clock drift, the **PRR residual** is
`PRR_measured − PRR_predicted`. A well-functioning receiver should have:

- **Small residual std** (≤ 0.5 m/s)
- **Low fraction of high-residual epochs** (≤ 20%)
- **Normalised RMS ≈ 1.0** — the PRR uncertainty field is accurately calibrated

PRR quality is relatively insensitive to ionosphere and is mainly a measure of Doppler
noise, which directly tracks CN0. Higher CN0 → lower PRR noise.

### ADR checks (Section 3 — ADR / PRR / PR)

- **% Valid ADR** — must be ≥ 50% for the check to pass. Most Android devices score 0%.
- **% Usable ADR** — valid and not reset or cycle-slipped; ≥ 80% threshold.
- **ADR variability** — MAD of within-epoch ADR residuals ≤ 0.5 cycles.
- **PRR vs ΔADR consistency** — `PRR − d(ADR)/dt` should be near zero (≤ 0.1 m/s median).
  This cross-check detects cycle slips and half-cycle ambiguities independently.
- **ΔPR vs ΔADR** — epoch-to-epoch change in pseudorange vs carrier phase; should match
  to within 0.5 m if both are tracking correctly.
