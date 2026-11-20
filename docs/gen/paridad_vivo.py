"""Solo lectura: huellas de la placa VIVA (kipy) frente al netlist del esquema: sobrantes, faltantes, huella distinta y
referencias repetidas. uso: paridad_vivo.py netlist.net  (kicad-cli sch export netlist --format kicadsexpr ...)"""
import re
import sys

from kipy import KiCad

sys.stdout.reconfigure(encoding="utf-8")
net = open(sys.argv[1], encoding="utf-8").read()
sch = {}
for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)\s+\(value "[^"]*"\)\s+\(footprint "([^"]*)"\)', net):
    sch[m.group(1)] = m.group(2)
board = KiCad().get_board()
live, dup = {}, []
for fp in board.get_footprints():
    lib = fp.definition.id
    r = fp.reference_field.text.value
    if r in live:
        dup.append((r, live[r], f"{lib.library}:{lib.name}", round(fp.position.x / 1e6, 2), round(fp.position.y / 1e6, 2)))
    live[r] = f"{lib.library}:{lib.name}"
print("referencias repetidas en la placa:", dup)
print("símbolos con huella en el esquema:", len(sch), "· huellas en la placa:", len(live))
print("en la placa SIN símbolo:", sorted(set(live) - set(sch)))
print("en el esquema SIN huella en la placa:", sorted(set(sch) - set(live)))
for r in sorted(set(sch) & set(live)):
    if sch[r] != live[r]:
        print("huella distinta", r, "placa:", live[r], "→ esquema:", sch[r])
