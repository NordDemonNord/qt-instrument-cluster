#!/usr/bin/env python3
"""Center power_steering path in ISO 166.4x130.49 canvas."""
import re
from pathlib import Path

ICON = Path(__file__).resolve().parents[1] / "assets" / "icons" / "power_steering.svg"
CANVAS_W, CANVAS_H = 166.4, 130.49
ISO_HUB_X, ISO_HUB_Y = 83.761, 65.847
# Визуальный диаметр круга ISO: r + stroke/2 с каждой стороны
ISO_CIRCLE_R = 56.599
ISO_STROKE = 9.3566
TARGET_D = 2 * (ISO_CIRCLE_R + ISO_STROKE / 2)
# Смещение от ISO-хаба (правее и ниже после ручной подгонки)
HUB_X = ISO_HUB_X + 30.5
HUB_Y = ISO_HUB_Y + 22.0

text = ICON.read_text(encoding="utf-8")
path_d = re.search(r'\sd="([^"]+)"', text).group(1)

try:
    from svg.path import parse_path

    p = parse_path(path_d)
    xmin, xmax, ymin, ymax = p.bbox()
except ImportError:
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", path_d)]
    xs = nums[0::2]
    ys = nums[1::2]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

cx = (xmin + xmax) / 2
cy = (ymin + ymax) / 2
pw = xmax - xmin
ph = ymax - ymin
scale = TARGET_D / max(pw, ph)

print(f"bbox: ({xmin:.3f},{ymin:.3f})-({xmax:.3f},{ymax:.3f})")
print(f"center: ({cx:.3f},{cy:.3f}) scale: {scale:.4f}")

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}">
  <g transform="translate({HUB_X:.3f},{HUB_Y:.3f}) scale({scale:.6f}) scale(1,-1) translate({-cx:.6f},{-cy:.6f})">
    <path fill="currentColor" fill-rule="nonzero" d="{path_d}" />
  </g>
</svg>
"""
ICON.write_text(svg, encoding="utf-8")
print(f"Wrote centered {ICON.name}")
