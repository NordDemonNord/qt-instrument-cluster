#!/usr/bin/env python3
"""Embed indicators 35-39 into panel.svg as white icons for Inkscape placement."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "assets" / "icons"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

INDICATORS = [
    (39, "low_beam.svg", "ближний свет", 455.2),
    (38, "high_beam.svg", "дальний свет", 476.3),
    (37, "fog_front.svg", "передние ПТФ", 497.5),
    (36, "fog_rear.svg", "задние ПТФ", 518.7),
    (35, "auto_hold.svg", "педаль тормоза", 539.8),
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


def is_background_rect(elem: ET.Element, w: float, h: float) -> bool:
    if elem.tag != f"{{{SVG_NS}}}rect":
        return False
    try:
        rw = float(elem.get("width", "0"))
        rh = float(elem.get("height", "0"))
    except ValueError:
        return False
    return rw * rh >= 0.45 * w * h


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def clone_white(elem: ET.Element, w: float, h: float) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in {"metadata", "defs", "title", "desc", "namedview"}:
        return None
    if is_background_rect(elem, w, h):
        return None

  # skip huge background paths (low_beam green box)
    if tag == "path":
        d = elem.get("d", "")
        if re.match(r"[Mm]\s*[\d.]+\s+[\d.]+\s*[Hh]\s*[\d.]+\s*[Vv]\s*[\d.]+\s*[Hh]", d):
            return None

    out = ET.Element(elem.tag, attrib=dict(elem.attrib))
    if tag in {"path", "circle", "rect", "ellipse", "polygon", "polyline", "line"}:
        out.attrib.pop("id", None)
        if "fill" in out.attrib and out.attrib.get("fill") not in {"none", "transparent"}:
            out.set("fill", "#ffffff")
        if "stroke" in out.attrib and out.attrib.get("stroke") not in {"none", "transparent"}:
            out.set("stroke", "#ffffff")
        style = out.get("style", "")
        if style:
            style = re.sub(r"fill:[^;]+", "fill:#ffffff", style)
            style = re.sub(r"stroke:[^;]+", "stroke:#ffffff", style)
            style = re.sub(r"fill-opacity:[^;]+", "fill-opacity:1", style)
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
    gid = f"indicator-{num}"
    return (
        f"    <!-- #{num} {label} — assets/icons/{file_name} -->\n"
        f"    <g\n"
        f'   id="{gid}"\n'
        f'   inkscape:label="#{num} {label}"\n'
        f'   transform="matrix({scale:.6f},0,0,{scale:.6f},{tx:.5f},{ty:.5f})"\n'
        f'   style="fill:#ffffff;stroke:#ffffff">\n'
        f"{inner}\n"
        f"    </g>\n"
    )


def strip_existing_35_39(panel: str) -> str:
    """Remove any prior embed of indicators 35-39 (idempotent re-run)."""
    while True:
        m = re.search(
            r"\n    <!-- #3[5-9][^\n]*\n    <g\n   id=\"indicator-3[5-9]\"",
            panel,
        )
        if not m:
            break
        start = m.start()
        depth = 0
        i = panel.index("<g", m.start())
        while i < len(panel):
            if panel.startswith("<g", i) and (i + 2 == len(panel) or panel[i + 2] in " \n\t>"):
                depth += 1
                i += 2
                continue
            if panel.startswith("</g>", i):
                depth -= 1
                i += 4
                if depth == 0:
                    panel = panel[:start] + panel[i:]
                    break
                continue
            i += 1
        else:
            break
    return panel


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    panel = strip_existing_35_39(panel)

    blocks = []
    for num, file_name, label, cx in INDICATORS:
        inner, iw, ih = icon_inner_xml(ICONS_DIR / file_name)
        blocks.append(make_group(num, label, file_name, cx, inner, iw, ih))

    marker = INSERT_BEFORE
    if marker not in panel:
        raise SystemExit(f"Marker not found: {marker!r}")
    idx = panel.index(marker)
    panel = panel[:idx] + "".join(blocks) + panel[idx:]
    PANEL.write_text(panel, encoding="utf-8")
    print(f"Embedded {len(blocks)} indicators into {PANEL.name}")


if __name__ == "__main__":
    main()
