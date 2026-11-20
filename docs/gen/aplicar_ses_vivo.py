"""Crea en la placa ABIERTA (kipy, un commit = un Ctrl+Z) los tramos y vías que ses_mesh.py añadió a la copia
(su JSON), sin bloquear, y rellena las zonas. Antes comprueba que la placa viva tiene las mismas pistas que la copia
de la que salió el DSN (si él tocó algo entre medias, se niega).
Uso: python aplicar_ses_vivo.py nuevas.json n_tramos_base n_vias_base [--apply]"""
import json
import sys

from kipy import KiCad
from kipy.board_types import Track, Via
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer

CAPA = {"F.Cu": BoardLayer.BL_F_Cu, "B.Cu": BoardLayer.BL_B_Cu}
items = json.load(open(sys.argv[1], encoding="utf-8"))
n_t0, n_v0 = int(sys.argv[2]), int(sys.argv[3])
b = KiCad().get_board()
nt, nv = len(list(b.get_tracks())), len(list(b.get_vias()))
print(f"placa viva: {nt} tramos, {nv} vías (base del DSN: {n_t0}, {n_v0}) · a crear: "
      f"{sum(i['t'] == 'tramo' for i in items)} tramos, {sum(i['t'] == 'via' for i in items)} vías")
assert (nt, nv) == (n_t0, n_v0), "la placa ha cambiado desde el DSN: no aplico"
if "--apply" not in sys.argv:
    print("(simulacro)")
    sys.exit()
nets = {n.name: n for n in b.get_nets()}
nuevas = []
for i in items:
    if i["t"] == "via":
        v = Via()
        v.position = Vector2.from_xy(*i["c"])
        v.diameter = i["d"]
        v.drill_diameter = i["taladro"]
        v.net = nets[i["red"]]
        nuevas.append(v)
    else:
        t = Track()
        t.start = Vector2.from_xy(*i["a"])
        t.end = Vector2.from_xy(*i["b"])
        t.width = i["w"]
        t.layer = CAPA[i["capa"]]
        t.net = nets[i["red"]]
        nuevas.append(t)
# 20-11-2026: con esquema Y placa abiertos, KiCad rechaza BeginCommit sin documento («not allowed when multiple
# editors are open») y el kipy instalado no deja indicarlo ⇒ una sola llamada create_items (también = un Ctrl+Z).
try:
    c = b.begin_commit()
except Exception as e:
    print("sin commit (", str(e)[:80], ") ⇒ una sola llamada create_items")
    c = None
if c is None:
    b.create_items(nuevas)
else:
    try:
        b.create_items(nuevas)
    except Exception:
        b.drop_commit(c)
        raise
    b.push_commit(c, "Ruteo de Freerouting (ses_mesh.py + aplicar_ses_vivo.py)")
b.refill_zones()
# el relleno sigue en curso y KiCad responde «busy» un rato (20-11-2026): reintentar el recuento
import time  # noqa: E402
for _ in range(60):
    try:
        print("en vivo:", len(nuevas), "objetos creados · ahora", len(list(b.get_tracks())), "tramos,",
              len(list(b.get_vias())), "vías")
        break
    except Exception as e:
        if "busy" not in str(e):
            raise
        time.sleep(1)
