#!/usr/bin/env python3
"""Embed top-row indicators 13, 15-16, 18, 20 into panel.svg (above path131). №14 — QML."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

TARGET_PX = 20
DEFAULT_CENTER_Y = 322.874  # fallback
# №15 авто и №18 медиа — смещение от №16 навигация (центр между поворотниками)
NAV_ICON_OFFSET_SVG = 40.0

TURN_EMBED_SIZE = (88.0, 88.0)
TURN_LEGACY_PARSE_SIZE = {
    13: (185.12375, 207.99995),
    20: (183.96089, 207.98285),
}

INDICATOR_META = {
    13: ("turn_left.svg", "поворот влево", "green"),
    15: ("standard_mode.svg", "Standard", "white"),
    16: ("navigation_mode.svg", "Навигация", "gray"),
    18: ("media_mode.svg", "Медиа", "gray"),
    20: ("turn_right.svg", "поворот вправо", "green"),
}

PATH131_HEAD = (
    '<path\n   style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-opacity:0"\n'
    '   d="m 805.44569,336.79864'
)
INSERT_BEFORE_PATH131 = re.compile(
    r'transform="matrix\(0\.99913334,0,0,1\.0000121,0\.33457174,-0\.0065842\)"\s*/>\s*(?='
    + re.escape(PATH131_HEAD)
    + r")"
)


def parse_size(root: ET.Element) -> tuple[float, float]:
    vb = root.get("viewBox")
    if vb:
        p = [float(x) for x in vb.split()]
        return p[2], p[3]
    w = float(re.sub(r"px$", "", root.get("width", "100")))
    h = float(re.sub(r"px$", "", root.get("height", "100")))
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


def clone_colored(
    elem: ET.Element, w: float, h: float, mode: str, skip_rects: bool
) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in {"metadata", "defs", "title", "desc", "namedview", "sodipodi:namedview"}:
        return None
    if skip_rects and tag == "rect":
        return None
    if is_background_rect(elem, w, h):
        return None

    out = ET.Element(elem.tag, attrib=dict(elem.attrib))
    if tag in {"path", "circle", "rect", "ellipse", "polygon", "polyline", "line"}:
        out.attrib.pop("id", None)
        fill = out.get("fill")
        stroke = out.get("stroke")
        style = out.get("style", "")

        if mode == "green":
            if fill not in {None, "none", "transparent"}:
                out.set("fill", "#00a000")
            if stroke not in {None, "none", "transparent"}:
                out.set("stroke", "#00a000")
            if style:
                style = re.sub(r"fill:[^;]+", "fill:#00a000", style)
                style = re.sub(r"stroke:[^;]+", "stroke:#00a000", style)
                out.set("style", style)
        elif mode == "gray":
            if fill not in {None, "none", "transparent"}:
                out.set("fill", "#808080")
            if stroke not in {None, "none", "transparent"}:
                out.set("stroke", "none")
            if style:
                style = re.sub(r"fill:[^;]+", "fill:#808080", style)
                style = re.sub(r"stroke:[^;]+", "stroke:none", style)
                out.set("style", style)
        else:
            if fill not in {None, "none", "transparent"}:
                out.set("fill", "#ffffff")
            if stroke not in {None, "none", "transparent"}:
                out.set("stroke", "#ffffff")
            if style:
                style = re.sub(r"fill:[^;]+", "fill:#ffffff", style)
                style = re.sub(r"stroke:[^;]+", "stroke:#ffffff", style)
                out.set("style", style)

    for child in elem:
        c = clone_colored(child, w, h, mode, skip_rects)
        if c is not None:
            out.append(c)
    if tag == "g" and len(out) == 0:
        return None
    return out


def icon_inner(icon_path: Path, mode: str) -> tuple[str, float, float]:
    skip_rects = "turn_" in icon_path.name
    root = ET.parse(icon_path).getroot()
    w, h = parse_size(root)
    wrapper = ET.Element(f"{{{SVG_NS}}}g")
    for child in root:
        c = clone_colored(child, w, h, mode, skip_rects)
        if c is not None:
            wrapper.append(c)
    inner = "".join(ET.tostring(c, encoding="unicode") for c in wrapper)
    inner = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', "", inner)
    return inner, w, h


def icon_group(
    num: int,
    label: str,
    file_name: str,
    cx: float,
    center_y: float,
    mode: str,
    transform_override: str | None = None,
) -> str:
    inner, iw, ih = icon_inner(ICONS / file_name, mode)
    if transform_override:
        transform = transform_override
    else:
        scale = TARGET_PX / max(iw, ih)
        tx = cx - (iw * scale) / 2
        ty = center_y - (ih * scale) / 2
        transform = f"matrix({scale:.6f},0,0,{scale:.6f},{tx:.5f},{ty:.5f})"
    fill_attr = "#00a000" if mode == "green" else "#808080" if mode == "gray" else "#ffffff"
    stroke_attr = fill_attr if mode != "gray" else "none"
    return (
        f"    <!-- #{num} {label} — assets/icons/{file_name} -->\n"
        f"    <g\n"
        f'   id="indicator-{num}"\n'
        f'   inkscape:label="#{num} {label}"\n'
        f'   transform="{transform}"\n'
        f'   style="fill:{fill_attr};stroke:{stroke_attr}">\n'
        f"{inner}\n"
        f"    </g>\n"
    )


def parse_turn_from_panel(panel: str, num: int) -> dict | None:
    pat = rf'id="indicator-{num}"[\s\S]*?transform="matrix\(([\d.]+),0,0,([\d.]+),([\d.]+),([\d.]+)\)"'
    m = re.search(pat, panel)
    if not m:
        return None
    scale = float(m.group(1))
    tx = float(m.group(3))
    ty = float(m.group(4))
    if scale < 0.12:
        iw, ih = TURN_LEGACY_PARSE_SIZE[num]
    else:
        iw, ih = TURN_EMBED_SIZE
    cx = tx + iw * scale / 2
    cy = ty + ih * scale / 2
    return {"cx": cx, "cy": cy}


def layout_from_panel(panel: str) -> tuple[dict[int, float], float, dict[int, str], dict[str, float]]:
    left = parse_turn_from_panel(panel, 13)
    right = parse_turn_from_panel(panel, 20)
    if not left or not right:
        left_cx, right_cx = 577.694, 843.454
        center_y = DEFAULT_CENTER_Y
        turn_transforms: dict[int, str] = {}
    else:
        left_cx, right_cx = left["cx"], right["cx"]
        center_y = (left["cy"] + right["cy"]) / 2
        turn_transforms = {}

    nav_cx = (left_cx + right_cx) / 2
    car_cx = nav_cx - NAV_ICON_OFFSET_SVG
    media_cx = nav_cx + NAV_ICON_OFFSET_SVG
    time_cx = (left_cx + car_cx) / 2
    temp_cx = (media_cx + right_cx) / 2

    positions = {
        13: left_cx,
        15: car_cx,
        16: nav_cx,
        18: media_cx,
        20: right_cx,
    }
    qml_x = {"clock": time_cx, "temp": temp_cx}
    return positions, center_y, turn_transforms, qml_x


TOP_ROW = [13, 15, 16, 18, 20]
PATH131_START = (
    '\n<path\n   style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-opacity:0"\n'
    '   d="m 805.44569,336.79864'
)


def strip_existing(panel: str) -> str:
    for num in [14] + TOP_ROW:
        start = panel.find(f"<!-- #{num} ")
        if start < 0:
            continue
        end = len(panel)
        for other in [14] + TOP_ROW:
            if other <= num:
                continue
            pos = panel.find(f"<!-- #{other} ", start + 1)
            if pos >= 0:
                end = min(end, pos)
        path_pos = panel.find(PATH131_START, start)
        if path_pos >= 0:
            end = min(end, path_pos)
        if end >= len(panel):
            raise SystemExit(f"Cannot find end for indicator {num}")
        panel = panel[:start] + panel[end:]
    return panel


def repair_broken_insert(panel: str) -> str:
    path_end = "-47.8394,0.26523 z\""
    if path_end not in panel or "<!-- #13 " not in panel:
        return panel
    end_idx = panel.find(path_end)
    ind_start = panel.find("<!-- #13 ", end_idx)
    if ind_start < 0 or ind_start > end_idx + len(path_end) + 5:
        return panel
    id_start = panel.find('id="path131"', ind_start)
    if id_start < 0:
        return panel
    return panel[: end_idx + len(path_end)] + "\n   " + panel[id_start:]


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    panel = repair_broken_insert(panel)
    positions, center_y, turn_transforms, qml_x = layout_from_panel(panel)
    panel = strip_existing(panel)

    if not INSERT_BEFORE_PATH131.search(panel):
        raise SystemExit("Insert point before path131 not found")
    blocks = []
    for num in [13, 15, 16, 18, 20]:
        file_name, label, mode = INDICATOR_META[num]
        blocks.append(
            icon_group(
                num,
                label,
                file_name,
                positions[num],
                center_y,
                mode,
                transform_override=turn_transforms.get(num),
            )
        )

    panel = INSERT_BEFORE_PATH131.sub(
        'transform="matrix(0.99913334,0,0,1.0000121,0.33457174,-0.0065842)" />\n'
        + "".join(blocks),
        panel,
        count=1,
    )
    PANEL.write_text(panel, encoding="utf-8")
    print(f"Embedded indicators 13, 15-16, 18, 20 into {PANEL.name}")
    print(f"  turn L cx={positions[13]:.3f}, turn R cx={positions[20]:.3f}; row cy={center_y:.3f}")
    print(f"  #15 car cx={positions[15]:.3f}, #16 nav cx={positions[16]:.3f}, #18 media cx={positions[18]:.3f}")
    print(f"  QML #14 time cx={qml_x['clock']:.3f}, #19 temp cx={qml_x['temp']:.3f}")


if __name__ == "__main__":
    main()
