#!/usr/bin/env python3
"""
run_analysis.py -- One-command GNSS log analysis runner
=======================================================
Usage (from the project root):
    python scripts/run_analysis.py Log3
    python scripts/run_analysis.py Log3 --device "My Custom Label"
    python scripts/run_analysis.py Log3 --threshold 200

What it does automatically:
    1. Finds the gnss_log_*.txt file in <LOG_DIR>
    2. Parses the GnssLogger header -> device name, Android version, chipset
    3. Chooses BiasUncertaintyNanos threshold:
         MPSS.HI chipsets -> 200 ns  (Snapdragon Gen 1 modem, reports 75-129 ns)
         everything else  ->  40 ns  (standard Google threshold)
    4. Patches the config cell of gnss_quality_analysis_v2.ipynb (in a temp copy)
    5. Executes the notebook via nbconvert
    6. Saves the executed notebook to <LOG_DIR>/outputs/gnss_quality_analysis_v2_<LOG_DIR>.ipynb
    7. Cleans up the temp copy

The master notebook (scripts/gnss_quality_analysis_v2.ipynb) is NEVER modified.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent   # project root
SCRIPTS   = Path(__file__).resolve().parent           # scripts/
MASTER_NB = SCRIPTS / "gnss_quality_analysis_v2.ipynb"

# ── Chipset -> threshold table ─────────────────────────────────────────────────
# Add new chipset families here if needed.
THRESHOLD_MAP = {
    "MPSS.HI": 200.0,   # Snapdragon Gen 1 modem (75-129 ns typical)
}
DEFAULT_THRESHOLD = 40.0


# ─────────────────────────────────────────────────────────────────────────────
def parse_gnsslogger_header(txt_path):
    """
    Read the GnssLogger header comment and extract:
        manufacturer, model, android_version, chipset
    Example header line:
        # Version: v3.1.1.2 Platform: 16 Manufacturer: Sony Model: XQ-GE54
          GNSS Hardware Model Name: qcom;MPSS.DE.9.0...;
    """
    with open(txt_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if "Version:" not in line or "Manufacturer:" not in line:
                continue

            def get(pattern):
                m = re.search(pattern, line)
                return m.group(1).strip() if m else "Unknown"

            manufacturer = get(r"Manufacturer:\s*(\S+)")
            model        = get(r"Model:\s*(\S+)")
            android      = get(r"Platform:\s*(\S+)")
            # Format: "GNSS Hardware Model Name: qcom;MPSS.DE.9.0.c2-...;"
            # Match the chipset family identifier after the vendor prefix
            m_chip = re.search(
                r"GNSS Hardware Model Name:\s*\S+;([A-Z]+\.[A-Z]+\.[\d]+(?:\.\d+)*)",
                line)
            chipset = m_chip.group(1).strip() if m_chip else ""
            return dict(manufacturer=manufacturer, model=model,
                        android=android, chipset=chipset)
    return dict(manufacturer="Unknown", model="Unknown", android="?", chipset="")


def choose_threshold(chipset):
    for key, val in THRESHOLD_MAP.items():
        if key in chipset:
            return val
    return DEFAULT_THRESHOLD


# ─────────────────────────────────────────────────────────────────────────────
def patch_and_execute(log_dir_name, device_label, bias_thresh, log_dir):
    """Clone master notebook -> patch config cell -> execute -> save to outputs/."""
    temp_nb    = SCRIPTS / f"_run_{log_dir_name}.ipynb"
    output_dir = log_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_nb  = output_dir / f"gnss_quality_analysis_v2_{log_dir_name}.ipynb"

    # 1. Clone master notebook
    nb = json.loads(MASTER_NB.read_text(encoding="utf-8"))

    # 2. Patch the config cell
    # Note: Jupyter may store the cell source as a single multi-line string
    # inside a one-element list, or as a proper list of lines. Handle both.
    patched = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if "LOG_DIR" in src and "DEVICE_NAME" in src and "BIAS_UNC_THRESH" in src:
            src = re.sub(
                r'LOG_DIR\s*=\s*r"[^"]*"',
                f'LOG_DIR          = r"../{log_dir_name}"',
                src)
            src = re.sub(
                r'DEVICE_NAME\s*=\s*"[^"]*"',
                f'DEVICE_NAME      = "{device_label}"',
                src)
            src = re.sub(
                r'BIAS_UNC_THRESH\s*=\s*[\d.]+',
                f'BIAS_UNC_THRESH  = {bias_thresh}',
                src)
            # Preserve the original storage format
            cell["source"] = [src] if len(cell["source"]) == 1 else src.splitlines(keepends=True)
            patched = True
            break

    if not patched:
        print("ERROR: could not find the config cell in the master notebook.")
        print("Make sure it contains LOG_DIR, DEVICE_NAME, and BIAS_UNC_THRESH.")
        sys.exit(1)

    temp_nb.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3. Execute
    print("Executing notebook...  (this may take ~30 s)")
    result = subprocess.run(
        [
            "jupyter", "nbconvert", "--to", "notebook", "--execute",
            "--ExecutePreprocessor.timeout=300",
            str(temp_nb),
            "--output", temp_nb.name,
            "--output-dir", str(SCRIPTS),
        ],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print("NOTEBOOK EXECUTION FAILED:\n")
        print(result.stderr[-3000:])
        temp_nb.unlink(missing_ok=True)
        sys.exit(1)

    # 4. Move executed notebook to outputs/
    shutil.move(str(temp_nb), str(output_nb))
    print(f"\nDone.")
    print(f"Executed notebook -> {output_nb.relative_to(ROOT)}")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Run GNSS quality analysis on a log folder.")
    parser.add_argument("log_dir",
        help="Log folder name relative to project root, e.g. Log3")
    parser.add_argument("--device", default=None,
        help="Override auto-detected device label")
    parser.add_argument("--threshold", type=float, default=None,
        help="Override BiasUncertaintyNanos threshold (ns). Default: auto-detect")
    args = parser.parse_args()

    log_dir_name = args.log_dir.rstrip("/\\")
    log_dir      = ROOT / log_dir_name

    if not log_dir.is_dir():
        print(f"ERROR: '{log_dir}' is not a directory.")
        sys.exit(1)

    txt_files = sorted(log_dir.glob("gnss_log_*.txt"))
    if not txt_files:
        print(f"ERROR: no gnss_log_*.txt found in '{log_dir}'")
        sys.exit(1)
    txt_path = txt_files[0]

    info         = parse_gnsslogger_header(txt_path)
    device_label = args.device or (
        f"{info['manufacturer']} {info['model']} (Android {info['android']})"
    )
    bias_thresh  = args.threshold if args.threshold is not None \
                   else choose_threshold(info["chipset"])

    sep  = "-" * 52
    note = " <- relaxed for MPSS.HI" if bias_thresh > 40 else ""
    print(sep)
    print(f"  Log dir    : {log_dir_name}")
    print(f"  Log file   : {txt_path.name}")
    print(f"  Device     : {device_label}")
    print(f"  Chipset    : {info['chipset'] or '(not detected)'}")
    print(f"  Bias thresh: {bias_thresh} ns{note}")
    print(sep + "\n")

    patch_and_execute(log_dir_name, device_label, bias_thresh, log_dir)


if __name__ == "__main__":
    main()
