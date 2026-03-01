"""
GNSS Analysis using gnss-lib-py
Analyses: gnss_log_2026_02_25_23_25_37.{txt, nmea, 26o}
Device: Xiaomi 2201116PI, Android 13, GnssLogger v3.1.1.2
"""

import os, warnings
warnings.filterwarnings("ignore")

import gnss_lib_py as glp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pynmea2

LOG_DIR    = os.path.dirname(os.path.abspath(__file__))
TXT_FILE   = os.path.join(LOG_DIR, "gnss_log_2026_02_25_23_25_37.txt")
NMEA_FILE  = os.path.join(LOG_DIR, "gnss_log_2026_02_25_23_25_37.nmea")
RINEX_FILE = os.path.join(LOG_DIR, "gnss_log_2026_02_25_23_25_37.26o")

CONST_COLOUR = {
    "gps":     "#1f77b4",
    "glonass": "#ff7f0e",
    "galileo": "#2ca02c",
    "beidou":  "#d62728",
    "qzss":    "#9467bd",
    "sbas":    "#8c564b",
    "navic":   "#e377c2",
    "unknown": "#7f7f7f",
}
CONST_NAMES_INT = {
    1:"GPS", 2:"SBAS", 3:"GLONASS", 4:"QZSS",
    5:"BeiDou", 6:"Galileo", 7:"NavIC"
}

print("=" * 60)
print(f"  GNSS Log Analysis  -  gnss-lib-py v{glp.__version__}")
print("=" * 60)

# ══════════════════════════════════════════════════════════════════════════════
# 1. RAW GNSS MEASUREMENTS  (relaxed filters for Xiaomi)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1] Loading raw GNSS measurements …")

# Default bias_uncertainty threshold (40 ns) rejects all rows on this device
# (BiasUncertaintyNanos = 75–129 ns). Relax to 200 ns; keep other filters.
relaxed_filters = {
    "bias_valid":            True,
    "bias_uncertainty":      200.0,   # relaxed from 40 -> 200 ns
    "arrival_time":          True,
    "unknown_constellations": True,
    "time_valid":            True,
    "state_decoded":         True,
    "sv_time_uncertainty":   500.0,
}
raw = glp.AndroidRawGnss(TXT_FILE, measurement_filters=relaxed_filters, verbose=False)
print(f"    Measurements after filtering : {raw.shape[1]}")
print(f"    Constellations               : {np.unique(raw['gnss_id']).tolist()}")

t_ms  = raw["gps_millis"]
t_sec = (t_ms - t_ms[0]) / 1000.0   # elapsed seconds

# ── 1a. Constellation count ───────────────────────────────────────────────────
print("\n--- Constellation measurement count ---")
for c, n in zip(*np.unique(raw["gnss_id"], return_counts=True)):
    print(f"    {c:10s}: {n:4d}")

# ── 1b. CN0 over time by constellation ───────────────────────────────────────
print("\n[1b] CN0 by constellation …")
fig, ax = plt.subplots(figsize=(12, 5))
for c in np.unique(raw["gnss_id"]):
    mask = raw["gnss_id"] == c
    ax.scatter(t_sec[mask], raw["cn0_dbhz"][mask],
               s=6, alpha=0.7, color=CONST_COLOUR.get(c, "#333"),
               label=c.upper())
ax.set_xlabel("Elapsed time (s)")
ax.set_ylabel("CN0 (dB-Hz)")
ax.set_title("Carrier-to-Noise Density (CN0) by Constellation")
ax.axhline(25, color="red", linewidth=0.8, linestyle="--", label="25 dB-Hz threshold")
ax.legend(markerscale=3, ncol=3)
ax.grid(True, alpha=0.3)
out = os.path.join(LOG_DIR, "cn0_by_constellation.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ── CN0 statistics ────────────────────────────────────────────────────────────
cn0 = raw["cn0_dbhz"]
print(f"\n--- CN0 statistics (all constellations) ---")
print(f"    Mean   : {np.mean(cn0):.1f} dB-Hz")
print(f"    Median : {np.median(cn0):.1f} dB-Hz")
print(f"    Min    : {np.min(cn0):.1f} dB-Hz")
print(f"    Max    : {np.max(cn0):.1f} dB-Hz")

# ── 1c. Pseudorange rate ──────────────────────────────────────────────────────
print("\n[1c] Pseudorange rate (Doppler) …")
prr = raw["PseudorangeRateMetersPerSecond"]
fig, ax = plt.subplots(figsize=(12, 4))
for c in np.unique(raw["gnss_id"]):
    mask = raw["gnss_id"] == c
    ax.scatter(t_sec[mask], prr[mask], s=4, alpha=0.5,
               color=CONST_COLOUR.get(c, "#333"), label=c.upper())
ax.set_xlabel("Elapsed time (s)")
ax.set_ylabel("Pseudorange Rate (m/s)")
ax.set_title("Pseudorange Rate (Doppler) over Time")
ax.axhline(0, color="red", linewidth=0.8, linestyle="--")
ax.legend(markerscale=3, ncol=3)
ax.grid(True, alpha=0.3)
out = os.path.join(LOG_DIR, "pseudorange_rate.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ── 1d. Raw pseudorange ───────────────────────────────────────────────────────
if "raw_pr_m" in raw.rows:
    print("\n[1d] Raw pseudorange …")
    pr = raw["raw_pr_m"]
    fig, ax = plt.subplots(figsize=(12, 4))
    for c in np.unique(raw["gnss_id"]):
        mask = raw["gnss_id"] == c
        ax.scatter(t_sec[mask], pr[mask] / 1e6, s=4, alpha=0.5,
                   color=CONST_COLOUR.get(c, "#333"), label=c.upper())
    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("Raw Pseudorange (x106 m)")
    ax.set_title("Raw Pseudorange over Time")
    ax.legend(markerscale=3, ncol=3)
    ax.grid(True, alpha=0.3)
    out = os.path.join(LOG_DIR, "raw_pseudorange.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"    Saved -> {out}")
    plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# 2. FIX MEASUREMENTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Fix measurements …")
fixes = glp.AndroidRawFixes(TXT_FILE)
print(f"    Fix rows: {list(fixes.rows)}")
# gnss-lib-py uses fix_provider, lat_rx_deg, lon_rx_deg, AccuracyMeters
prov_key = "fix_provider" if "fix_provider" in fixes.rows else "provider"
lat_key  = "lat_rx_deg"   if "lat_rx_deg"   in fixes.rows else "lat_deg"
lon_key  = "lon_rx_deg"   if "lon_rx_deg"   in fixes.rows else "lng_deg"
acc_key  = "AccuracyMeters" if "AccuracyMeters" in fixes.rows else "accuracy_m"

providers = np.unique(fixes[prov_key]) if prov_key in fixes.rows else []
print(f"    Providers: {list(providers)}")

if lat_key in fixes.rows and lon_key in fixes.rows:
    fig, ax = plt.subplots(figsize=(8, 6))
    prov_col = {"gps":"#1f77b4","fused":"#ff7f0e","network":"#2ca02c","gnss":"#1f77b4"}
    for p in providers:
        mask = fixes[prov_key] == p
        ax.scatter(fixes[lon_key][mask], fixes[lat_key][mask],
                   s=12, alpha=0.8, label=p.upper(),
                   color=prov_col.get(p.lower(), "#333"))
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title("Fix Positions by Provider")
    ax.legend(); ax.grid(True, alpha=0.3)
    out = os.path.join(LOG_DIR, "fix_positions.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"    Saved -> {out}")
    plt.close(fig)

    if acc_key in fixes.rows:
        fig, ax = plt.subplots(figsize=(8, 4))
        for p in providers:
            mask = fixes[prov_key] == p
            ax.hist(fixes[acc_key][mask], bins=25, alpha=0.6,
                    label=p.upper(), color=prov_col.get(p.lower(), "#333"))
        ax.set_xlabel("Horizontal accuracy (m)")
        ax.set_ylabel("Count")
        ax.set_title("Reported Accuracy Distribution by Provider")
        ax.legend(); ax.grid(True, alpha=0.3)
        out = os.path.join(LOG_DIR, "accuracy_histogram.png")
        fig.savefig(out, dpi=150, bbox_inches="tight")
        print(f"    Saved -> {out}")
        plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# 3. STATUS ROWS  -> sky plot + CN0 box plot + tracked vs used
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Parsing Status rows …")
status_rows = []
with open(TXT_FILE) as f:
    for line in f:
        if line.startswith("Status,"):
            p = line.strip().split(",")
            try:
                status_rows.append({
                    "t_ms":  float(p[1]),
                    "const": int(p[4]),
                    "svid":  int(p[5]),
                    "cn0":   float(p[7]),
                    "az":    float(p[8]),
                    "el":    float(p[9]),
                    "used":  p[10].strip() == "1",
                })
            except (ValueError, IndexError):
                pass

df = pd.DataFrame(status_rows)
df["const_name"] = df["const"].map(CONST_NAMES_INT).fillna("Unknown")
print(f"    Status rows : {len(df)}")
print(f"    Constellations: {sorted(df['const_name'].unique())}")

# ── 3a. Sky plot ──────────────────────────────────────────────────────────────
print("\n[3a] Sky plot …")
fig = plt.figure(figsize=(7, 7))
ax  = fig.add_subplot(111, projection="polar")
cc  = {"GPS":"#1f77b4","GLONASS":"#ff7f0e","Galileo":"#2ca02c",
       "BeiDou":"#d62728","QZSS":"#9467bd"}
for c, grp in df.groupby("const_name"):
    sc = ax.scatter(np.deg2rad(grp["az"]), 90 - grp["el"],
                    c=grp["cn0"], cmap="RdYlGn", vmin=15, vmax=45,
                    s=20, alpha=0.75, label=c)
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_ylim(0, 90)
ax.set_yticks([0, 30, 60, 90])
ax.set_yticklabels(["90°", "60°", "30°", "0°"])
ax.set_title("Sky Plot (colour = CN0 dB-Hz)", va="bottom", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.4, 1.1), markerscale=2)
fig.colorbar(sc, ax=ax, label="CN0 (dB-Hz)", shrink=0.6, pad=0.1)
out = os.path.join(LOG_DIR, "sky_plot.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ── 3b. CN0 box plot per constellation ───────────────────────────────────────
print("\n[3b] CN0 box plot per constellation …")
fig, ax = plt.subplots(figsize=(9, 5))
const_list = sorted(df["const_name"].unique())
data_list  = [df[df["const_name"] == c]["cn0"].values for c in const_list]
bp = ax.boxplot(data_list, labels=const_list, patch_artist=True, notch=False,
                medianprops=dict(color="black", linewidth=2))
for patch, c in zip(bp["boxes"], const_list):
    patch.set_facecolor(cc.get(c, "#aaaaaa"))
    patch.set_alpha(0.7)
ax.set_ylabel("CN0 (dB-Hz)")
ax.set_title("CN0 Distribution per Constellation")
ax.axhline(25, color="red", linewidth=0.8, linestyle="--", label="25 dB-Hz")
ax.legend(); ax.grid(True, axis="y", alpha=0.3)
out = os.path.join(LOG_DIR, "cn0_boxplot.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ── 3c. Tracked vs used in fix ────────────────────────────────────────────────
print("\n[3c] Satellites tracked vs used …")
tracked = df.groupby("const_name")["svid"].nunique()
used    = df[df["used"]].groupby("const_name")["svid"].nunique()
fig, ax = plt.subplots(figsize=(8, 4))
x = np.arange(len(tracked))
ax.bar(x - 0.2, tracked.values, 0.4, label="Tracked", color="#4c72b0")
ax.bar(x + 0.2, used.reindex(tracked.index, fill_value=0).values,
       0.4, label="Used in fix", color="#55a868")
ax.set_xticks(x); ax.set_xticklabels(tracked.index)
ax.set_ylabel("Unique SVIDs")
ax.set_title("Satellites Tracked vs Used in Fix")
ax.legend(); ax.grid(True, axis="y", alpha=0.3)
out = os.path.join(LOG_DIR, "sats_tracked_vs_used.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ── 3d. Elevation histogram ───────────────────────────────────────────────────
print("\n[3d] Elevation histogram …")
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(df["el"], bins=18, range=(0, 90), color="#4c72b0", edgecolor="white", alpha=0.8)
ax.set_xlabel("Elevation (°)")
ax.set_ylabel("Count")
ax.set_title("Satellite Elevation Distribution")
ax.grid(True, alpha=0.3)
out = os.path.join(LOG_DIR, "elevation_histogram.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"    Saved -> {out}")
plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# 4. NMEA  - GGA positions
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] NMEA summary (GGA fixes) …")
gga_rows = []
with open(NMEA_FILE) as f:
    for line in f:
        if not line.startswith("NMEA,"):
            continue
        parts = line.strip().split(",")
        sentence_type = parts[1] if len(parts) > 1 else ""
        if "GGA" not in sentence_type:
            continue
        try:
            raw_nmea = ",".join(parts[1:-1])   # strip leading NMEA, and trailing timestamp
            msg = pynmea2.parse(raw_nmea)
            if msg.latitude and msg.longitude:
                gga_rows.append({
                    "lat": msg.latitude,
                    "lon": msg.longitude,
                    "alt": float(msg.altitude) if msg.altitude else np.nan,
                    "hdop": float(msg.horizontal_dil) if msg.horizontal_dil else np.nan,
                    "fix_quality": int(msg.gps_qual),
                    "num_sats": int(msg.num_sats),
                })
        except Exception:
            pass

if gga_rows:
    gdf = pd.DataFrame(gga_rows)
    print(f"    GGA fixes   : {len(gdf)}")
    print(f"    Lat range   : {gdf['lat'].min():.6f}° – {gdf['lat'].max():.6f}°")
    print(f"    Lon range   : {gdf['lon'].min():.6f}° – {gdf['lon'].max():.6f}°")
    print(f"    Alt range   : {gdf['alt'].min():.1f} – {gdf['alt'].max():.1f} m")
    print(f"    Avg HDOP    : {gdf['hdop'].mean():.2f}")
    print(f"    Avg #sats   : {gdf['num_sats'].mean():.1f}")

    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(gdf["lon"], gdf["lat"], c=gdf["hdop"], cmap="RdYlGn_r",
                    s=20, alpha=0.8)
    fig.colorbar(sc, ax=ax, label="HDOP")
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    ax.set_title("NMEA GGA Fix Positions (colour = HDOP)")
    ax.grid(True, alpha=0.3)
    out = os.path.join(LOG_DIR, "nmea_positions.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"    Saved -> {out}")
    plt.close(fig)

    # Altitude over time
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(gdf["alt"].values, color="#4c72b0", linewidth=1.2)
    ax.set_xlabel("Fix index")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("NMEA Altitude over Time")
    ax.grid(True, alpha=0.3)
    out = os.path.join(LOG_DIR, "nmea_altitude.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"    Saved -> {out}")
    plt.close(fig)
else:
    print("    No GGA sentences found.")

# ══════════════════════════════════════════════════════════════════════════════
# 5. RINEX OBSERVATION SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5] RINEX 4.01 summary …")
epochs, systems = 0, set()
with open(RINEX_FILE) as f:
    in_header = True
    for line in f:
        if "END OF HEADER" in line:
            in_header = False; continue
        if not in_header:
            if line.startswith(">"):
                epochs += 1
            elif line.strip() and not line.startswith(">"):
                systems.add(line[0])
RINEX_SYS = {"G":"GPS","R":"GLONASS","E":"Galileo","C":"BeiDou","J":"QZSS",
              "S":"SBAS","I":"NavIC"}
print(f"    Epochs  : {epochs}")
print(f"    Systems : {[RINEX_SYS.get(s, s) for s in sorted(systems)]}")

# ══════════════════════════════════════════════════════════════════════════════
# 6. COMBINED SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  ANALYSIS COMPLETE")
print("=" * 60)
print(f"\n  Device : Xiaomi 2201116PI  |  Android 13")
print(f"  App    : GnssLogger v3.1.1.2")
print(f"  Log    : 2026-02-25 17:55 UTC")
print(f"\n  Raw measurements : {raw.shape[1]}")
print(f"  NMEA GGA fixes   : {len(gga_rows)}")
print(f"  RINEX epochs     : {epochs}")
print(f"\n  Output PNGs:")
for f in sorted(os.listdir(LOG_DIR)):
    if f.endswith(".png"):
        print(f"    +  {f}")
print()
