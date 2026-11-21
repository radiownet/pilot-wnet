# -*- coding: utf-8 -*-
"""Sonda footprintów: obrysy (courtyard, fab), skrajne pady, strefy w footprincie. Tylko odczyt."""
import os
import sys

import pcbnew

FP = os.environ.get("KICAD10_FOOTPRINT_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
TU = os.path.dirname(os.path.abspath(__file__))
mm = pcbnew.ToMM
for spec in sys.argv[1:]:
    lib, nazwa = spec.split(":")
    sciezka = os.path.join(TU, "lib", lib + ".pretty") if lib == "pilot_jlc" else os.path.join(FP, lib + ".pretty")
    f = pcbnew.FootprintLoad(sciezka, nazwa)
    if f is None:
        print(spec, "BRAK"); continue
    out = [spec]
    for warstwa in (pcbnew.F_CrtYd, pcbnew.F_Fab, pcbnew.Edge_Cuts):
        xs, ys = [], []
        for g in f.GraphicalItems():
            if g.GetLayer() == warstwa:
                bb = g.GetBoundingBox(); xs += [bb.GetLeft(), bb.GetRight()]; ys += [bb.GetTop(), bb.GetBottom()]
        if xs:
            out.append(f"{pcbnew.LayerName(warstwa)} x[{mm(min(xs)):.2f},{mm(max(xs)):.2f}] y[{mm(min(ys)):.2f},{mm(max(ys)):.2f}]")
    pads = list(f.Pads())
    out.append(f"pady={len(pads)} x[{mm(min(p.GetPosition().x for p in pads)):.2f},{mm(max(p.GetPosition().x for p in pads)):.2f}] y[{mm(min(p.GetPosition().y for p in pads)):.2f},{mm(max(p.GetPosition().y for p in pads)):.2f}] THT={sum(1 for p in pads if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH)}")
    strefy = list(f.Zones())
    for z in strefy:
        bb = z.GetBoundingBox()
        out.append(f"strefa '{z.GetZoneName()}' keepout={z.GetIsRuleArea()} x[{mm(bb.GetLeft()):.2f},{mm(bb.GetRight()):.2f}] y[{mm(bb.GetTop()):.2f},{mm(bb.GetBottom()):.2f}]")
    m = [x.m_Filename for x in f.Models()]
    out.append(f"modele={m}")
    print(" | ".join(out))
