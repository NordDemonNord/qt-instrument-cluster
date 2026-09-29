#!/usr/bin/env python3
"""Apply ISO / ECE tell-tale colors to embedded indicators 34-40 in panel.svg."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "assets" / "panel.svg"

# ECE R48 / ISO 2575 — те же семейства цветов, что у №24–30 в Main.qml
ISO_COLORS = {
    34: "#e31e24",  # давление масла — красный
    35: "#00a000",  # педаль тормоза — зелёный
    36: "#f5b800",  # задние ПТФ — жёлтый
    37: "#00a000",  # передние ПТФ — зелёный
    38: "#0099ff",  # дальний свет — синий
    39: "#00a000",  # ближний свет — зелёный
    40: "#00a000",  # габариты — зелёный
}

MARKER_END = "    <!-- #30 капот"


def extract_block(panel: str, num: int) -> tuple[str, int, int]:
    start = panel.find(f"<!-- #{num} ")
    if start < 0:
        raise SystemExit(f"marker for #{num} not found")
    end = panel.find("\n    <!-- #", start + 1)
    if end < 0 or num == 34:
        end = panel.find(MARKER_END, start)
    if end < 0:
        raise SystemExit(f"end marker for #{num} not found")
    return panel[start:end], start, end


def colorize_block(block: str, color: str) -> str:
    block = re.sub(
        r'style="fill:#ffffff;stroke:#ffffff"',
        f'style="fill:{color};stroke:{color}"',
        block,
        count=1,
    )
    block = block.replace('fill="#ffffff"', f'fill="{color}"')
    block = block.replace('stroke="#ffffff"', f'stroke="{color}"')
    block = re.sub(r"fill:#ffffff(?=[;\"'])", f"fill:{color}", block)
    block = re.sub(r"stroke:#ffffff(?=[;\"'\s])", f"stroke:{color}", block)
    return block


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    for num in sorted(ISO_COLORS):
        block, start, end = extract_block(panel, num)
        colored = colorize_block(block, ISO_COLORS[num])
        panel = panel[:start] + colored + panel[end:]
        print(f"#{num}: {ISO_COLORS[num]}")
    PANEL.write_text(panel, encoding="utf-8")


if __name__ == "__main__":
    main()
