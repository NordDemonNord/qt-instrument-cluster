"""Decompress PDF streams and search for Russian dashboard text."""
import re
import sys
import zlib
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
out_path = Path(sys.argv[2])
chunks = []

# FlateDecode streams
for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
    raw = m.group(1)
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
        try:
            dec = zlib.decompress(raw, wbits)
            chunks.append(dec)
            break
        except Exception:
            continue

blob = b"\n".join(chunks)
# UTF-16BE in hex
text_parts = []
for m in re.finditer(rb"<([0-9A-Fa-f]{8,})>", blob):
    hexs = m.group(1)
    if len(hexs) % 4 == 0:
        try:
            text_parts.append(bytes.fromhex(hexs.decode()).decode("utf-16-be"))
        except Exception:
            pass
# literal strings
for m in re.finditer(rb"\(([^()\\]{2,200})\)", blob):
    try:
        text_parts.append(m.group(1).decode("utf-8"))
    except Exception:
        try:
            text_parts.append(m.group(1).decode("latin-1"))
        except Exception:
            pass

text = "\n".join(text_parts)
# find section around 3.3.1
idx = text.find("3.3.1")
if idx >= 0:
    snippet = text[max(0, idx - 500) : idx + 8000]
else:
    snippet = text

keywords = ["Комбинация", "прибор", "оборот", "скорост", "температур", "одометр", "суточ", "топлив", "круиз", "передач"]
lines = []
for ln in snippet.splitlines():
    ln = ln.strip()
    if not ln:
        continue
    if any(k in ln for k in keywords) or re.search(r"\b([1-9]|[1-3][0-9]|4[01])\b", ln):
        lines.append(ln)

out_path.write_text("\n".join(lines[:200]), encoding="utf-8")
print(f"chunks={len(chunks)} lines={len(lines)} idx3.3.1={idx}")
