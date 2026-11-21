# -*- coding: utf-8 -*-
"""Geometria miedzi z eksport_geometrii.py: odległości i kontrola odstępów (bez zewnętrznych bibliotek).

Kształty: ("p", wielokąt[pkt], dziury) — pad; ("c", a, b, r) — kapsuła (ścieżka; przelotka/otwór = a == b).
Odstęp = odległość między brzegami miedzi. Wszystko w mm.
"""
import json
import math

WARSTWY = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
SZER, GLEB = 90.0, 100.0


def d_pkt_odc(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _przec(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2, d3, d4 = o(c, d, a), o(c, d, b), o(a, b, c), o(a, b, d)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def d_odc_odc(a, b, c, d):
    if _przec(a, b, c, d):
        return 0.0
    return min(d_pkt_odc(a, c, d), d_pkt_odc(b, c, d), d_pkt_odc(c, a, b), d_pkt_odc(d, a, b))


def w_wielokacie(p, wk):
    x, y = p; w = False
    n = len(wk)
    for i in range(n):
        x1, y1 = wk[i]; x2, y2 = wk[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            w = not w
    return w


def d_wiel_odc(wk, a, b):
    if w_wielokacie(a, wk) or w_wielokacie(b, wk):
        return 0.0
    n = len(wk)
    return min(d_odc_odc(a, b, wk[i], wk[(i + 1) % n]) for i in range(n))


class Plytka:
    """Przeszkody na warstwach z kubełkami 2 mm."""

    def __init__(self, plik):
        g = json.load(open(plik, encoding="utf-8"))
        self.g = g
        self.kub = {L: {} for L in WARSTWY}
        self.otwory = []          # (x, y, r, siec)
        self.smd = []             # wielokąty padów SMD (każdej sieci) — przelotka nie może w nie wejść
        for p in g["pady"]:
            for L, wk in p["ksztalt"].items():
                for o in wk:
                    self._dodaj(L, ("p", o["zew"]), p["siec"], self._bbox(o["zew"]))
                    if p["atr"] == 1 and L in ("F.Cu", "B.Cu"):
                        self.smd.append((o["zew"], self._bbox(o["zew"])))
            if p["otwor"][0] > 0:
                self.otwory.append((p["poz"][0], p["poz"][1], max(p["otwor"]) / 2, p["siec"]))
        for t in g["sciezki"]:
            self._dodaj(t["warstwa"], ("c", tuple(t["a"]), tuple(t["b"]), t["w"] / 2), t["siec"], self._bbox([t["a"], t["b"]], t["w"] / 2))
        for v in g["przelotki"]:
            sr = v["sr"] or 0.6
            for L in WARSTWY:
                self._dodaj(L, ("c", tuple(v["poz"]), tuple(v["poz"]), sr / 2), v["siec"], self._bbox([v["poz"]], sr / 2))
            self.otwory.append((v["poz"][0], v["poz"][1], v["otwor"] / 2, v["siec"]))
        self.reguly = g["reguly"]

    @staticmethod
    def _bbox(pts, m=0.0):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)

    def _dodaj(self, L, ks, siec, bb):
        if L not in self.kub:
            return
        for i in range(int(bb[0] // 2), int(bb[2] // 2) + 1):
            for j in range(int(bb[1] // 2), int(bb[3] // 2) + 1):
                self.kub[L].setdefault((i, j), []).append((ks, siec, bb))

    def blisko(self, L, bb):
        wid = set()
        for i in range(int(bb[0] // 2), int(bb[2] // 2) + 1):
            for j in range(int(bb[1] // 2), int(bb[3] // 2) + 1):
                for e in self.kub[L].get((i, j), ()):
                    if id(e) not in wid:
                        wid.add(id(e))
                        yield e

    def odstep_kapsuly(self, L, a, b, r, siec, zasieg=1.0, pomin=None):
        """Najmniejszy odstęp kapsuły (a–b, promień r) do miedzi INNYCH sieci na warstwie L."""
        bb = (min(a[0], b[0]) - r - zasieg, min(a[1], b[1]) - r - zasieg, max(a[0], b[0]) + r + zasieg, max(a[1], b[1]) + r + zasieg)
        best = 99.0
        for ks, s, ebb in self.blisko(L, bb):
            if s == siec or (pomin and pomin(ks)):
                continue
            if ebb[0] > bb[2] or ebb[2] < bb[0] or ebb[1] > bb[3] or ebb[3] < bb[1]:
                continue
            if ks[0] == "p":
                d = d_wiel_odc(ks[1], a, b) - r
            else:
                d = d_odc_odc(a, b, ks[1], ks[2]) - r - ks[3]
            best = min(best, d)
        return best

    def odstep_krawedzi(self, a, b, r):
        return min(min(p[0], p[1], SZER - p[0], GLEB - p[1]) for p in (a, b)) - r

    def w_zakazie(self, L, p, ksztalt="sciezka"):
        for z in self.reguly:
            if L in z["warstwy"] and (z["zakaz_sciezek"] if ksztalt == "sciezka" else z["zakaz_przelotek"]):
                for o in z["obrys"]:
                    if w_wielokacie(p, o["zew"]):
                        return True
        return False

    def odstep_otworu(self, p, r, siec):
        best = 99.0
        for x, y, ro, s in self.otwory:
            if abs(x - p[0]) < 3 and abs(y - p[1]) < 3:
                best = min(best, math.hypot(x - p[0], y - p[1]) - r - ro)
        return best
