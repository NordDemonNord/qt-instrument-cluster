"""Extract readable strings from PDF (no deps)."""
import re
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
# PDF literal strings in parentheses
strings = re.findall(rb"\(([^()\\]*(?:\\.[^()\\]*)*)\)", data)
text = b"\n".join(strings).decode("latin-1", errors="replace")
# also try UTF-16BE streams
for m in re.finditer(rb"<([0-9A-Fa-f]+)>", data):
    hexs = m.group(1)
    if len(hexs) % 4 == 0 and len(hexs) > 20:
        try:
            text += "\n" + bytes.fromhex(hexs.decode()).decode("utf-16-be", errors="ignore")
        except Exception:
            pass

keywords = ["3.3.1", "Комбинация", "прибор", "оборот", "скорост", "температур", "одометр"]
lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
out = []
for i, ln in enumerate(lines):
    low = ln.lower()
    if any(k.lower() in low for k in keywords) or re.match(r"^\d{1,2}\.", ln):
        out.append(ln)
Path(sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] + ".txt").write_text("\n".join(out), encoding="utf-8")
print(f"Wrote {len(out)} lines")
