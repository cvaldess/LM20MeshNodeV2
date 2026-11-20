"""Crea en la placa VIVA (una sola create_items = un Ctrl+Z) el área de regla UFL_J401 en F.Cu: el hueco entre las dos
patas GND del U.FL J401, sobre la pata SIG, donde Hirose (U.FL-R-SMT-1, «Recommended PCB Mounting Pattern») pide
«No conductive traces in this area». Sin relleno, pistas ni vías. Luego rellena zonas. Si ya existe no hace nada.
uso: keepout_ufl.py"""
import sys
import time

from kipy import KiCad
from kipy.board_types import Zone
from kipy.geometry import PolyLine, PolyLineNode, PolygonWithHoles, Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer, ZoneType
from kipy.util.units import from_mm

sys.stdout.reconfigure(encoding="utf-8")
NOM = "UFL_J401"
X0, Y0, X1, Y1 = 129.58, 105.535, 131.78, 107.425   # x = patas GND (2,2) · y = entre patas GND (1,9)
b = KiCad().get_board()
fp = next(f for f in b.get_footprints() if f.reference_field.text.value == "J401")
print("J401 en", round(fp.position.x / 1e6, 3), round(fp.position.y / 1e6, 3), "rot", fp.orientation.degrees)
assert (round(fp.position.x / 1e6, 2), round(fp.position.y / 1e6, 2), round(fp.orientation.degrees, 1)) == (129.92, 106.48, 0.0), \
    "J401 se ha movido: recalcular el rectángulo"
if NOM in {z.name for z in b.get_zones()}:
    print("ya existe:", NOM)
else:
    z = Zone()
    z.type = ZoneType.ZT_RULE_AREA
    z.layers = [BoardLayer.BL_F_Cu]
    z.name = NOM
    ra = z.proto.rule_area_settings
    ra.keepout_copper = True
    ra.keepout_tracks = True
    ra.keepout_vias = True
    ra.keepout_pads = False
    ra.keepout_footprints = False
    lin = PolyLine()
    for x, y in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)):
        lin.append(PolyLineNode.from_point(Vector2.from_xy(from_mm(x), from_mm(y))))
    pol = PolygonWithHoles()
    pol.outline = lin
    z.outline = pol
    b.create_items([z])
    print("creada:", NOM)
b.refill_zones()
for _ in range(60):
    try:
        z = next(z for z in b.get_zones() if z.name == NOM)
        break
    except Exception as e:
        if "busy" not in str(e):
            raise
        time.sleep(1)
ra = z.proto.rule_area_settings
bb = z.outline.bounding_box()
print(z.name, list(z.layers), "relleno no" if ra.keepout_copper else "relleno sí", "· pistas no" if ra.keepout_tracks else "",
      "· vías no" if ra.keepout_vias else "", "· caja", [round(v / 1e6, 3) for v in (bb.pos.x, bb.pos.y, bb.pos.x + bb.size.x, bb.pos.y + bb.size.y)])
