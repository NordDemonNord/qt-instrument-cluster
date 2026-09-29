#!/usr/bin/env python3
"""Indicators 34-40: uniform 24px, Y like #24, mirrored X (40..34 order preserved)."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "assets" / "panel.svg"
ICONS = ROOT / "assets" / "icons"

PANEL_W = 1418
TARGET_PX = 24

# Центр Y индикатора #24 (battery, как в Main.qml / panel.svg)
CENTER_Y = 569.8435

# Доп. смещение по Y в координатах SVG (+ вниз)
Y_OFFSET = {34: 2.0}

# QML centerX для 24-30 (справа); зеркало: 40<->24, 39<->25, …, 34<->30
RIGHT_CENTER = {
    30: 826.94163,
    29: 856.76822,
    28: 888.5948,
    27: 915.35782,
    26: 942.96475,
    25: 970.57168,
    24: 999.4445,
}

# Слева направо: 40 … 34
LEFT_TO_RIGHT = [40, 39, 38, 37, 36, 35, 34]
RIGHT_PAIR = [24, 25, 26, 27, 28, 29, 30]

ICON_FILES = {
    40: "side_lamps.svg",
    39: "low_beam.svg",
    38: "high_beam.svg",
    37: "fog_front.svg",
    36: "fog_rear.svg",
    35: "auto_hold.svg",
    34: "oil_pressure.svg",
}


def icon_size(path: Path) -> tuple[float, float]:
    root = ET.parse(path).getroot()
    vb = root.get("viewBox")
    if vb:
        p = [float(x) for x in vb.split()]
        return p[2], p[3]
    w = float(re.sub(r"px$", "", root.get("width", "100")))
    h = float(re.sub(r"px$", "", root.get("height", "100")))
    return w, h


def mirror_center(right_cx: float) -> float:
    return PANEL_W - right_cx


def make_transform(cx: float, iw: float, ih: float, num: int) -> str:
    scale = TARGET_PX / max(iw, ih)
    tx = cx - (iw * scale) / 2
    ty = CENTER_Y - (ih * scale) / 2 + Y_OFFSET.get(num, 0.0)
    return f"matrix({scale:.6f},0,0,{scale:.6f},{tx:.5f},{ty:.5f})"


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    for left_num, right_num in zip(LEFT_TO_RIGHT, RIGHT_PAIR):
        cx = mirror_center(RIGHT_CENTER[right_num])
        iw, ih = icon_size(ICONS / ICON_FILES[left_num])
        transform = make_transform(cx, iw, ih, left_num)
        pat = re.compile(
            rf'(id="indicator-{left_num}"\n'
            rf'   inkscape:label="#{left_num} [^"]*"\n'
            rf'   transform=")[^"]*(")',
            re.MULTILINE,
        )
        panel, n = pat.subn(rf"\1{transform}\2", panel, count=1)
        if n != 1:
            raise SystemExit(f"indicator-{left_num} not updated")
        print(
            f"#{left_num} mirror #{right_num}: centerX={cx:.2f}, "
            f"centerY={CENTER_Y:.2f}, scale={TARGET_PX/max(iw,ih):.4f}"
        )
    PANEL.write_text(panel, encoding="utf-8")


if __name__ == "__main__":
    main()
