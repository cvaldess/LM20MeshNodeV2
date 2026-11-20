"""Read-only: list top-level items of a .kicad_sch (type, uuid, position, ref/text)."""
import json
import re
import sys

BS = chr(92)
src = open(sys.argv[1], encoding="utf-8").read()
items, depth, i, start = [], 0, 0, None
while i < len(src):
    c = src[i]
    if c == '"':
        j = i + 1
        while src[j] != '"':
            j += 2 if src[j] == BS else 1
        i = j + 1
        continue
    if c == '(':
        depth += 1
        if depth == 2:
            start = i
    elif c == ')':
        if depth == 2:
            items.append(src[start:i + 1])
        depth -= 1
    i += 1
SKIP = ("version", "generator", "generator_version", "uuid", "paper", "title_block", "lib_symbols",
        "sheet_instances", "embedded_fonts")
out = []
for it in items:
    typ = re.match(r'\((\w+)', it).group(1)
    if typ in SKIP:
        continue
    u = re.findall(r'\(uuid "([0-9a-f-]+)"\)', it)
    at = re.search(r'\(at ([-\d.]+) ([-\d.]+)', it) or re.search(r'\(xy ([-\d.]+) ([-\d.]+)', it)
    name = re.match(r'\(\w+ "([^"]*)"', it)
    ref = re.search(r'\(property "Reference" "([^"]*)"', it)
    # a symbol's own uuid is the first top-level (uuid ...) after lib_id; pins carry their own uuids later
    own = re.search(r'\n\t\t\(uuid "([0-9a-f-]+)"\)', it)
    out.append({"type": typ, "uuid": own.group(1) if own else (u[0] if u else None),
                "at": [float(at.group(1)), float(at.group(2))] if at else None,
                "name": ref.group(1) if ref else (name.group(1) if name else "")})
json.dump(out, sys.stdout, ensure_ascii=False)
