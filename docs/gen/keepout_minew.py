"""Crea en la placa VIVA (una sola create_items = un Ctrl+Z) dos áreas de regla en F.Cu bajo los módulos Minew, entre
sus filas/columnas de pads: «no wires at the bottom of the module» (MS21SF1 §8, ME31GR02 §5.2). Prohíben pistas;
permiten vías (las GND que pone él), rellenos y pads. dsn_mesh.py les añade «sin vías» en la copia para Freerouting.
Si ya existen (mismo nombre) no hace nada. uso: keepout_minew.py"""
import sys

from kipy import KiCad
from kipy.board_types import Zone
from kipy.geometry import PolyLine, PolyLineNode, PolygonWithHoles, Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer, ZoneType
from kipy.util.units import from_mm

sys.stdout.reconfigure(encoding="utf-8")
AREAS = {  # nombre: (x0, y0, x1, y1) mm
    "MINEW_U301": (114.30, 80.14, 130.30, 92.34),   # MS21SF1: entre las filas de pads (y 79,94 / 92,54), cuerpo ±0,5 en x
    "MINEW_U401": (116.90, 97.34, 124.20, 108.84),  # ME31GR02: entre las columnas (x 116,7 / 124,4), cuerpo ±0,5 en y
}
b = KiCad().get_board()
ya = {z.name for z in b.get_zones()}
nuevas = []
for nom, (x0, y0, x1, y1) in AREAS.items():
    if nom in ya:
        print("ya existe:", nom)
        continue
    z = Zone()
    z.type = ZoneType.ZT_RULE_AREA
    z.layers = [BoardLayer.BL_F_Cu]
    z.name = nom
    ra = z.proto.rule_area_settings
    ra.keepout_tracks = True
    ra.keepout_vias = False
    ra.keepout_copper = False
    ra.keepout_pads = False
    ra.keepout_footprints = False
    lin = PolyLine()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        lin.append(PolyLineNode.from_point(Vector2.from_xy(from_mm(x), from_mm(y))))
    pol = PolygonWithHoles()
    pol.outline = lin
    z.outline = pol
    nuevas.append(z)
if nuevas:
    b.create_items(nuevas)
for z in b.get_zones():
    if z.name.startswith("MINEW_"):
        ra = z.proto.rule_area_settings
        bb = z.outline.bounding_box()
        print(z.name, list(z.layers), "pistas no" if ra.keepout_tracks else "pistas sí", "· vías no" if ra.keepout_vias else "· vías sí",
              "· relleno no" if ra.keepout_copper else "· relleno sí",
              "· caja", [round(v / 1e6, 3) for v in (bb.pos.x, bb.pos.y, bb.pos.x + bb.size.x, bb.pos.y + bb.size.y)])
