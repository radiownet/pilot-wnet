# -*- coding: utf-8 -*-
"""Opis płytki Pilota Wnet, druga poprawka — pakiet v0.1, 20.11.2026 (Python KiCada 10).

    python opis2_v01.py kontrola <plik.kicad_pcb> <raport.json>   (tylko odczyt; kod wyjścia 1, gdy są błędy)
    python opis2_v01.py popraw   <plik.kicad_pcb> <raport.json>   (zapis płytki tylko wtedy, gdy po poprawce 0 błędów)

Powód: przegląd renderów 19.11 wykazał, że `opis_v01.py` szukał wolnego miejsca po prostokątach KiCada i bez korpusów
elementów: oznaczenie Y1 trafiło pod W5500 (U4), H1 leżało poza płytką, a napis „SERW” (złącze serwisowe J20) stał
przy J19 — obie listwy 1×6 mają różny układ zasilania. DRC KiCada nic z tego nie zgłasza (min_silk_clearance = 0).

Wszystkie pomiary na kształcie tuszu (GetEffectiveTextShape — kreski z grubością, jak w Gerberze), nie na prostokącie
napisu (ten jest 0,15–0,32 mm większy). Dla każdego widocznego napisu opisu (pola footprintów, napisy płytki) na F/B:
  BŁĘDY  pod_korpusem — tusz nachodzi na korpus elementu tej strony (prostokąt kształtów Fab; bez Fab — courtyard;
                        otwór montażowy — koło 3,5 mm od środka: podkładka M3 DIN 125 / tulejka), także własnego i DNP;
         krawedz      — tusz poza płytką albo bliżej krawędzi niż 0,3 mm;
         pad          — tusz bliżej otwarcia maski niż 0,15 mm;
         opis         — tusz bliżej innego opisu (napisy, linie, znaczniki pinu 1) niż 0,15 mm;
         niejednoznaczne — napis z właścicielem (pole Reference albo etykieta funkcji z WLASCICIELE) leży bliżej
                        obrysu (courtyard) lub padu konkurenta niż obrysu własnego; konkurent = element z tym samym
                        prefiksem (U, J, SW…), a dla etykiet funkcji także właściciel innej etykiety funkcji (np. SERW:
                        J19 i SW2). Pady liczą się osobno, bo courtyard modułu U6 (E22) nie obejmuje jego padów.
  INFO   przelotki pod tuszem (pierścień; zakryte maską) i otwory przelotek pod tuszem, < 0,5 mm od krawędzi, sam
         courtyard, najbliższy korpus (Fab) cudzy zamiast własnego.
Poprawka przesuwa tylko napisy z błędami: gdy błąd dotyczy samego odstępu (pad, opis), szuka najmniejszego przesunięcia
od obecnego miejsca (krok 0,05 mm); w pozostałych przypadkach — najbliższego miejsca przy korpusie właściciela (krok
0,25 mm, ten sam obrót, w razie braku miejsca także drugi obrót, a na końcu czcionka 0,8 mm = min_text_height,
z tą samą grubością kreski).
Warunki twarde nowego miejsca: krawędź ≥ 0,5 mm, korpusy ≥ 0,15 mm, pady ≥ 0,2 mm, linie opisu ≥ 0,2 mm, inne
napisy ≥ 0,4 mm, otwory przelotek ≥ 0,05 mm, jednoznaczność (własny obrys co najmniej 0,75 mm bliżej niż obrys i pady
każdego konkurenta). Kary w ocenie: pierścień przelotki pod tuszem, a przy przenoszeniu do właściciela także korpus obcego
elementu bliżej niż własny (napis ma stać przy swoim elemencie, nie przy sąsiednim kondensatorze); w trybie odstępu
liczy się tylko najmniejsze przesunięcie. Bez usuwania elementów: tylko położenie (wyjątkowo obrót i rozmiar) pól i napisów.
"""
import json
import math
import re
import sys

import pcbnew

MM = pcbnew.FromMM
B_KRAWEDZ, B_PAD, B_OPIS = 0.3, 0.15, 0.15          # progi błędów (mm)
N_KRAWEDZ, N_KORPUS, N_PAD, N_OPIS, N_NAPIS = 0.5, 0.15, 0.2, 0.2, 0.4   # warunki dla nowego miejsca (mm)
JEDNOZNACZNOSC = 0.75                                # nowe miejsce: własny obrys co najmniej tyle bliżej niż obrys konkurenta
R_OTWOR = 3.5                                        # korpus otworu montażowego: podkładka M3 DIN 125 (Ø7 mm)
PAS = 1.5                                            # pas szukania za pierwszym wolnym miejscem (mm)
# etykiety funkcji z plytka.py (wiersze 285–291) → element, który opisują; JOY (wiersz 288, bez refa) → J16 z netów
# IN_JOY_UP/DOWN/LEFT/RIGHT
WLASCICIELE = {"REC": "J10", "PLAY": "J11", "WYSLIJ": "J12", "SPRAWDZ": "J13", "START": "J14", "STOP": "J15",
               "JOY": "J16", "OLED": "J17", "QWIIC": "J18", "EXP": "J19", "SERW": "J20", "RST": "SW1", "BOOT": "SW2"}


def mm(v):
    return pcbnew.ToMM(v)


def bb_mm(bb):
    return (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))


def prefiks(ref):
    m = re.match(r"[A-Za-z]+", ref or "")
    return m.group(0) if m else ""


def odl(a, b, maks=1.0):
    """Odległość kształtów (mm): górna granica bisekcji po Collide (dokładność ok. 0,01 mm — KiCad przybliża łuki),
    obcięta do `maks`; 0 = nachodzą."""
    if a.Collide(b, 0):
        return 0.0
    if not a.Collide(b, MM(maks)):
        return maks
    lo, hi = 0.0, maks
    while hi - lo > 0.005:
        s = (lo + hi) / 2
        if a.Collide(b, MM(s)):
            hi = s
        else:
            lo = s
    return round(hi, 3)


def _odl_pkt_odc(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    u = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - u * dx, py - ay - u * dy)


def _w_wielokacie(x, y, pk):
    w = False
    for i in range(len(pk)):
        (x1, y1), (x2, y2) = pk[i], pk[(i + 1) % len(pk)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            w = not w
    return w


def do_krawedzi(bb, pk):
    """Odległość prostokąta tuszu od brzegu płytki (wielokąt pk, mm); 0, gdy prostokąt nie leży cały w płytce."""
    rogi = ((bb[0], bb[1]), (bb[2], bb[1]), (bb[2], bb[3]), (bb[0], bb[3]))
    if not all(_w_wielokacie(x, y, pk) for x, y in rogi):
        return 0.0
    if any(bb[0] < x < bb[2] and bb[1] < y < bb[3] for x, y in pk):
        return 0.0
    d = min(_odl_pkt_odc(x, y, *pk[i], *pk[(i + 1) % len(pk)]) for x, y in rogi for i in range(len(pk)))
    d2 = min(_odl_pkt_odc(x, y, *rogi[j], *rogi[(j + 1) % 4]) for x, y in pk for j in range(4))
    return round(min(d, d2), 3)


def blisko(bb1, bb2, m):
    return not (bb1[2] + m < bb2[0] or bb2[2] + m < bb1[0] or bb1[3] + m < bb2[1] or bb2[3] + m < bb1[1])


def prost(r):
    return pcbnew.SHAPE_RECT(pcbnew.VECTOR2I(MM(r[0]), MM(r[1])), MM(r[2] - r[0]), MM(r[3] - r[1]))


def czy_dnp(f):
    try:
        return bool(f.IsDNP())
    except Exception:
        return False


def otwor(f):
    return "MountingHole" in f.GetFPIDAsString()


class Plytka:
    def __init__(self, b):
        self.b = b
        self.fps = {f.GetReference(): f for f in b.GetFootprints()}
        self.obrys = pcbnew.SHAPE_POLY_SET()
        b.GetBoardPolygonOutlines(self.obrys, True)
        if self.obrys.OutlineCount() != 1 or self.obrys.HoleCount(0):
            raise SystemExit("BŁĄD: obrys płytki nie jest jednym wielokątem bez otworów")
        lc = self.obrys.Outline(0)
        self.brzeg = [(mm(lc.CPoint(i).x), mm(lc.CPoint(i).y)) for i in range(lc.PointCount())]
        wiasy = [v for v in b.GetTracks() if v.GetClass() == "PCB_VIA"]
        self.przelotki = [(v.GetEffectiveShape(pcbnew.F_Cu), bb_mm(v.GetBoundingBox())) for v in wiasy]
        self.otwory = []
        for v in wiasy:
            r = mm(v.GetDrillValue()) / 2
            x, y = mm(v.GetPosition().x), mm(v.GetPosition().y)
            self.otwory.append((pcbnew.SHAPE_CIRCLE(v.GetPosition(), v.GetDrillValue() // 2), (x - r, y - r, x + r, y + r)))
        self.korpus, self.crt, self.pady, self.linie = {"F": [], "B": []}, {"F": [], "B": []}, {"F": [], "B": []}, {"F": [], "B": []}
        for f in b.GetFootprints():
            ref, s0 = f.GetReference(), ("F" if f.GetLayer() == pcbnew.F_Cu else "B")
            fab, cy = (pcbnew.F_Fab, pcbnew.F_CrtYd) if s0 == "F" else (pcbnew.B_Fab, pcbnew.B_CrtYd)
            xs = [bb_mm(it.GetBoundingBox()) for it in f.GraphicalItems() if it.GetLayer() == fab and it.GetClass() == "PCB_SHAPE"]
            try:
                f.BuildCourtyardCaches()
            except Exception:
                pass
            for s, w in (("F", pcbnew.F_CrtYd), ("B", pcbnew.B_CrtYd)):
                ps = f.GetCourtyard(w)
                if ps.OutlineCount():
                    self.crt[s].append((ref, ps, bb_mm(ps.BBox())))
            if otwor(f):
                for s in ("F", "B"):
                    self.korpus[s].append((ref, False, pcbnew.SHAPE_CIRCLE(f.GetPosition(), MM(R_OTWOR)),
                                           (mm(f.GetPosition().x) - R_OTWOR, mm(f.GetPosition().y) - R_OTWOR,
                                            mm(f.GetPosition().x) + R_OTWOR, mm(f.GetPosition().y) + R_OTWOR)))
            elif xs:
                r = (min(x[0] for x in xs), min(x[1] for x in xs), max(x[2] for x in xs), max(x[3] for x in xs))
                self.korpus[s0].append((ref, czy_dnp(f), prost(r), r))
            else:
                ps = f.GetCourtyard(cy)
                if not ps.OutlineCount():
                    raise SystemExit("BŁĄD: %s bez Fab i bez courtyardu — nie wiem, gdzie jest korpus" % ref)
                self.korpus[s0].append((ref, czy_dnp(f), ps, bb_mm(ps.BBox())))
            for pad in f.Pads():
                for s, cu, mk in (("F", pcbnew.F_Cu, pcbnew.F_Mask), ("B", pcbnew.B_Cu, pcbnew.B_Mask)):
                    if pad.IsOnLayer(mk):
                        self.pady[s].append((ref + "." + pad.GetNumber(), pad.GetEffectiveShape(cu), bb_mm(pad.GetBoundingBox())))
            for it in f.GraphicalItems():
                for s, sl in (("F", pcbnew.F_SilkS), ("B", pcbnew.B_SilkS)):
                    if it.GetLayer() == sl and it.GetClass() == "PCB_SHAPE":
                        self.linie[s].append((ref + ":linia", it.GetEffectiveShape(sl), bb_mm(it.GetBoundingBox())))
        for d in b.GetDrawings():
            for s, sl in (("F", pcbnew.F_SilkS), ("B", pcbnew.B_SilkS)):
                if d.GetLayer() == sl and d.GetClass() == "PCB_SHAPE":
                    self.linie[s].append(("plytka:linia", d.GetEffectiveShape(sl), bb_mm(d.GetBoundingBox())))

    def d_konkurenta(self, sh, bb, kk, s, maks=20.0):
        """Najmniejsza odległość tuszu od courtyardu albo padu któregoś z elementów `kk` na stronie `s`: (mm, ref)."""
        w = [(odl(sh, ps, maks), r) for r, ps, pb in self.crt[s] if r in kk and blisko(bb, pb, maks)]
        w += [(odl(sh, ps, maks), n.split(".")[0]) for n, ps, pb in self.pady[s] if n.split(".")[0] in kk and blisko(bb, pb, maks)]
        d = min(w) if w else (None, None)
        return (None, None) if d[0] is not None and d[0] >= maks else d

    def konkurenci(self, wl, etykieta):
        """Elementy, z którymi napis właściciela `wl` nie może być mylony."""
        pf = prefiks(wl)
        wl_etyk = set(WLASCICIELE.values())
        return {r for s in ("F", "B") for r, ps, pb in self.crt[s]
                if r != wl and (prefiks(r) == pf or (etykieta and r in wl_etyk))}

    def napisy(self):
        out = []
        for f in self.b.GetFootprints():
            ref = f.GetReference()
            for fld in list(f.GetFields()):
                L = fld.GetLayer()
                if L in (pcbnew.F_SilkS, pcbnew.B_SilkS) and fld.IsVisible():
                    out.append(("%s:%s" % (ref, fld.GetName()), fld, "F" if L == pcbnew.F_SilkS else "B",
                                fld.GetShownText(True), ref if fld.GetName() == "Reference" else None))
            for it in f.GraphicalItems():
                L = it.GetLayer()
                if it.GetClass() == "PCB_TEXT" and L in (pcbnew.F_SilkS, pcbnew.B_SilkS) and it.IsVisible():
                    out.append(("%s:tekst:%s" % (ref, it.GetText()), it, "F" if L == pcbnew.F_SilkS else "B", it.GetText(), None))
        for d in self.b.GetDrawings():
            L = d.GetLayer()
            if d.GetClass() == "PCB_TEXT" and L in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                out.append(("plytka:%s" % d.GetText()[:40], d, "F" if L == pcbnew.F_SilkS else "B", d.GetText(),
                            WLASCICIELE.get(d.GetText())))
        return out

    def pomiar(self, klucz, o, s, wl, wszystkie):
        """Pomiary tuszu napisu `o` (aktualne położenie)."""
        sh = o.GetEffectiveTextShape()
        bb = bb_mm(sh.BBox())
        e = {"klucz": klucz, "strona": s, "bb_tuszu": [round(v, 3) for v in bb]}
        e["pod_korpusem"] = sorted("%s%s" % (r, " (DNP)" if dnp else "") for r, dnp, k, kb in self.korpus[s]
                                   if blisko(bb, kb, 0) and sh.Collide(k, 0))
        e["do_krawedzi"] = do_krawedzi(bb, self.brzeg)
        e["do_padu"] = min([(odl(sh, ps), n) for n, ps, pb in self.pady[s] if blisko(bb, pb, 1.0)] or [(1.0, None)])
        if e["do_padu"][0] >= 1.0:
            e["do_padu"] = (1.0, None)
        inne = [(n, ps, pb) for n, ps, pb in self.linie[s]]
        inne += [(k2, o2.GetEffectiveTextShape(), bb_mm(o2.GetEffectiveTextShape().BBox())) for k2, o2, s2, t2, w2 in wszystkie
                 if s2 == s and k2 != klucz]
        e["do_opisu"] = min([(odl(sh, ps), n) for n, ps, pb in inne if blisko(bb, pb, 1.0)] or [(1.0, None)])
        if e["do_opisu"][0] >= 1.0:
            e["do_opisu"] = (1.0, None)
        e["przelotki"] = sum(1 for vs, vb in self.przelotki if blisko(bb, vb, 0) and sh.Collide(vs, 0))
        e["otwory_przelotek"] = sum(1 for vs, vb in self.otwory if blisko(bb, vb, 0) and sh.Collide(vs, 0))
        kor = [(odl(sh, k, 5.0), r) for r, dnp, k, kb in self.korpus[s] if blisko(bb, kb, 5.0)]
        e["najblizszy_korpus"] = list(min(kor)) if kor and min(kor)[0] < 5.0 else [None, None]
        e["courtyard"] = sorted(r for r, ps, pb in self.crt[s] if blisko(bb, pb, 0) and sh.Collide(ps, 0))
        if wl:
            kk = self.konkurenci(wl, not klucz.endswith(":Reference"))
            d_wl = min([odl(sh, ps, 20.0) for r, ps, pb in self.crt[s] if r == wl]
                       or [odl(sh, ps, 20.0) for r, ps, pb in self.crt["B" if s == "F" else "F"] if r == wl] or [None])
            d_k = self.d_konkurenta(sh, bb, kk, s)
            e["wlasciciel"] = wl
            e["do_wlasciciela"] = d_wl
            e["najblizszy_konkurent"] = list(d_k)
            e["niejednoznaczne"] = d_wl is not None and d_k[0] is not None and d_k[0] < d_wl - 0.05
            e["obcy_blizej"] = e["najblizszy_korpus"][1] not in (None, wl)
        bl = []
        if e["pod_korpusem"]:
            bl.append("pod_korpusem")
        if e["do_krawedzi"] < B_KRAWEDZ:
            bl.append("krawedz")
        if e["do_padu"][0] < B_PAD:
            bl.append("pad")
        if e["do_opisu"][0] < B_OPIS:
            bl.append("opis")
        if e.get("niejednoznaczne"):
            bl.append("niejednoznaczne")
        e["bledy"] = bl
        return e

    def kontrola(self):
        wsz = self.napisy()
        return [dict(self.pomiar(k, o, s, wl, wsz), tekst=t) for k, o, s, t, wl in wsz]

    # --- szukanie miejsca -------------------------------------------------------------------------------------
    def wolne(self, o, s, wl, klucz, wsz):
        sh = o.GetEffectiveTextShape()
        bb = bb_mm(sh.BBox())
        if do_krawedzi(bb, self.brzeg) < N_KRAWEDZ:
            return None
        for r, dnp, k, kb in self.korpus[s]:
            if blisko(bb, kb, N_KORPUS) and sh.Collide(k, MM(N_KORPUS)):
                return None
        for n, ps, pb in self.pady[s]:
            if blisko(bb, pb, N_PAD) and sh.Collide(ps, MM(N_PAD)):
                return None
        for n, ps, pb in self.linie[s]:
            if blisko(bb, pb, N_OPIS) and sh.Collide(ps, MM(N_OPIS)):
                return None
        for vs, vb in self.otwory:
            if blisko(bb, vb, 0.05) and sh.Collide(vs, MM(0.05)):
                return None
        for k2, o2, s2, t2, w2 in wsz:
            if s2 == s and k2 != klucz:
                sh2 = o2.GetEffectiveTextShape()
                if blisko(bb, bb_mm(sh2.BBox()), N_NAPIS) and sh.Collide(sh2, MM(N_NAPIS)):
                    return None
        d_wl, obcy = None, 0.0
        if wl:
            kk = self.konkurenci(wl, not klucz.endswith(":Reference"))
            d_wl = min([odl(sh, ps, 20.0) for r, ps, pb in self.crt[s] if r == wl]
                       or [odl(sh, ps, 20.0) for r, ps, pb in self.crt["B" if s == "F" else "F"] if r == wl] or [20.0])
            d_k = self.d_konkurenta(sh, bb, kk, s, d_wl + JEDNOZNACZNOSC)
            if d_k[0] is not None:
                return None
            wl_k = [k for r, dnp, k, kb in self.korpus[s] if r == wl]
            if wl_k:
                d_wk = min(odl(sh, k, 20.0) for k in wl_k)
                d_ok = min([odl(sh, k, 20.0) for r, dnp, k, kb in self.korpus[s] if r != wl and blisko(bb, kb, d_wk)] or [20.0])
                obcy = max(0.0, d_wk - d_ok + 0.1)
        wiasy = sum(1 for vs, vb in self.przelotki if blisko(bb, vb, 0) and sh.Collide(vs, 0))
        return {"d_wl": d_wl, "przelotki": wiasy, "obcy": round(obcy, 3), "bb": bb}

    def przesun(self, klucz, o, s, wl, bledy, wsz):
        poz0 = o.GetPosition()
        kat0 = o.GetTextAngleDegrees()
        roz0 = o.GetTextSize()
        gr0 = o.GetTextThickness()
        bb0 = bb_mm(o.GetEffectiveTextShape().BBox())
        c0 = ((bb0[0] + bb0[2]) / 2, (bb0[1] + bb0[3]) / 2)
        tylko_odstep = set(bledy) <= {"pad", "opis"}
        if tylko_odstep:
            kotwica, krok, warianty = c0, 0.05, [(kat0, None)]
        else:
            f = self.fps.get(wl) if wl else None
            if f is not None:
                kb = [kb for r, dnp, k, kb in self.korpus["F" if f.GetLayer() == pcbnew.F_Cu else "B"] if r == wl]
                kotwica = ((kb[0][0] + kb[0][2]) / 2, (kb[0][1] + kb[0][3]) / 2) if kb else (mm(f.GetPosition().x), mm(f.GetPosition().y))
            else:
                kotwica = c0
            krok = 0.25
            inny = 0.0 if abs(kat0 % 180) > 45 else 90.0
            warianty = [(kat0, None), (inny, None), (kat0, 0.8), (inny, 0.8)]

        def ustaw(cx, cy, kat, roz):
            o.SetTextAngleDegrees(kat)
            if roz is None:
                o.SetTextSize(roz0)
                o.SetTextThickness(gr0)
            else:
                o.SetTextSize(pcbnew.VECTOR2I(MM(roz), MM(roz)))
                o.SetTextThickness(gr0)  # kreska bez zmian (0,135 mm w etykietach funkcji, 0,15 w oznaczeniach; minimum producenta — do sprawdzenia)
            o.SetPosition(poz0)
            bb = bb_mm(o.GetEffectiveTextShape().BBox())
            p = o.GetPosition()
            o.SetPosition(pcbnew.VECTOR2I(p.x + MM(round(cx - (bb[0] + bb[2]) / 2, 4)), p.y + MM(round(cy - (bb[1] + bb[3]) / 2, 4))))

        for kat, roz in warianty:
            kand, pierwszy = [], None
            for ri in range(0, 400):
                if pierwszy is not None and (ri - pierwszy) * krok > (0.3 if tylko_odstep else PAS):
                    break
                if ri * krok > 15:
                    break
                n = max(1, 8 * ri)
                for k in range(n):
                    a = 2 * math.pi * k / n
                    cx, cy = kotwica[0] + ri * krok * math.cos(a), kotwica[1] + ri * krok * math.sin(a)
                    ustaw(cx, cy, kat, roz)
                    w = self.wolne(o, s, wl, klucz, wsz)
                    if w is None:
                        continue
                    przes = math.hypot(cx - c0[0], cy - c0[1])
                    if tylko_odstep:
                        ocena = przes + 1.0 * w["przelotki"]
                    else:
                        ocena = (w["d_wl"] or 0) + 0.6 * w["przelotki"] + 2.0 * w["obcy"] + 0.01 * ri
                    kand.append((round(ocena, 4), ri, k, cx, cy, w))
                    if pierwszy is None:
                        pierwszy = ri
            if kand:
                ocena, ri, k, cx, cy, w = min(kand, key=lambda x: x[:3])
                ustaw(cx, cy, kat, roz)
                p = o.GetPosition()
                ruch = {"klucz": klucz, "bledy": bledy, "tryb": "odstęp" if tylko_odstep else "przy właścicielu",
                        "dx": round(mm(p.x - poz0.x), 3), "dy": round(mm(p.y - poz0.y), 3), "obrot": kat,
                        "rozmiar": roz or round(mm(roz0.x), 2), "bb_przed": [round(v, 3) for v in bb0],
                        "bb_po": [round(v, 3) for v in w["bb"]], "do_wlasciciela": w["d_wl"], "przelotki": w["przelotki"],
                        "kara_obcy_korpus": w["obcy"]}
                print("przesunięty", klucz, bledy, "o", (ruch["dx"], ruch["dy"]), "mm, obrót", kat, "rozmiar", ruch["rozmiar"],
                      "| tusz", [round(v, 2) for v in w["bb"]], "| do właściciela", w["d_wl"], "| przelotki", w["przelotki"],
                      "| obcy korpus bliżej o", w["obcy"])
                return ruch
        o.SetTextAngleDegrees(kat0)
        o.SetTextSize(roz0)
        o.SetTextThickness(gr0)
        o.SetPosition(poz0)
        print("BRAK MIEJSCA:", klucz, bledy)
        return None


def nazwa(e):
    return e["klucz"].split(":")[0] if e["klucz"].endswith(":Reference") else e["tekst"][:20]


def podsumuj(lista, napis):
    zle = [e for e in lista if e["bledy"]]
    licz = {}
    for e in zle:
        for x in e["bledy"]:
            licz[x] = licz.get(x, 0) + 1
    print("%s: napisów %d, z błędami %d %s | info: przelotki pod tuszem %d napisów (otwór pod tuszem: %d), "
          "< 0,5 mm od krawędzi %d, najbliższy korpus cudzy: %s" % (
              napis, len(lista), len(zle), licz, sum(1 for e in lista if e["przelotki"]),
              sum(1 for e in lista if e["otwory_przelotek"]), sum(1 for e in lista if e["do_krawedzi"] < 0.5),
              sorted(nazwa(e) for e in lista if e.get("obcy_blizej"))))
    cudzy = sorted("%s→%s" % (nazwa(e), ",".join(c for c in e["courtyard"] if c != e.get("wlasciciel")))
                   for e in lista if [c for c in e["courtyard"] if c != e.get("wlasciciel")])
    print("   info: tusz w courtyardzie cudzego elementu:", cudzy)
    for e in zle:
        print("  ", e["klucz"], e["bledy"], "tusz", e["bb_tuszu"], "| korpus", e["pod_korpusem"], "| krawędź", e["do_krawedzi"],
              "| pad", e["do_padu"], "| opis", e["do_opisu"],
              ("| właściciel %s %s, konkurent %s" % (e.get("wlasciciel"), e.get("do_wlasciciela"), e.get("najblizszy_konkurent"))
               if e.get("wlasciciel") else ""))
    return zle


def main():
    tryb, p, raport = sys.argv[1], sys.argv[2], sys.argv[3]
    b = pcbnew.LoadBoard(p)
    pl = Plytka(b)
    przed = pl.kontrola()
    zle = podsumuj(przed, "PRZED")
    out = {"przed": przed}
    kod = 1 if zle else 0
    if tryb == "popraw" and zle:
        wsz = pl.napisy()
        ruchy = []
        for e in zle:
            k, o, s, t, wl = [x for x in wsz if x[0] == e["klucz"]][0]
            ruchy.append(pl.przesun(k, o, s, wl, e["bledy"], wsz))
        out["ruchy"] = ruchy
        po = pl.kontrola()
        out["po"] = po
        zle_po = podsumuj(po, "PO")
        if zle_po or None in ruchy:
            print("NIE ZAPISUJĘ: po poprawce zostały błędy albo brak miejsca")
            kod = 2
        else:
            pcbnew.SaveBoard(p, b)
            print("ZAPIS", flush=True)
            kod = 0
    with open(raport, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    sys.exit(kod)


if __name__ == "__main__":
    main()
