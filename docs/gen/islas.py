"""Sólo lectura (copia volcada): islas de cobre (pistas+vías unidas, misma red) que no unen ≥ 2 pads y contienen algo
que el DRC de KiCad marca como track_dangling / via_dangling. uso: islas.py copia.kicad_pcb drc.json salida.json"""
import json
import sys

import pcbnew

sys.stdout.reconfigure(encoding="utf-8")
b = pcbnew.LoadBoard(sys.argv[1])
drc = json.load(open(sys.argv[2], encoding="utf-8"))
MM = 1e6
marcados = {i["uuid"] for v in drc["violations"] if v["type"] in ("track_dangling", "via_dangling") for i in v["items"]}
items = [t for t in b.GetTracks() if t.GetNetname() not in ("GND", "3V3")]
pads = [p for f in b.GetFootprints() for p in f.Pads()]
idx = {t.m_Uuid.AsString(): t for t in items}
padre = {k: k for k in idx}


def raiz(k):
    while padre[k] != k:
        padre[k] = padre[padre[k]]
        k = padre[k]
    return k


def puntos(t):
    return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]


def tol(t):
    return (t.GetWidth(pcbnew.F_Cu) if t.GetClass() == "PCB_VIA" else t.GetWidth()) // 2


def mismo_cobre(a, b_):
    if a.GetNetname() != b_.GetNetname():
        return False
    va, vb = a.GetClass() == "PCB_VIA", b_.GetClass() == "PCB_VIA"
    if not va and not vb and a.GetLayer() != b_.GetLayer():
        return False
    return any(b_.HitTest(p, tol(a)) for p in puntos(a)) or any(a.HitTest(p, tol(b_)) for p in puntos(b_))


por_red = {}
for t in items:
    por_red.setdefault(t.GetNetname(), []).append(t)
for red, ts in por_red.items():
    for i, a in enumerate(ts):
        for b_ in ts[i + 1:]:
            if mismo_cobre(a, b_):
                padre[raiz(a.m_Uuid.AsString())] = raiz(b_.m_Uuid.AsString())
islas = {}
for k in idx:
    islas.setdefault(raiz(k), []).append(k)
borrar = []
for r, ks in islas.items():
    if not set(ks) & marcados:
        continue
    toca = set()
    for k in ks:
        t = idx[k]
        for p in pads:
            if p.GetNetname() != t.GetNetname():
                continue
            capas = [pcbnew.F_Cu, pcbnew.B_Cu] if t.GetClass() == "PCB_VIA" else [t.GetLayer()]
            if any(p.IsOnLayer(c) for c in capas) and any(p.HitTest(q, tol(t)) for q in puntos(t)):
                toca.add(f"{p.GetParentFootprint().GetReference()}.{p.GetNumber()}")
    t0 = idx[ks[0]]
    q = puntos(t0)[0]
    print(f"isla {t0.GetNetname():16s} {len(ks):2d} elementos  pads {sorted(toca)}  cerca ({q.x/MM:.2f},{q.y/MM:.2f})",
          "→ BORRAR" if len(toca) < 2 else "→ se queda (une 2 pads)")
    if len(toca) < 2:
        borrar += ks
    else:
        # isla buena con una rama colgando: fuera lo marcado y, en bucle, lo que se quede con un extremo al aire
        fuera = set(ks) & marcados
        cambio = True
        while cambio:
            cambio = False
            vivos = [idx[k] for k in ks if k not in fuera]
            for t in vivos:
                if t.GetClass() == "PCB_VIA":
                    continue
                for q in puntos(t):
                    ok = any(p.GetNetname() == t.GetNetname() and p.IsOnLayer(t.GetLayer()) and p.HitTest(q, tol(t))
                             for p in pads)
                    ok = ok or any(o is not t and (o.GetClass() == "PCB_VIA" or o.GetLayer() == t.GetLayer())
                                   and o.HitTest(q, tol(t)) for o in vivos)
                    if not ok:
                        fuera.add(t.m_Uuid.AsString()); cambio = True
                        break
        print(f"   rama colgante recortada: {len(fuera)} elementos")
        borrar += sorted(fuera)
print("a borrar:", len(borrar), "· marcados por el DRC sin cubrir:", sorted(marcados - set(borrar) - {None}))
json.dump({"n_items": len(list(b.GetTracks())), "uuids": sorted(borrar)}, open(sys.argv[3], "w"))
