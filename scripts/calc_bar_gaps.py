#!/usr/bin/env python3
import re
from pathlib import Path

panel = Path(__file__).resolve().parents[1] / "assets" / "panel.svg"
text = panel.read_text(encoding="utf-8")
SY = 1.0664542
ids = [
    "path131-5",
    "path131-5-3",
    "path131-5-3-4",
    "path131-5-3-7",
    "path131-5-3-7-6",
    "path131-5-3-7-5",
    "path131-5-3-7-5-0",
    "path131-5-3-7-5-0-8",
    "path131-5-3-7-5-0-3",
]
worlds = []
for pid in ids:
    m = re.search(
        rf'id="{re.escape(pid)}"\s+style="[^"]*"\s+d="([^"]+)"\s+transform="matrix\([^,]+,[^,]+,[^,]+,[^,]+,[^,]+,([^)]+)\)"',
        text,
    )
    if not m:
        raise SystemExit(f"missing {pid}")
    d, ty = m.group(1), float(m.group(2))
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d)]
    yvals = nums[1::2]
    ymid = (min(yvals) + max(yvals)) / 2
    world = SY * ymid + ty
    worlds.append(world)
    print(f"{pid}: world_y={world:.3f}")

print("--- gaps ---")
for i in range(len(worlds) - 1):
    g = (worlds[i] + worlds[i + 1]) / 2
    print(f"gap {i}: {g:.3f}")
