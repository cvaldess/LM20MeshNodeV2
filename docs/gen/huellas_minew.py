"""Footprints for the MinewSemi modules of rev 0.2 (MS21SF1 LoRa, ME31GR02 GNSS) into libs/meshnode.pretty.

Pads come from the vendor CAD sent by Minew on 20-11-2026 (folder minewsemi/ of the repo root, not redistributed);
body, silkscreen and courtyard are redrawn from the datasheets in the same style as the other project footprints.
Run with KiCad's python:
    python huellas_minew.py                      -> write both footprints (text, then a load/save round trip)
    python huellas_minew.py --check <MS21SF1 dir with MS21SF1_V1.0.kicad_mod> <Minew-GNSS.PcbLib>
                                                 -> also compare every pad with the vendor footprints (0.01 mm)

MS21SF1  datasheet K p.6-7: 15.00 x 16.40 x 3.00, 16 stamp holes pitch 1.8, first centre 1.9 from the top edge,
         module pad 1.0 wide x 1.2 deep. Vendor land 2.0 x 1.0 at x = +-7.3 (0.8 outside the body), mask +0.05.
         U.FL on the module top (from the vendor STEP) next to pad 16 ANT.
ME31GR02 datasheet p.8-10: 9.7 (9.5-9.9) x 10.5 (10.0-10.8) x 2.0, LCC-18 pitch 1.1. Minew: same land pattern as
         their MS31SN1 = footprint "1010-LCC-18PIN" of Minew-GNSS.PcbLib: 1.8 x 0.8 (corner pads 0.7) at x = +-4.75.
         The vendor pad has paste margin -2 mm and separate paste/mask primitives that KiCad's Altium importer loses
         (zero-size shapes) => here paste = pad (stencil 0.15 recommended by Minew; this board uses 0.10).
         Datasheet "TOP VIEW" numbers pins counter-clockwise from pin 1 bottom-right = this footprint turned 180 deg.
"""
import os
import sys
import uuid

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.normpath(os.path.join(HERE, "..", "..", "libs", "meshnode.pretty"))
MODELS = "${KIPRJMOD}/libs/meshnode.3dshapes/"

SILK, FAB, CRT = 0.12, 0.10, 0.05


def u():
    return str(uuid.uuid4())


def stroke(w):
    return f'(stroke (width {w}) (type solid))'


def line(x1, y1, x2, y2, layer, w):
    return f'(fp_line (start {x1:g} {y1:g}) (end {x2:g} {y2:g}) {stroke(w)} (layer "{layer}") (uuid "{u()}"))'


def text(kind, val, x, y, layer, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'(property "{kind}" "{val}" (at {x:g} {y:g} 0) (layer "{layer}"){h} (uuid "{u()}") '
            f'(effects (font (size 1 1) (thickness 0.15))))')


def pad(num, x, y, sx, sy, mask=None):
    m = f" (solder_mask_margin {mask:g})" if mask is not None else ""
    return (f'(pad "{num}" smd rect (at {x:g} {y:g}) (size {sx:g} {sy:g}) (layers "F.Cu" "F.Mask" "F.Paste"){m} '
            f'(uuid "{u()}"))')


def footprint(name, descr, keywords, body_w, body_h, pads, crt, silk, extra, model, ref_y, val_y):
    """body centred on the origin, pin 1 top-left; fab outline with a 1 mm chamfer at the pin-1 corner."""
    hw, hh = body_w / 2, body_h / 2
    c = 1.0
    fab = (f'(fp_poly (pts (xy {-hw + c:g} {-hh:g}) (xy {hw:g} {-hh:g}) (xy {hw:g} {hh:g}) (xy {-hw:g} {hh:g}) '
           f'(xy {-hw:g} {-hh + c:g})) {stroke(FAB)} (fill no) (layer "F.Fab") (uuid "{u()}"))')
    cx, cy = crt
    court = (f'(fp_rect (start {-cx:g} {-cy:g}) (end {cx:g} {cy:g}) {stroke(CRT)} (fill no) (layer "F.CrtYd") '
             f'(uuid "{u()}"))')
    mfile, (ox, oy, oz), (rx, ry, rz) = model
    parts = [
        f'(footprint "{name}" (version 20260206) (generator "pcbnew") (generator_version "10.0") (layer "F.Cu")',
        f'(descr "{descr}")', f'(tags "{keywords}")',
        text("Reference", "REF**", 0, ref_y, "F.SilkS"), text("Value", name, 0, val_y, "F.Fab"),
        text("Datasheet", "", 0, 0, "F.Fab", True), text("Description", "", 0, 0, "F.Fab", True),
        '(attr smd)', fab, court, *silk, *extra, *pads,
        f'(model "{MODELS}{mfile}" (offset (xyz {ox:g} {oy:g} {oz:g})) (scale (xyz 1 1 1)) '
        f'(rotate (xyz {rx:g} {ry:g} {rz:g})))',
        ')']
    return "\n".join(parts) + "\n"


def silk_box(hw, hh, side_to, dot_x, dot_y):
    """top/bottom lines 0.11 outside the body, short side stubs down/up to side_to, pin-1 dot."""
    s = 0.11
    x, y = hw + s, hh + s
    out = [line(-x, -y, x, -y, "F.SilkS", SILK), line(-x, y, x, y, "F.SilkS", SILK)]
    if side_to is not None and side_to < y:
        for sx in (-x, x):
            out += [line(sx, -y, sx, -side_to, "F.SilkS", SILK), line(sx, y, sx, side_to, "F.SilkS", SILK)]
    out.append(f'(fp_circle (center {dot_x:g} {dot_y:g}) (end {dot_x + 0.15:g} {dot_y:g}) {stroke(0.1)} (fill yes) '
               f'(layer "F.SilkS") (uuid "{u()}"))')
    return out


def ms21sf1():
    ys = [round(-6.3 + 1.8 * k, 3) for k in range(8)]
    pads = [(n + 1, -7.3, ys[n], 2.0, 1.0) for n in range(8)]
    pads += [(9 + n, 7.3, ys[7 - n], 2.0, 1.0) for n in range(8)]
    # pads 1/16 end at y -6.8: silk side stubs stop 0.2 + half width before them
    silk = silk_box(7.5, 8.2, 6.8 + 0.2 + SILK / 2, -8.75, -6.3)
    # U.FL footprint on the module top, taken from the vendor STEP (x 10.49-13.49, y 11.70-14.75 from the
    # bottom-left corner) -> centre (+4.49, -5.02) here
    ufl = [line(2.99, -6.55, 5.99, -6.55, "F.Fab", FAB), line(5.99, -6.55, 5.99, -3.50, "F.Fab", FAB),
           line(5.99, -3.50, 2.99, -3.50, "F.Fab", FAB), line(2.99, -3.50, 2.99, -6.55, "F.Fab", FAB),
           f'(fp_text user "U.FL" (at 4.49 -2.6 0) (layer "F.Fab") (uuid "{u()}") '
           f'(effects (font (size 0.6 0.6) (thickness 0.09))))']
    fp = footprint(
        "MS21SF1",
        "MinewSemi MS21SF1 SX1262 LoRa module 15.0x16.4x3.0 mm, 16 stamp holes pitch 1.8, U.FL on top "
        "(pads from Minew MS21SF1_V1.0.kicad_mod; module rev V1.1: pins 2/3/14 NC)",
        "LoRa SX1262 Minew MS21SF1 module",
        15.0, 16.4, [pad(*p, mask=0.05) for p in pads], (8.55, 8.55), silk, ufl,
        # vendor STEP: corner at the origin, PCB z -1.04..0 -> lift 1.04 so the module sits on the board
        ("MS21SF1_PCB_V1.0.step", (-7.5, -8.2, 1.04), (0, 0, 0)), -9.4, 9.4)
    return fp, pads


def me31gr02():
    ys = [round(-4.4 + 1.1 * k, 3) for k in range(9)]
    h = lambda k: 0.7 if k in (0, 8) else 0.8
    pads = [(n + 1, -4.75, ys[n], 1.8, h(n)) for n in range(9)]
    pads += [(10 + n, 4.75, ys[8 - n], 1.8, h(8 - n)) for n in range(9)]
    silk = silk_box(4.85, 5.25, None, -6.1, -4.4)
    fp = footprint(
        "ME31GR02",
        "MinewSemi ME31GR02 GNSS module 9.7x10.5x2.0 mm, LCC-18 pitch 1.1 "
        "(pads from Minew-GNSS.PcbLib 1010-LCC-18PIN, shared with MS31SN1)",
        "GNSS GPS Minew ME31GR02 LCC-18 module",
        9.7, 10.5, [pad(*p) for p in pads], (5.9, 5.65), silk, [],
        # vendor STEP (generic 9.7x10.1x2.7 "GNSS_MODULE_1010") is Y-up: KiCad rotate x = -90 stands it on the
        # board (x = +90 sinks it 2.7 mm into the board); checked on a STEP export of a test board
        ("GNSS_MODULE_1010.step", (0, 0, 0), (-90, 0, 0)), -6.6, 6.6)
    return fp, pads


def check(pads, lib, name):
    fp = pcbnew.FootprintLoad(lib, name)
    vend = {}
    for p in fp.Pads():
        q, s = p.GetPosition(), p.GetSize(pcbnew.F_Cu)
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        if round(p.GetOrientationDegrees()) % 180 == 90:
            sx, sy = sy, sx
        vend[str(p.GetNumber())] = (pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), sx, sy)
    bad = 0
    for n, x, y, sx, sy in pads:
        v = vend.pop(str(n), None)
        if v is None or max(abs(a - b) for a, b in zip((x, y, sx, sy), v)) > 0.01:
            bad += 1
            print(f"   MISMATCH pad {n}: ours {(x, y, sx, sy)} vendor {v}")
    if vend:
        bad += len(vend)
        print("   vendor pads not in ours:", sorted(vend))
    print(f"   {name}: {len(pads)} pads, {bad} mismatches")
    return bad


def main():
    io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    built = {}
    for name, fn in (("MS21SF1", ms21sf1), ("ME31GR02", me31gr02)):
        txt, pads = fn()
        path = os.path.join(DST, name + ".kicad_mod")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        fp = pcbnew.FootprintLoad(DST, name)       # round trip = parse check + KiCad's own formatting
        n = len(fp.Pads())
        io.FootprintSave(DST, fp)                  # fp is invalid after this line
        print("saved", name, n, "pads")
        built[name] = pads
    if len(sys.argv) == 4 and sys.argv[1] == "--check":
        bad = check(built["MS21SF1"], sys.argv[2], "MS21SF1_V1.0")
        bad += check(built["ME31GR02"], sys.argv[3], "1010-LCC-18PIN")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
