#!/usr/bin/env python3
"""Align warning-strip indicators on X and emit QML label Y values."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "assets" / "panel.svg"
MAIN_QML = ROOT / "Main.qml"
ICON_CX = 631.0
LABEL_X_SVG = 643.0  # anchorX для подписей

# Visual anchor in icon coordinates (from embedded panel content).
ANCHORS = {
    1: (134.53328, 101.25519),  # power_steering inner matrix origin
    2: (83.761, 65.847),
    3: (83.0, 65.4),
    4: (83.2, 65.245),  # parking rect center
    6: (50.0, 40.0),  # airbag 100×80
    7: (39.775, 26.515),  # check_engine viewBox center
    8: (100.0, 74.0),  # coolant thermometer visual center
    10: (50.0, 40.0),  # fuel_low 100×80
}

LABELS = {
    1: "Неисправность усилителя руля",
    2: "Неисправность тормозной системы",
    3: "Неисправность системы ABS",
    4: "Включён стояночный тормоз",
    6: "Неисправность подушек",
    7: "Неисправность двигателя",
    8: "Перегрев охлаждающей жидкости",
    10: "Низкий уровень топлива в баке",
}


def main() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    results: list[tuple[int, float, float, float, float]] = []

    for num in [1, 2, 3, 4, 6, 7, 8, 10]:
        m = re.search(
            rf'id="indicator-{num}"[^>]*transform="matrix\(([-\d.eE]+),0,0,([-\d.eE]+),([-\d.eE]+),([-\d.eE]+)\)"',
            panel,
        )
        if not m:
            raise SystemExit(f"indicator-{num} not found")
        sx, sy, tx, ty = map(float, m.groups())
        ax, ay = ANCHORS[num]
        cx = tx + ax * sx
        cy = ty + ay * sy
        new_tx = ICON_CX - ax * sx
        results.append((num, sx, sy, new_tx, ty, cy))

        old = m.group(0)
        new = re.sub(
            r"matrix\(([-\d.eE]+),0,0,([-\d.eE]+),([-\d.eE]+),([-\d.eE]+)\)",
            f"matrix({sx:.8g},0,0,{sy:.8g},{new_tx:.5f},{ty:.5f})",
            old,
        )
        panel = panel.replace(old, new, 1)
        print(f"#{num}: center=({cx:.2f},{cy:.2f}) tx {tx:.3f}->{new_tx:.3f}")

    PANEL.write_text(panel, encoding="utf-8")

    qml = MAIN_QML.read_text(encoding="utf-8")
    block = "        readonly property var warningStripLabels: [\n"
    lines = []
    for num, _, _, _, _, cy in results:
        lines.append(f'            {{ centerYSvg: {cy:.2f}, text: "{LABELS[num]}" }}')
    block += ",\n".join(lines) + "\n        ]"

    qml = re.sub(
        r"        readonly property var warningStripLabels: \[[\s\S]*?\n        \]",
        block,
        qml,
        count=1,
    )
    MAIN_QML.write_text(qml, encoding="utf-8")
    print("\nUpdated Main.qml warningStripLabels")


if __name__ == "__main__":
    main()
