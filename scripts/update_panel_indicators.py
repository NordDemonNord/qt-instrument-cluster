#!/usr/bin/env python3
"""Replace inner SVG for selected indicators in panel.svg (keeps transform)."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "assets" / "icons"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"

UPDATES = {
    35: "auto_hold.svg",
    36: "fog_rear.svg",
    37: "fog_front.svg",
    38: "high_beam.svg",
    39: "low_beam.svg",
}


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


def is_registration(elem: ET.Element) -> bool:
    tag = strip_ns(elem.tag)
    if tag == "g" and elem.get("stroke") in {"#999", "#999999"}:
        return True
    if tag == "path":
        d = elem.get("d", "").replace(",", " ").lower()
        if re.match(r"m0 16v-16h16", d) or re.match(r"m200 16v-16h-16", d):
            return True
    return False


def clone_white(elem: ET.Element) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in {"metadata", "defs", "title", "desc", "namedview"}:
        return None
    if is_registration(elem):
        return None

    out = ET.Element(elem.tag, attrib=dict(elem.attrib))
    if tag == "g":
        if out.get("stroke") not in {None, "none", "transparent"}:
            out.set("stroke", "#ffffff")
        style = out.get("style", "")
        if style and "stroke:" in style:
            style = re.sub(r"stroke:[^;]+", "stroke:#ffffff", style)
            out.set("style", style)
    if tag in {"path", "circle", "rect", "ellipse", "polygon", "polyline", "line"}:
        out.attrib.pop("id", None)
        fill = out.get("fill")
        stroke = out.get("stroke")
        style = out.get("style", "")
        stroke_only = fill == "none" or re.search(r"fill\s*:\s*none", style)
        if stroke_only:
            out.set("fill", "none")
        elif fill in {None, "transparent"} and stroke in {None, "transparent"}:
            out.set("fill", "#ffffff")
        elif fill not in {None, "none", "transparent"}:
            out.set("fill", "#ffffff")
        if stroke not in {None, "none", "transparent"}:
            out.set("stroke", "#ffffff")
        if style:
            if not re.search(r"fill\s*:\s*none", style):
                style = re.sub(r"fill:[^;]+", "fill:#ffffff", style)
            style = re.sub(r"stroke:[^;]+", "stroke:#ffffff", style)
            out.set("style", style)
    for child in elem:
        c = clone_white(child)
        if c is not None:
            out.append(c)
    if tag == "g" and len(out) == 0:
        return None
    return out


def icon_inner_xml(icon_path: Path) -> str:
    root = ET.parse(icon_path).getroot()
    wrapper = ET.Element(f"{{{SVG_NS}}}g")
    for child in root:
        c = clone_white(child)
        if c is not None:
            wrapper.append(c)
    inner = "".join(ET.tostring(c, encoding="unicode") for c in wrapper)
    inner = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', "", inner)
    inner = re.sub(r"</?ns\d+:", lambda m: m.group(0).replace(re.search(r"ns\d+:", m.group(0)).group(0), ""), inner)
    inner = inner.replace("ns0:", "")
    return inner


def replace_inner(panel: str, num: int, inner: str) -> str:
    pat = re.compile(
        rf'(    <!-- #{num}[^\n]*\n'
        rf'    <g\n'
        rf'   id="indicator-{num}"\n'
        rf'   inkscape:label="#{num} [^"]*"\n'
        rf'   transform="[^"]*"\n'
        rf'   style="fill:#ffffff;stroke:#ffffff">)\n'
        rf'[\s\S]*?'
        rf'(\n    </g>)',
        re.MULTILINE,
    )
    m = pat.search(panel)
    if not m:
        raise SystemExit(f"indicator-{num} not found in panel.svg")
    return panel[: m.start()] + m.group(1) + "\n" + inner + m.group(2) + panel[m.end() :]


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    for num, file_name in UPDATES.items():
        inner = icon_inner_xml(ICONS_DIR / file_name)
        panel = replace_inner(panel, num, inner)
        print(f"Updated indicator-{num} from {file_name}")
    PANEL.write_text(panel, encoding="utf-8")


if __name__ == "__main__":
    main()
