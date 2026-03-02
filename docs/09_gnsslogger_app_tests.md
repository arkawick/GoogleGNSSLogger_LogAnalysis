# GnssLogger App Tests — No Extra Tools Required

All tests in this document can be performed using **only the GnssLogger app** on
an Android phone or Wear OS watch. No Python, no RTKLIB, no post-processing software.
Some tests observe the live in-app display; others inspect the three output files
(`.txt`, `.nmea`, `.26o`) with nothing more than a text editor or spreadsheet.

---

## The GnssLogger Interface

The app has four main views used during testing:

| View | What it shows |
|------|--------------|
| **Logger** | Start/Stop logging; logging status |
| **Status** | Live satellite list: CN0 bar per satellite, azimuth, elevation, used-in-fix flag |
| **Map** | Live fix position plotted on a map |
| **GNSS** | Scrolling live display of Raw measurement rows |

All tests below reference one or more of these views.

---

## Test 1 — Open-Sky Baseline (Signal Environment)

**Purpose:** Establish a reference CN0 and satellite count for the device in the best
possible conditions. All other tests compare against this baseline.

**Procedure:**
1. Go outdoors to a location with an unobstructed 360° sky view (no buildings, no trees).
2. Hold the phone flat (screen facing up) at chest height.
3. Start logging. Wait 30 seconds for full acquisition.
4. Observe the **Status** view for 60 seconds.

**What to read from the Status view:**

| Observation | Good | Poor |
|------------|------|------|
| Number of satellites with CN0 bars | ≥ 25 | < 15 |
| Highest CN0 bar (any satellite) | > 40 dBHz | < 30 dBHz |
| Number of constellations visible | 5 (GPS, GLO, GAL, BDS, QZSS) | ≤ 3 |
| Satellites with `Used in Fix` = Yes | ≥ 12 | < 8 |

**What to read from the .nmea file (text editor):**

Open the `.nmea` file and find any `$GNGGA` line:
```
NMEA,$GNGGA,083012.00,...,1,14,0.4,958.7,...
                                ^   ^^^
                                |   HDOP = 0.4 (outstanding)
                                Satellites used = 14
```
HDOP < 1.0 and ≥ 12 satellites used confirms an excellent open-sky baseline.

---

## Test 2 — Time to First Fix (TTFF)

**Purpose:** Measure how quickly the device acquires a position fix from different
starting states.

### Test 2a — Hot Start TTFF

**Procedure:**
1. Use the device normally (GNSS has been active in the last hour).
2. Open GnssLogger, go to the **Map** view.
3. Start logging. Note the wall-clock time.
4. Watch the map for the first fix marker to appear.
5. Record the elapsed time.

**Expected:** 1–5 seconds with network assistance (SUPL) active.

### Test 2b — Warm Start TTFF

**Procedure:**
1. Disable mobile data and Wi-Fi (prevent SUPL assistance).
2. Open GnssLogger, start logging, watch the **Status** view.
3. Time from first log row to first `Fix` row in the `.txt` file.

**Expected:** 10–45 seconds. Almanac is cached but ephemeris may be stale.

### Test 2c — Cold Start TTFF

**Procedure:**
1. Reboot the device (clears GNSS cache) or enable flight mode for > 4 hours then
   move to a different city-scale location (> 100 km from last known position).
2. Disable mobile data and Wi-Fi.
3. Go outdoors. Open GnssLogger, start logging immediately.
4. Time from app start to first `Fix` row in `.txt`.

**Expected:** 30–90 seconds. The receiver must decode full ephemeris from the satellite
signal (30 s per GPS subframe).

**How to check TTFF from the .txt file (text editor):**
```
Look for the first "Fix," line and note its utcTimeMillis.
Look for the first "Raw," line and note its utcTimeMillis.
TTFF = Fix_utcTimeMillis - first_Raw_utcTimeMillis   (divide by 1000 for seconds)
```

---

## Test 3 — Multi-Constellation Verification

**Purpose:** Confirm the device tracks all expected constellations.

**Procedure:**
1. Open-sky location. Start logging for 60 seconds.
2. In the **Status** view, note which constellation-coloured bars appear.
   (GnssLogger colour-codes bars by constellation type.)

**What to check in the .txt file (text editor):**

Scan the `Raw,` lines and look at the `ConstellationType` column (column 17 in the
header):
```
grep "^Raw," gnss_log.txt | cut -d',' -f17 | sort | uniq -c
```
Or open in a spreadsheet and filter column 17:

| ConstellationType value | Expected constellation |
|------------------------|----------------------|
| 1 | GPS |
| 3 | GLONASS |
| 5 | BeiDou |
| 6 | Galileo |
| 4 | QZSS (Asia-Pacific only) |
| 7 | NavIC (Indian subcontinent only) |

**Pass condition:** Values 1, 3, 5, 6 all present for a mid-latitude location.
Value 4 (QZSS) present confirms Asia-Pacific regional coverage.

**What to check in the .nmea file:**

Scan for talker-ID prefixes — each constellation has its own GSV sentence:
```
$GPGSV  → GPS
$GLGSV  → GLONASS
$GAGSV  → Galileo
$GBGSV  → BeiDou
$GQGSV  → QZSS
$GIGSV  → NavIC
```
If a `$GBGSV` line is present, BeiDou is visible. The count of satellites per
sentence (3rd field) tells you how many of each constellation are in view.

---

## Test 4 — L5 / Dual-Frequency Availability Check

**Purpose:** Check whether the device exposes GPS L5 (1176.45 MHz) measurements.

**Procedure:**
1. Open-sky baseline session, 60+ seconds.
2. Open the `.txt` file in a text editor.
3. Search for the carrier frequency value `1176450000` in the `CarrierFrequencyHz`
   column.

```
Search in text editor:  1176450000
```

If found → GPS L5 (or Galileo E5a) is being tracked.
If absent → device does not expose L5. Structural limitation.

**What to also check:**

BeiDou dual-frequency: search for both `1575420000` (B1C) and `1561098000` (B1I) in
the same session. If both appear in `Raw,` rows with `ConstellationType=5`, the device
tracks BeiDou dual-frequency.

---

## Test 5 — Carrier Phase (ADR) Availability Check

**Purpose:** Determine whether the device exposes valid carrier phase.

**Procedure:**
1. Open-sky session, 60+ seconds.
2. Open the `.txt` file. Find the column `AccumulatedDeltaRangeState` (from the header).
3. Scan the values in that column across all `Raw,` rows.

**Interpret the values:**

| Value seen | Meaning |
|-----------|---------|
| 0 | No carrier phase at all |
| 1 | **ADR valid** — carrier phase is usable |
| 16 | Half-cycle reported, NOT valid — chip computes phase internally but HAL does not certify |
| 17 | Valid + half-cycle resolved — best case |

**Quick check:** If ALL values are 0 or 16, the device has 0% valid ADR.
This is a structural limitation — firmware/HAL update required.

---

## Test 6 — BiasUncertaintyNanos Chipset Check

**Purpose:** Identify the oscillator quality class of the device and confirm the
correct BiasUncNanos analysis threshold.

**Procedure:**
1. Any outdoor session, 30+ seconds.
2. Open the `.txt` file. Find the `BiasUncertaintyNanos` column.
3. Read any 5–10 values from `Raw,` rows.

**Interpret the values:**

| Typical range | Chipset class | Threshold to use |
|--------------|---------------|-----------------|
| 2–10 ns | Dedicated GNSS modem (e.g. Snapdragon MPSS.DE) | 40 ns (standard) |
| 10–40 ns | Tensor G-series, some MediaTek | 40 ns (standard) |
| 75–200 ns | Modem-integrated (e.g. Snapdragon MPSS.HI) | **200 ns** (relax) |

If the values are 75–200 ns and you use the default 40 ns threshold, **all measurements
will be filtered out** and every analysis check will fail erroneously. This single
check prevents that misdiagnosis.

**Also check the device header:**
The first comment line of the `.txt` file contains:
```
# GNSS Hardware Model Name: qcom;MPSS.HI.4.3.1;...
                                  ^^^^^^^^
                                  MPSS.HI → use 200 ns threshold
```

---

## Test 7 — Stationary Fix Scatter Test

**Purpose:** Measure the noise of the position fix when the receiver is completely
stationary. Reveals the combined effect of geometry, CN0, and chipset filtering.

**Procedure:**
1. Place the phone on a flat stable surface outdoors (no hand tremor).
2. Log for 120–300 seconds without touching the device.
3. Open the `.nmea` file and extract all `$GNGGA` lines.

**What to read from the .nmea file:**

Each `$GNGGA` line gives a position fix. Extract the latitude and longitude fields
and observe the range of values:

```
$GNGGA,083012.00,1304.08720,N,07735.50990,E,...
$GNGGA,083013.00,1304.08718,N,07735.50993,E,...
$GNGGA,083014.00,1304.08721,N,07735.50988,E,...
```

The 5th decimal place of the DDMM.MMMMM format corresponds to:
- Latitude: ~0.00001' ≈ 0.018 m  (each unit = 1.8 cm)
- Longitude at 13°N: ~0.00001' ≈ 0.017 m

**Scatter interpretation:**

| Last-digit variation in DDMM.MMMMM | Position scatter | Quality |
|------------------------------------|-----------------|---------|
| ±1–3 digits | ~2–5 cm | Excellent |
| ±5–15 digits | ~10–30 cm | Very good |
| ±30–80 digits | ~0.5–1.5 m | Good |
| ±200+ digits | > 3 m | Moderate / poor sky |

The `AccuracyMeters` field (9th field after the fix quality) gives the chipset's
self-reported 1-sigma horizontal accuracy. Compare the reported accuracy to the
actual scatter you measure above to assess how well-calibrated the uncertainty model is.

---

## Test 8 — Phone Orientation vs Signal Quality

**Purpose:** Observe how antenna orientation affects satellite visibility and CN0.

**Procedure:**
1. Outdoors, open sky. Start logging.
2. Hold the phone in each orientation for 30 seconds, watching the **Status** view:
   - Flat / screen up (ideal for roof-mounted antenna)
   - Portrait vertical (normal use)
   - Portrait vertical facing North
   - Portrait vertical facing South
   - Landscape horizontal

**What to observe:**
- Total CN0 bar height across all satellites
- Which constellation satellites disappear or strengthen
- Whether HDOP changes (visible in `$GNGSA` lines)

**Expected pattern:** Flat/screen-up gives the most uniform sky coverage. Portrait
mode creates an asymmetric gain pattern — satellites in the direction the screen faces
receive stronger signals; those behind the phone body are attenuated.

This test is particularly informative for Wear OS watches — the wrist orientation
constantly changes, so watching CN0 variation during normal wrist movement reveals
the antenna pattern.

---

## Test 9 — Environment Comparison Test

**Purpose:** Quantitatively compare signal quality across environments using only
the `.nmea` file's HDOP and satellite count.

**Procedure:** Log for 60 seconds in each of the following locations without
changing device settings:

| Location | Log name |
|----------|---------|
| Open sky (rooftop or open field) | LogA |
| Under a tree | LogB |
| Urban street (buildings on both sides) | LogC |
| Near a window indoors | LogD |

**Quick comparison using .nmea file (text editor):**

From each log, read the first `$GNGGA` sentence's fields:
- Field 7: satellites used
- Field 8: HDOP
- Field 9: altitude (should be consistent across locations)

From each log, read any `$GNGSA` sentence's fields:
- Field 15: PDOP
- Field 16: HDOP
- Field 17: VDOP

| Environment | Expected HDOP | Expected sats used | Expected CN0 (Status view) |
|------------|:------------:|:-----------------:|:------------------------:|
| Open sky | 0.3–0.8 | 14–24 | 35–50 dBHz |
| Under tree | 0.5–1.5 | 10–18 | 25–40 dBHz |
| Urban street | 1.0–4.0 | 6–14 | 15–35 dBHz |
| Near window | 2.0–8.0 | 4–10 | 10–30 dBHz |

---

## Test 10 — AGC / Interference Spot Check

**Purpose:** Check whether the RF environment is clean at the recording location.

**Procedure:**
1. Open the `.txt` file in a text editor or spreadsheet.
2. Find the `AgcDb` column in the `Raw,` rows (check the `# Raw,` header for index).
3. Scan 20–30 values from different times in the session.

**Interpret the values:**

| AgcDb range | RF environment |
|------------|---------------|
| −0.5 to +0.5 dB | Clean — no significant interference |
| −2 to −5 dB | Mild interference (nearby Wi-Fi, crowded spectrum) |
| < −10 dB | Strong interference — AGC heavily attenuating |
| 0 for all rows | Chipset does not report AGC (not a failure) |

**Interference signature to watch for:** If `AgcDb` drops sharply (large negative) for
all constellations simultaneously at the same epoch, that is a wideband interference
event. If only one frequency band is affected, it is narrowband interference.

---

## Test 11 — Fix Provider Comparison

**Purpose:** Compare GPS-only vs Fused (FLP) accuracy numbers the device reports.

**Procedure:**
1. Stationary outdoors session, 120 seconds.
2. Open the `.txt` file. Find the `Fix,` rows.
3. Filter by `Provider` column: compare `gps` rows vs `fused` rows.

**What to compare:**

| Field | GPS rows | FLP rows | Interpretation |
|-------|---------|---------|----------------|
| `AccuracyMeters` | Typically 3–15 m | Same or slightly better | Fused can tighten with IMU |
| `LatitudeDegrees` scatter | See spread over time | Same or tighter | Less scatter = better IMU fusion |
| `SpeedMps` | ~0.0 when stationary | ~0.0 | Both should be near zero |
| `VerticalAccuracyMeters` | Typically 4–20 m | Similar | Barometer can improve if available |

**If FLP accuracy is identical to GPS:** Minimal IMU fusion happening (device may not have
barometer or IMU tight-coupling).

**If FLP scatter is much tighter:** Dead-reckoning / sensor fusion is actively improving
the position.

---

## Test 12 — Satellite Geometry Check (Sky Plot from Status View)

**Purpose:** Visually confirm that satellites are distributed across the sky, not
clustered in one direction.

**Procedure:**
1. Open-sky outdoors. Open the **Status** view.
2. Note the azimuth values of the highest-CN0 satellites.
3. Mentally plot: are they spread around the compass (N/S/E/W/zenith)?
   Or are they all in one quadrant?

**What it means:**

| Sky distribution | HDOP impact |
|-----------------|------------|
| Evenly spread (all quadrants + zenith) | HDOP < 1.0 — best geometry |
| Missing one quadrant (e.g. building to North) | HDOP 1.0–2.0 |
| Satellites only in half the sky | HDOP 2.0–5.0 |
| Satellites in one arc | HDOP > 5.0 — poor horizontal fix |

Good geometry requires satellites at low elevation in multiple directions (to anchor
horizontal position) AND at high elevation (to anchor vertical). All satellites near
the horizon → good horizontal but poor vertical. All near zenith → poor horizontal.

---

## Test 13 — Device Header Information Check

**Purpose:** Identify device chipset, Android version, and GnssLogger version from
the log file header — no app settings needed.

**Procedure:**
1. Open the `.txt` file in any text editor.
2. Read the first 10–15 comment lines (starting with `#`).

**What to look for:**

```
# GnssLogger Version: 3.1.1.2       ← app version
# manufacturer: Google               ← device manufacturer
# model: Pixel 9                     ← device model
# AndroidVersionRelease: 16          ← Android version
# Platform: Tensor G4                ← SoC
# GNSS Hardware Model Name: qcom;MPSS.DE.9.1;... ← GNSS modem
```

**Key check — GNSS Hardware Model Name:**
- Contains `MPSS.HI` → modem-integrated GNSS → BiasUncNanos will be 75–200 ns → relax threshold
- Contains `MPSS.DE` → dedicated GNSS modem → BiasUncNanos will be 2–10 ns → standard threshold
- Contains `Exynos` or `Tensor` → Samsung/Google SoC → typically 5–40 ns

This check takes 10 seconds and prevents the most common analysis mistake
(filtering out all measurements with the wrong threshold).

---

## Test 14 — Altitude Sanity Check

**Purpose:** Verify the reported altitude is physically plausible.

**Procedure:**
1. Open the `.nmea` file. Find any `$GNGGA` line.
2. Read field 9 (MSL altitude in metres) and field 11 (geoid separation).
3. Compute the ellipsoidal height: `h = MSL altitude + geoid separation`.
4. Compare against a known reference (Google Earth shows both MSL and ellipsoidal).

```
$GNGGA,...,958.7,M,-85.8,M,...
           ^^^^^   ^^^^^
           MSL     Geoid sep
           958.7 + (-85.8) = 872.9 m ellipsoidal
```

**Pass condition:** Computed ellipsoidal height matches Google Earth elevation
within ±20 m for a single-frequency stationary receiver.

**If altitude is off by ~85–90 m:** The geoid separation is being added instead of
the MSL altitude being reported (common confusion between WGS-84 and MSL).

---

## Quick-Reference: What to Check and Where

| Question | File | What to look at |
|----------|------|----------------|
| How many satellites are tracked? | `.nmea` | `$GBGSV/GPGSV/GAGSV/GLGSV` 3rd field |
| How many are used in fix? | `.nmea` | `$GNGGA` field 7 |
| What is HDOP? | `.nmea` | `$GNGGA` field 8 / `$GNGSA` field 16 |
| What is my altitude? | `.nmea` | `$GNGGA` fields 9 + 11 |
| Is the device stationary? | `.nmea` | `$GNVTG` speed fields (should be 0.0) |
| Which constellations are present? | `.txt` | `ConstellationType` column in `Raw,` rows |
| Is L5 present? | `.txt` | Search for `1176450000` in `CarrierFrequencyHz` |
| Is BeiDou dual-frequency? | `.txt` | Both `1575420000` and `1561098000` with `ConstellationType=5` |
| Is carrier phase valid? | `.txt` | `AccumulatedDeltaRangeState` column (look for value = 1) |
| What is the chipset? | `.txt` | `# GNSS Hardware Model Name:` in header |
| Is the RF environment clean? | `.txt` | `AgcDb` column in `Raw,` rows |
| What is fix accuracy? | `.txt` | `AccuracyMeters` column in `Fix,` rows |
| Hot start TTFF? | `.txt` | First `Fix,` row minus first `Raw,` row (utcTimeMillis) |
