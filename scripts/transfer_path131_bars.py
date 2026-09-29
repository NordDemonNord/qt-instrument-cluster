#!/usr/bin/env python3
"""Transfer path131-5* horizontal bars from example.svg into panel.svg."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "assets" / "example.svg"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"
INK_NS = "http://www.inkscape.org/namespaces/inkscape"

IDS = [
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

LOCAL_CY = 337.76
MATRIX = (0.64841066, 0.0, 0.0, 1.0664542)
TX = 249.63145
TY_EXAMPLE = 12.685097

PATH196_Y = 356.70145
PATH196_1_Y = 535.85087
TRIANGLE_MARGIN = 11.0


def world_center_y(ty: float) -> float:
    return MATRIX[3] * LOCAL_CY + ty


def path_to_snippet(el: ET.Element, ty: float) -> str:
    a, b, c, d = MATRIX
    attrs = [
        f'id="{el.get("id")}"',
        'style="fill:#808080;fill-opacity:1;stroke:#000000;stroke-opacity:0"',
        f'd="{el.get("d", "")}"',
        f'transform="matrix({a},{b},{c},{d},{TX},{ty:.5f})"',
    ]
    pe = el.get(f"{{{INK_NS}}}path-effect")
    od = el.get(f"{{{INK_NS}}}original-d")
    if pe:
        attrs.append(f'inkscape:path-effect="{pe}"')
    if od:
        attrs.append(f'inkscape:original-d="{od}"')
    return "<path\n   " + "\n   ".join(attrs) + " />\n"


def main() -> None:
    y_top = PATH196_Y + TRIANGLE_MARGIN
    y_bottom = PATH196_1_Y - TRIANGLE_MARGIN
    n = len(IDS)
    target_ys = [y_top + (y_bottom - y_top) * (i + 0.5) / n for i in range(n)]
    wy_base = world_center_y(TY_EXAMPLE)

    ex_root = ET.parse(EXAMPLE).getroot()
    source = {}
    for el in ex_root.iter(f"{{{SVG_NS}}}path"):
        pid = el.get("id")
        if pid in IDS:
            source[pid] = el

    missing = [pid for pid in IDS if pid not in source]
    if missing:
        raise SystemExit(f"Missing paths in example.svg: {missing}")

    panel_text = PANEL.read_text(encoding="utf-8")
    for pid in IDS:
        if f'id="{pid}"' in panel_text:
            raise SystemExit(f"{pid} already exists in panel.svg")

    match = re.search(r'\bid="path196"\s*/>', panel_text)
    if not match:
        raise SystemExit("path196 not found in panel.svg")

    snippets = []
    for i, pid in enumerate(IDS):
        ty = TY_EXAMPLE + (target_ys[i] - wy_base)
        snippets.append(path_to_snippet(source[pid], ty))

    insert_block = "".join(snippets)
    updated = panel_text[: match.end()] + "\n" + insert_block + panel_text[match.end() :]
    PANEL.write_text(updated, encoding="utf-8")

    print(f"Inserted {n} paths between path196 (y={PATH196_Y}) and path196-1 (y={PATH196_1_Y})")
    print(f"Y centers: {[round(y, 2) for y in target_ys]}")
    print("X center: 711.0")


if __name__ == "__main__":
    main()
