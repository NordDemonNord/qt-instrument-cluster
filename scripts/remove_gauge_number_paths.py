#!/usr/bin/env python3
"""Remove drawn gauge scale number paths from panel.svg."""
import re
from pathlib import Path

PANEL = Path(__file__).resolve().parents[1] / "assets" / "panel.svg"
IDS = {
    "path117", "path121",
    "path122", "path123", "path124", "path125",
    "path175", "path176", "path177", "path178", "path179", "path180", "path181",
    "path182", "path183", "path185", "path186", "path187",
}

text = PANEL.read_text(encoding="utf-8")
pattern = re.compile(
    r"<path\b[^>]*\bid=\"(" + "|".join(re.escape(i) for i in IDS) + r")\"[^>]*/>",
    re.DOTALL,
)
new_text, count = pattern.subn("", text)
PANEL.write_text(new_text, encoding="utf-8")
print(f"Removed {count} path elements from {PANEL.name}")
