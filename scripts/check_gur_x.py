#!/usr/bin/env python3
"""Verify warning strip indicators share panel X center (~ICON_CX)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "assets" / "panel.svg"
ICONS = ROOT / "assets" / "icons"
ICON_CX = 642.0
ISO_HUB_X = 83.761
TARGET_PX = 13
NUMS = [1, 2, 3, 4, 6, 7, 8, 10]
FILES = {
    1: "power_steering.svg",
    2: "brake_system.svg",
    3: "abs.svg",
    4: "parking_brake.svg",
    6: "airbag.svg",
    7: "check_engine.svg",
    8: "coolant_temp.svg",
    10: "fuel_low.svg",
}

panel = PANEL.read_text(encoding="utf-8")


def read_hub(file_name: str) -> float | None:
    text = (ICONS / file_name).read_text(encoding="utf-8")
    m = re.search(
        r'translate\(([-\d.]+),([-\d.]+)\)\s+scale\([^)]+\)\s+scale\(1,-1\)',
        text,
    )
    return float(m.group(1)) if m else None


def parse_vb(file_name: str) -> tuple[float, float]:
    text = (ICONS / file_name).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="[^"]*\s+([\d.]+)\s+([\d.]+)"', text)
    if vb:
        return float(vb.group(1)), float(vb.group(2))
    w = re.search(r'width="([\d.]+)"', text)
    h = re.search(r'height="([\d.]+)"', text)
    return float(w.group(1)), float(h.group(1))


print(f"Target panel X = {ICON_CX}")
for num in NUMS:
    m = re.search(
        rf'id="indicator-{num}"[^>]*transform="matrix\(([-\d.]+),0,0,([-\d.]+),([-\d.]+),([-\d.]+)\)"',
        panel,
    )
    if not m:
        print(f"  #{num}: MISSING")
        continue
    scale, _, tx, ty = map(float, m.groups())
    fn = FILES[num]
    iw, ih = parse_vb(fn)
    hub_x = read_hub(fn)
    if hub_x is not None:
        panel_x = tx + hub_x * scale
    else:
        panel_x = tx + ISO_HUB_X * scale
    print(f"  #{num} tx={tx:.2f} scale={scale:.5f} hub_x={hub_x or ISO_HUB_X:.3f} -> panel X={panel_x:.3f}")
