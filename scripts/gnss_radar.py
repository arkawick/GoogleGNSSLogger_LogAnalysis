#!/usr/bin/env python3
"""
gnss_radar.py
GNSS Quality Radar -- Google Android Bootcamp style
Inverted scale: centre = PASS / better, outer ring = FAIL / worse
N/A checks plotted at the mid-ring (0.48).
Output: gnss_radar.png
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# === CHANGE THESE FOR EACH LOG / DEVICE ===
LOG_DIR_NAME = "Log1"
DEVICE       = "Xiaomi 13  |  Qualcomm MPSS.HI.4.3.1"
SCORE        = "9 / 26 applicable  (35 %)"
# ─────────────────────────────────────────────────────────────────────────────
_ROOT      = Path(__file__).resolve().parent.parent   # project root
LOG_DIR    = _ROOT / LOG_DIR_NAME
OUTPUT_DIR = LOG_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Check results
# (section_key, short_label, status)   status: "PASS" | "FAIL" | "NA"
# Arranged clockwise from the top: BASIC → TIME → ADR/PRR/PR → Residuals
# ─────────────────────────────────────────────────────────────────────────────
CHECKS = [
    # ── BASIC CHECKS (14) ────────────────────────────────────────────────────
    ("BASIC", "Avg CN0\nTop 4/Epoch",       "FAIL"),
    ("BASIC", "Max Time\nBetween Epochs",    "PASS"),
    ("BASIC", "Avg Valid/Epoch\nGPS L1",     "FAIL"),
    ("BASIC", "Avg Valid/Epoch\nGPS L5",     "NA"),
    ("BASIC", "Avg Valid/Epoch\nGLO G1",     "FAIL"),
    ("BASIC", "Avg Valid/Epoch\nGAL E1",     "FAIL"),
    ("BASIC", "Avg Valid/Epoch\nGAL E5A",    "NA"),
    ("BASIC", "Avg Valid/Epoch\nGAL E5B",    "NA"),
    ("BASIC", "Avg Valid/Epoch\nBDS B1I",    "FAIL"),
    ("BASIC", "Avg Valid/Epoch\nBDS B2A",    "NA"),
    ("BASIC", "Avg Valid/Epoch\nBDS B1C",    "NA"),
    ("BASIC", "Required\nSig Types",         "FAIL"),
    ("BASIC", "Measurement\nState Usable",   "PASS"),
    ("BASIC", "Duplicate\nSignals",          "PASS"),
    # ── TIME (8) ─────────────────────────────────────────────────────────────
    ("TIME",  "Time Tag\nLarge Jumps",       "PASS"),
    ("TIME",  "Time Tag\nJitter",            "PASS"),
    ("TIME",  "Time-sync\nMax Jitter",       "PASS"),
    ("TIME",  "Time-sync\nJitter",           "PASS"),
    ("TIME",  "dERTN\nRange",               "FAIL"),
    ("TIME",  "dERTN\nStd",                 "FAIL"),
    ("TIME",  "dClock Bias\nStd",           "FAIL"),
    ("TIME",  "LS-Freq PR\nResiduals Std",  "FAIL"),
    # ── ADR / PRR / PR (7) ───────────────────────────────────────────────────
    ("ADR",   "% Valid ADR",                "FAIL"),
    ("ADR",   "% Usable ADR",               "FAIL"),
    ("ADR",   "ADR\nVariability",           "NA"),
    ("ADR",   "Median\nPRR - dADR",         "NA"),
    ("ADR",   "Std\nPRR - dADR",            "NA"),
    ("ADR",   "L1freq\ndPR - dADR",         "NA"),
    ("ADR",   "L5freq\ndPR - dADR",         "NA"),
    # ── RESIDUALS (12) ───────────────────────────────────────────────────────
    ("RES",   "L1 PR\nResiduals Std",       "FAIL"),
    ("RES",   "L5 PR\nResiduals Std",       "NA"),
    ("RES",   "L1 Med Norm\nPR Resid RMS",  "FAIL"),
    ("RES",   "L5 Med Norm\nPR Resid RMS",  "NA"),
    ("RES",   "% PR Resid\nOutliers",       "FAIL"),
    ("RES",   "Epochs w/\nADR Resid",       "FAIL"),
    ("RES",   "ADR\nResiduals Std",         "NA"),
    ("RES",   "Med Norm ADR\nResid RMS",    "NA"),
    ("RES",   "% High ADR\nResiduals",      "NA"),
    ("RES",   "PRR\nResiduals Std",         "FAIL"),
    ("RES",   "% High PRR\nResiduals",      "PASS"),
    ("RES",   "Med Norm PRR\nResid RMS",    "PASS"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Style constants
# ─────────────────────────────────────────────────────────────────────────────
SEC_COL = {
    "BASIC": "#1565C0",   # deep blue
    "TIME":  "#2E7D32",   # deep green
    "ADR":   "#E65100",   # deep orange
    "RES":   "#6A1B9A",   # deep purple
}
STATUS_SCORE = {"PASS": 0.04, "FAIL": 1.00, "NA": 0.48}

PASS_ZONE_R  = 0.32       # radius of inner green "pass" circle
LABEL_R      = 1.23       # radius at which check labels are placed
FILL_COLOR   = "#263238"  # dark blue-grey for the data polygon
FILL_ALPHA   = 0.30
BG_COLOR     = "#F5F5F5"

# ─────────────────────────────────────────────────────────────────────────────
# Polar angles  (clockwise from top / 12 o'clock)
# ─────────────────────────────────────────────────────────────────────────────
N      = len(CHECKS)
angles = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, N, endpoint=False)
scores = np.array([STATUS_SCORE[c[2]] for c in CHECKS])

# Close polygon
ang_c = np.append(angles, angles[0])
sc_c  = np.append(scores, scores[0])

# ─────────────────────────────────────────────────────────────────────────────
# Figure
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 16), subplot_kw=dict(polar=True))
fig.patch.set_facecolor("white")
ax.set_facecolor(BG_COLOR)

theta = np.linspace(0, 2 * np.pi, 720)

# ── Inner "pass" zone ────────────────────────────────────────────────────────
ax.fill(theta, np.full_like(theta, PASS_ZONE_R),
        color="#C8E6C9", alpha=0.60, zorder=1)
ax.plot(theta, np.full_like(theta, PASS_ZONE_R),
        color="#388E3C", lw=1.2, ls="--", alpha=0.90, zorder=2)

# ── Concentric reference rings ────────────────────────────────────────────────
for r in (0.2, 0.4, 0.6, 0.8, 1.0):
    ax.plot(theta, np.full_like(theta, r),
            color="#90A4AE", lw=0.65, ls="--", alpha=0.75, zorder=1)

# ── Outer boundary ────────────────────────────────────────────────────────────
ax.plot(theta, np.ones_like(theta), color="#37474F", lw=1.2, zorder=2)

# ── Spoke lines (section-coloured) ────────────────────────────────────────────
for i, (sec, _, _st) in enumerate(CHECKS):
    ax.plot([angles[i], angles[i]], [0, 1.0],
            color=SEC_COL[sec], lw=0.55, alpha=0.40, zorder=1)

# ── Main data polygon ─────────────────────────────────────────────────────────
ax.fill(ang_c, sc_c, color=FILL_COLOR, alpha=FILL_ALPHA, zorder=3)
ax.plot(ang_c, sc_c, color=FILL_COLOR, lw=0.9, zorder=4)

# ── Data-point markers (coloured by section) ──────────────────────────────────
MARKER = {"PASS": ("o", 7), "FAIL": ("o", 7), "NA": ("D", 4)}
for i, (sec, _, st) in enumerate(CHECKS):
    mk, ms = MARKER[st]
    ax.plot(angles[i], scores[i], mk,
            color=SEC_COL[sec], markersize=ms,
            markeredgecolor="white", markeredgewidth=0.7, zorder=5)

# Centre dot
ax.plot(0, 0, "o", color=FILL_COLOR, markersize=5, zorder=6)

# ── Labels ────────────────────────────────────────────────────────────────────
for i, (sec, label, st) in enumerate(CHECKS):
    a   = angles[i]
    col = SEC_COL[sec]
    fw  = "bold" if st != "NA" else "normal"
    ca, sa = np.cos(a), np.sin(a)
    ha  = "left"   if ca >  0.15 else ("right" if ca < -0.15 else "center")
    va  = "bottom" if sa >  0.15 else ("top"   if sa < -0.15 else "center")
    ax.text(a, LABEL_R, label,
            ha=ha, va=va, fontsize=6.8, color=col,
            fontweight=fw, multialignment=ha, linespacing=1.3)


# ── Remove default polar decorations ─────────────────────────────────────────
ax.set_yticks([])
ax.set_xticks([])
ax.spines["polar"].set_visible(False)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    mpatches.Patch(color=SEC_COL["BASIC"], label="Basic Checks  (14)"),
    mpatches.Patch(color=SEC_COL["TIME"],  label="Time          (8)"),
    mpatches.Patch(color=SEC_COL["ADR"],   label="ADR/PRR/PR    (7)"),
    mpatches.Patch(color=SEC_COL["RES"],   label="Residuals     (12)"),
    mpatches.Patch(facecolor="#C8E6C9", edgecolor="#388E3C",
                   lw=1.5, ls="--", label="Pass zone  (centre)"),
    plt.Line2D([0], [0], marker="D", color="w", markerfacecolor="#90A4AE",
               markersize=6, label="N/A  (mid-ring)"),
]
ax.legend(handles=legend_handles,
          loc="upper right", bbox_to_anchor=(1.40, 1.12),
          fontsize=9, title="Section", title_fontsize=9,
          framealpha=0.93, edgecolor="#B0BEC5")

# ── Title ─────────────────────────────────────────────────────────────────────
fig.suptitle(
    f"GNSS Quality Radar\n{DEVICE}\n"
    f"Centre = PASS / Better    |    Outer = FAIL / Worse    |    Score: {SCORE}",
    fontsize=12, fontweight="bold", y=0.985, va="top")

# ─────────────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=1.5)
out = OUTPUT_DIR / "gnss_radar_inverted.png"
plt.savefig(out, dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print(f"Saved: {out}")
