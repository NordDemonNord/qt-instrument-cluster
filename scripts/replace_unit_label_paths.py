#!/usr/bin/env python3
"""Remove drawn unit-label letter paths from panel.svg."""
import re
from pathlib import Path

PANEL = Path(__file__).resolve().parents[1] / "assets" / "panel.svg"

PATH_IDS = {
    # km/h
    *(f"path{i}" for i in range(108, 116)),
    # km
    "path129",
    "path130",
    "path129-7",
    "path130-3",
    # °C
    "path126",
    "path127",
    # x1000 rpm
    "path167",
    "path168",
    "path169",
    "path170",
    "path171",
    "path172",
    "path173",
    "path174",
    "path169-5",
    "path170-4",
    "path169-7",
    "path170-2",
}

EFFECT_IDS = {
    *(f"path-effect{i}" for i in range(108, 116)),
    "path-effect126",
    "path-effect127",
    "path-effect128",
    "path-effect129",
    "path-effect130",
    "path-effect130-1",
    "path-effect131",
    "path-effect131-7",
    *(f"path-effect{i}" for i in range(167, 176)),
    "path-effect170-1",
    "path-effect170-8",
    "path-effect171-4",
    "path-effect171-7",
}


def main() -> None:
    text = PANEL.read_text(encoding="utf-8")

    path_pattern = re.compile(
        r"<path\b[^>]*\bid=\"(" + "|".join(re.escape(i) for i in PATH_IDS) + r")\"[^>]*/>",
        re.DOTALL,
    )
    text, removed_paths = path_pattern.subn("", text)

    effect_pattern = re.compile(
        r"<inkscape:path-effect\b[^>]*\bid=\"("
        + "|".join(re.escape(i) for i in EFFECT_IDS)
        + r")\"[^>]*/>",
        re.DOTALL,
    )
    text, removed_effects = effect_pattern.subn("", text)

    PANEL.write_text(text, encoding="utf-8")
    print(f"Removed {removed_paths} paths and {removed_effects} path-effects from {PANEL.name}")


if __name__ == "__main__":
    main()
