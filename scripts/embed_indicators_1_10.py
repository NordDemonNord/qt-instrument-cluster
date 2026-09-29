#!/usr/bin/env python3
"""Embed warning tell-tales №1–4, 6–8, 10 between path131-5* bars in panel.svg."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
PANEL = ROOT / "assets" / "panel.svg"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

TARGET_PX = 13
ICON_CX = 631.0
ISO_HUB_X = 83.761  # circle center in ISO 166.4×130.49 icons
ICON_Y_NUDGE = 0.0
LOCAL_CY = 336.79864  # moveto Y из path131-5
MATRIX_SY = 1.0664542
WY_BASE = MATRIX_SY * LOCAL_CY

INSERT_BEFORE = "    <!-- #13 поворот влево"

COLORS = {
    "red": "#e31e24",
    "amber": "#f5b800",
}

# (num, icon, label_ru, color_mode) — color_mode: red | amber | native
INDICATORS = [
    (1, "power_steering.svg", "Неисправность усилителя руля", "red"),
    (2, "brake_system.svg", "Неисправность тормозной системы", "red"),
    (3, "abs.svg", "Неисправность системы ABS", "amber"),
    (4, "parking_brake.svg", "Включён стояночный тормоз", "native"),
    (6, "airbag.svg", "Неисправность подушек", "red"),
    (7, "check_engine.svg", "Неисправность двигателя", "amber"),
    (8, "coolant_temp.svg", "Перегрев охлаждающей жидкости", "red"),
    (10, "fuel_low.svg", "Низкий уровень топлива в баке", "amber"),
]

SKIP_TAGS = {"metadata", "defs", "title", "desc", "namedview", "sodipodi:namedview"}


def read_icon_hub(icon_path: Path) -> tuple[float, float] | None:
    text = icon_path.read_text(encoding="utf-8")
    m = re.search(
        r'translate\(([-\d.]+),([-\d.]+)\)\s+scale\([^)]+\)\s+scale\(1,-1\)',
        text,
    )
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))


def embed_cx(file_name: str, iw: float, ih: float) -> float:
    scale = TARGET_PX / max(iw, ih)
    hub = read_icon_hub(ICONS / file_name)
    if hub is None:
        return ICON_CX
    hub_x, _ = hub
    return ICON_CX - (hub_x - ISO_HUB_X) * scale


def parse_matrix_ty(panel: str) -> list[float]:
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
    ty_values: list[float] = []
    for pid in ids:
        m = re.search(
            rf'id="{re.escape(pid)}"[^>]*transform="matrix\([^,]+,[^,]+,[^,]+,[^,]+,[^,]+,([^)]+)\)"',
            panel,
        )
        if not m:
            raise SystemExit(f"Bar path not found: {pid}")
        ty_values.append(float(m.group(1)))
    return ty_values


def bar_center_y(ty: float) -> float:
    return WY_BASE + ty


def gap_centers(ty_values: list[float]) -> list[float]:
    ys = [bar_center_y(ty) for ty in ty_values]
    return [(ys[i] + ys[i + 1]) / 2 for i in range(len(ys) - 1)]


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


def clone_passthrough(elem: ET.Element) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in SKIP_TAGS:
        return None
    out = ET.Element(elem.tag, attrib=dict(elem.attrib))
    for child in elem:
        c = clone_passthrough(child)
        if c is not None:
            out.append(c)
    if tag == "g" and len(out) == 0:
        return None
    return out


def clone_colored(
    elem: ET.Element, w: float, h: float, hex_color: str, skip_rects: bool
) -> ET.Element | None:
    tag = strip_ns(elem.tag)
    if tag in SKIP_TAGS:
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

    if tag in {"path", "circle", "rect", "ellipse", "polygon", "polyline", "line", "g"}:
        if fill in {"currentColor", "currentcolor"}:
            out.set("fill", hex_color)
        elif fill not in {None, "none", "transparent"}:
            out.set("fill", hex_color)
        if stroke in {"currentColor", "currentcolor"}:
            out.set("stroke", hex_color)
        elif stroke not in {None, "none", "transparent"}:
            out.set("stroke", hex_color)
        if style:
            if "currentColor" in style or "currentcolor" in style:
                style = re.sub(r"fill:[^;]+", f"fill:{hex_color}", style)
                style = re.sub(r"stroke:[^;]+", f"stroke:{hex_color}", style)
            else:
                style = re.sub(r"fill:[^;]+", f"fill:{hex_color}", style)
                style = re.sub(r"stroke:[^;]+", f"stroke:{hex_color}", style)
            out.set("style", style)

    for child in elem:
        c = clone_colored(child, w, h, hex_color, skip_rects)
        if c is not None:
            out.append(c)
    if tag == "g" and len(out) == 0:
        return None
    return out


def icon_inner(icon_path: Path, color_mode: str) -> tuple[str, float, float]:
    root = ET.parse(icon_path).getroot()
    w, h = parse_size(root)
    wrapper = ET.Element(f"{{{SVG_NS}}}g")

    if color_mode == "native":
        clone_fn = clone_passthrough
        for child in root:
            c = clone_fn(child)
            if c is not None:
                wrapper.append(c)
    else:
        hex_color = COLORS[color_mode]
        skip_rects = "turn_" in icon_path.name
        for child in root:
            c = clone_colored(child, w, h, hex_color, skip_rects)
            if c is not None:
                wrapper.append(c)

    inner = "".join(ET.tostring(c, encoding="unicode") for c in wrapper)
    inner = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', "", inner)
    return inner, w, h


def icon_group(
    num: int, label: str, file_name: str, cx: float, cy: float, color_mode: str
) -> str:
    inner, iw, ih = icon_inner(ICONS / file_name, color_mode)
    scale = TARGET_PX / max(iw, ih)
    tx = cx - (iw * scale) / 2
    ty = cy - (ih * scale) / 2
    if color_mode == "native":
        style_attr = ""
    else:
        hex_color = COLORS[color_mode]
        style_attr = f'\n   style="fill:{hex_color};stroke:{hex_color}"'
    return (
        f"    <!-- #{num} {label} — assets/icons/{file_name} -->\n"
        f"    <g\n"
        f'   id="indicator-{num}"\n'
        f'   inkscape:label="#{num} {label}"\n'
        f'   transform="matrix({scale:.6f},0,0,{scale:.6f},{tx:.5f},{ty:.5f})"'
        f"{style_attr}>\n"
        f"{inner}\n"
        f"    </g>\n"
    )


def remove_g_block(panel: str, g_open: int) -> str:
    depth = 0
    i = g_open
    while i < len(panel):
        if panel.startswith("<g", i) and (i + 2 == len(panel) or panel[i + 2] in " \n\t>"):
            depth += 1
            i += 2
            continue
        if panel.startswith("</g>", i):
            depth -= 1
            i += 4
            if depth == 0:
                end = i
                while end < len(panel) and panel[end] in " \t\n":
                    end += 1
                return panel[:g_open] + panel[end:]
            continue
        i += 1
    return panel


def strip_existing(panel: str) -> str:
    nums = {n for n, *_ in INDICATORS}
    for num in sorted(nums):
        needle = f'id="indicator-{num}"'
        while True:
            pos = panel.find(needle)
            if pos < 0:
                break
            g_open = panel.rfind("<g", 0, pos)
            if g_open < 0:
                break
            comment_start = panel.rfind("\n", 0, g_open)
            line_start = comment_start + 1 if comment_start >= 0 else 0
            if panel[line_start:g_open].strip().startswith("<!-- #"):
                panel = panel[:line_start] + panel[g_open:]
                g_open = line_start
            panel = remove_g_block(panel, g_open)
    for num in nums:
        panel = re.sub(
            rf"\n?<!-- #{num} [^\n]*-->\n?",
            "\n",
            panel,
        )
    return panel


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    ty_values = parse_matrix_ty(panel)
    ys = gap_centers(ty_values)

    panel = strip_existing(panel)
    if INSERT_BEFORE not in panel:
        raise SystemExit(f"Insert marker not found: {INSERT_BEFORE!r}")
    if len(ys) != len(INDICATORS):
        raise SystemExit(f"Expected {len(INDICATORS)} gaps, got {len(ys)}")

    blocks = []
    for (num, file_name, label, mode), cy in zip(INDICATORS, ys):
        _, iw, ih = icon_inner(ICONS / file_name, mode)
        cx = embed_cx(file_name, iw, ih)
        blocks.append(icon_group(num, label, file_name, cx, cy + ICON_Y_NUDGE, mode))

    idx = panel.index(INSERT_BEFORE)
    panel = panel[:idx] + "".join(blocks) + panel[idx:]
    panel = re.sub(r"\n{3,}", "\n\n", panel)
    PANEL.write_text(panel, encoding="utf-8")

    print(f"Embedded {len(blocks)} warning indicators into {PANEL.name}")
    print(f"  icon cx={ICON_CX}, size={TARGET_PX}px")
    for (num, _, label, mode), cy in zip(INDICATORS, ys):
        print(f"  #{num} y={cy + ICON_Y_NUDGE:.2f} {mode} — {label}")
    print("\nQML warningStripLabels centerYSvg:")
    for (_, _, label, mode), cy in zip(INDICATORS, ys):
        color_key = "warningRedColor" if mode in {"red", "native"} else "warningAmberColor"
        if mode == "native":
            color_key = "warningRedColor"
        y = cy + ICON_Y_NUDGE
        hex_c = "#808080"
        print(f'            {{ centerYSvg: {y:.2f}, text: "{label}" }},')


if __name__ == "__main__":
    main()
