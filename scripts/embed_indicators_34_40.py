#!/usr/bin/env python3
"""Embed indicators 34-40 into panel.svg as white icons."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "assets" / "icons"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

# Слева направо: 40 … 34 (примерные X — поправите в Inkscape)
INDICATORS = [
    (40, "side_lamps.svg", "габаритные огни", 434.0),
    (39, "low_beam.svg", "ближний свет", 455.2),
    (38, "high_beam.svg", "дальний свет", 476.3),
    (37, "fog_front.svg", "передние ПТФ", 497.5),
    (36, "fog_rear.svg", "задние ПТФ", 518.7),
    (35, "auto_hold.svg", "педаль тормоза", 539.8),
    (34, "oil_pressure.svg", "давление масла", 561.0),
]

TARGET_PX = 24
CENTER_Y = 569.8435
INSERT_BEFORE = "    <!-- #30 капот"


def parse_size(svg_root: ET.Element) -> tuple[float, float]:
    vb = svg_root.get("viewBox")
    if vb:
        parts = [float(x) for x in vb.split()]
        return parts[2], parts[3]
    w = float(re.sub(r"px$", "", svg_root.get("width", "100")))
    h = float(re.sub(r"px$", "", svg_root.get("height", "100")))
    return w, h


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def is_background_rect(elem: ET.Element, w: float, h: float) -> bool:
    if strip_ns(elem.tag) != "rect":
        return False
    try:
        rw = float(elem.get("width", "0"))
        rh = float(elem.get("height", "0"))
    except ValueError:
        return False
    return rw * rh >= 0.45 * w * h


def is_background_path(elem: ET.Element, w: float, h: float) -> bool:
    if strip_ns(elem.tag) != "path":
        return False
    d = elem.get("d", "")
    m = re.match(
        r"[Mm]\s*([\d.]+)[,\s]+([\d.]+)\s*[Hh]\s*([\d.]+)\s*[Vv]\s*([\d.]+)\s*[Hh]",
        d.replace(",", " "),
    )
    if not m:
        return False
    x1, y1, x2, y2 = map(float, m.groups())
    rw = abs(x2 - x1)
    rh = abs(y2 - y1)
    return rw * rh >= 0.45 * w * h


def clone_white(elem: ET.Element, w: float, h: float) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in {"metadata", "defs", "title", "desc", "namedview"}:
        return None
    if is_background_rect(elem, w, h) or is_background_path(elem, w, h):
        return None

    out = ET.Element(elem.tag, attrib=dict(elem.attrib))
    if tag in {"path", "circle", "rect", "ellipse", "polygon", "polyline", "line"}:
        out.attrib.pop("id", None)
        if out.get("fill") not in {None, "none", "transparent"}:
            out.set("fill", "#ffffff")
        if out.get("stroke") not in {None, "none", "transparent"}:
            out.set("stroke", "#ffffff")
        style = out.get("style", "")
        if style:
            style = re.sub(r"fill:[^;]+", "fill:#ffffff", style)
            style = re.sub(r"stroke:[^;]+", "stroke:#ffffff", style)
            out.set("style", style)
    for child in elem:
        c = clone_white(child, w, h)
        if c is not None:
            out.append(c)
    if tag == "g" and len(out) == 0:
        return None
    return out


def icon_inner_xml(icon_path: Path) -> tuple[str, float, float]:
    tree = ET.parse(icon_path)
    root = tree.getroot()
    w, h = parse_size(root)
    wrapper = ET.Element(f"{{{SVG_NS}}}g")
    for child in root:
        c = clone_white(child, w, h)
        if c is not None:
            wrapper.append(c)
    inner = "".join(ET.tostring(c, encoding="unicode") for c in wrapper)
    inner = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', "", inner)
    inner = re.sub(r"<[^>]*namedview[^>]*/>", "", inner, flags=re.IGNORECASE)
    return inner, w, h


def make_group(num: int, label: str, file_name: str, cx: float, inner: str, iw: float, ih: float) -> str:
    scale = TARGET_PX / max(iw, ih)
    tx = cx - (iw * scale) / 2
    ty = CENTER_Y - (ih * scale) / 2
    return (
        f"    <!-- #{num} {label} — assets/icons/{file_name} -->\n"
        f"    <g\n"
        f'   id="indicator-{num}"\n'
        f'   inkscape:label="#{num} {label}"\n'
        f'   transform="matrix({scale:.6f},0,0,{scale:.6f},{tx:.5f},{ty:.5f})"\n'
        f'   style="fill:#ffffff;stroke:#ffffff">\n'
        f"{inner}\n"
        f"    </g>\n"
    )


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    if INSERT_BEFORE not in panel:
        raise SystemExit(f"Marker not found: {INSERT_BEFORE!r}")

    blocks = []
    for num, file_name, label, cx in INDICATORS:
        inner, iw, ih = icon_inner_xml(ICONS_DIR / file_name)
        blocks.append(make_group(num, label, file_name, cx, inner, iw, ih))

    panel = panel.replace(INSERT_BEFORE, "".join(blocks) + INSERT_BEFORE, 1)
    PANEL.write_text(panel, encoding="utf-8")
    print(f"Embedded indicators 34-40 into {PANEL.name}")


if __name__ == "__main__":
    main()
