"""Borra en la placa VIVA (una sola llamada remove_items = un Ctrl+Z) las pistas/vías cuyos UUID lista un JSON
{"n_items": N, "uuids": [...]} (de islas.py o similar), si la placa no ha cambiado desde el volcado (mismo número de
pistas+vías). uso: borrar_vivo.py borrar.json"""
import json
import sys

from kipy import KiCad

sys.stdout.reconfigure(encoding="utf-8")
plan = json.load(open(sys.argv[1]))
b = KiCad().get_board()
items = list(b.get_tracks()) + list(b.get_vias())
if len(items) != plan["n_items"]:
    sys.exit(f"ABORTO: la placa tiene {len(items)} pistas+vías y el volcado {plan['n_items']} (¿la has tocado?)")
quiero = set(plan["uuids"])
sel = [i for i in items if i.id.value in quiero]
if len(sel) != len(quiero):
    sys.exit(f"ABORTO: encontrados {len(sel)} de {len(quiero)}")
# begin_commit de este kipy no lleva documento y KiCad lo rechaza con esquema y placa abiertos a la vez;
# una sola llamada remove_items (que sí lo lleva) entra como un único paso de deshacer.
b.remove_items(sel)
despues = list(b.get_tracks()) + list(b.get_vias())
quedan = [i for i in despues if i.id.value in quiero]
print(f"antes {len(items)} · borrados {len(sel)} · ahora {len(despues)} · de la lista siguen {len(quedan)}")
