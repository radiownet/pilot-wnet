# -*- coding: utf-8 -*-
"""Mały router rastrowy do domknięcia pojedynczych połączeń (pakiet v0.1, 19.11.2026).

Mapa przeszkód (numpy) w oknie wokół połączenia: komórka zablokowana, gdy jej środek jest bliżej niż
r + KLR + ZAPAS od miedzi INNEJ sieci (pady jako wielokąty, ścieżki i przelotki jako kapsuły), krawędzi płytki
(0,4 mm) albo leży w obszarze zakazu. A* po (x, y, warstwa), zmiana warstwy = przelotka 0,6/0,3 mm
(wolne miejsce na wszystkich 4 warstwach + otwór–otwór). Wynik: odcinki po scaleniu kierunków i przelotki;
każdy odcinek sprawdzany potem dokładnie (geom_v01.Plytka).
"""
import heapq
import math

import numpy as np

from geom_v01 import WARSTWY, SZER, GLEB

KLR = 0.205      # reguła 0,20 mm + zapas na przybliżenie łuków w eksporcie
ZAPAS = 0.035    # na dyskretyzację siatki
H = 0.05         # krok siatki [mm]
KRAW = 0.40      # miedź od krawędzi
VIA_R, VIA_OTW = 0.30, 0.15


class Okno:
    def __init__(self, pl, x0, y0, x1, y1):
        self.pl = pl
        self.x0, self.y0 = x0, y0
        self.nx = int(math.ceil((x1 - x0) / H)) + 1
        self.ny = int(math.ceil((y1 - y0) / H)) + 1
        xs = x0 + np.arange(self.nx) * H
        ys = y0 + np.arange(self.ny) * H
        self.X, self.Y = np.meshgrid(xs, ys, indexing="ij")
        self.bb = (x0, y0, x1, y1)
        self._dist = {}

    def ij(self, p):
        return int(round((p[0] - self.x0) / H)), int(round((p[1] - self.y0) / H))

    def xy(self, i, j):
        return (round(self.x0 + i * H, 4), round(self.y0 + j * H, 4))

    def odleglosc(self, L, siec):
        """Odległość środka komórki od miedzi innych sieci na warstwie L (cache)."""
        k = (L, siec)
        if k in self._dist:
            return self._dist[k]
        D = np.full(self.X.shape, 99.0)
        x0, y0, x1, y1 = self.bb
        for ks, s, ebb in self.pl.blisko(L, (x0 - 1, y0 - 1, x1 + 1, y1 + 1)):
            if s == siec:
                continue
            i0 = max(0, int((ebb[0] - 1.5 - x0) / H)); i1 = min(self.nx, int((ebb[2] + 1.5 - x0) / H) + 1)
            j0 = max(0, int((ebb[1] - 1.5 - y0) / H)); j1 = min(self.ny, int((ebb[3] + 1.5 - y0) / H) + 1)
            if i0 >= i1 or j0 >= j1:
                continue
            PX, PY = self.X[i0:i1, j0:j1], self.Y[i0:i1, j0:j1]
            if ks[0] == "c":
                d = _d_odc(PX, PY, ks[1], ks[2]) - ks[3]
            else:
                wk = ks[1]
                d = np.full(PX.shape, 99.0)
                n = len(wk)
                for e in range(n):
                    d = np.minimum(d, _d_odc(PX, PY, wk[e], wk[(e + 1) % n]))
                d = np.where(_wewnatrz(PX, PY, wk), 0.0, d)
            D[i0:i1, j0:j1] = np.minimum(D[i0:i1, j0:j1], d)
        self._dist[k] = D
        return D

    def zakaz(self, L):
        Z = np.zeros(self.X.shape, bool)
        for z in self.pl.reguly:
            if L in z["warstwy"] and (z["zakaz_sciezek"] or z["zakaz_przelotek"]):
                for o in z["obrys"]:
                    Z |= _wewnatrz(self.X, self.Y, o["zew"])
        return Z

    def wolne(self, L, siec, r):
        D = self.odleglosc(L, siec)
        kraw = np.minimum.reduce([self.X, self.Y, SZER - self.X, GLEB - self.Y])
        return (D >= r + KLR + ZAPAS) & (kraw >= r + KRAW + ZAPAS) & ~self.zakaz(L)

    def wolne_przelotki(self, siec):
        W = np.ones(self.X.shape, bool)
        for L in WARSTWY:
            W &= self.odleglosc(L, siec) >= VIA_R + KLR + ZAPAS
        kraw = np.minimum.reduce([self.X, self.Y, SZER - self.X, GLEB - self.Y])
        W &= kraw >= VIA_R + KRAW + ZAPAS
        for L in WARSTWY:
            W &= ~self.zakaz(L)
        Ho = np.full(self.X.shape, 99.0)
        for x, y, ro, s in self.pl.otwory:
            if self.bb[0] - 2 < x < self.bb[2] + 2 and self.bb[1] - 2 < y < self.bb[3] + 2:
                Ho = np.minimum(Ho, np.hypot(self.X - x, self.Y - y) - ro)
        W &= Ho >= VIA_OTW + 0.26 + ZAPAS
        # bez przelotek w padach SMD (także tej samej sieci): wsysanie lutu przy montażu SMD
        Ds = np.full(self.X.shape, 99.0)
        x0, y0, x1, y1 = self.bb
        for wk, ebb in self.pl.smd:
            if ebb[0] > x1 + 1 or ebb[2] < x0 - 1 or ebb[1] > y1 + 1 or ebb[3] < y0 - 1:
                continue
            d = np.full(self.X.shape, 99.0)
            n = len(wk)
            for e in range(n):
                d = np.minimum(d, _d_odc(self.X, self.Y, wk[e], wk[(e + 1) % n]))
            d = np.where(_wewnatrz(self.X, self.Y, wk), 0.0, d)
            Ds = np.minimum(Ds, d)
        W &= Ds >= VIA_R + 0.10
        return W


def _d_odc(PX, PY, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    if L == 0:
        return np.hypot(PX - ax, PY - ay)
    t = np.clip(((PX - ax) * dx + (PY - ay) * dy) / L, 0, 1)
    return np.hypot(PX - (ax + t * dx), PY - (ay + t * dy))


def _wewnatrz(PX, PY, wk):
    w = np.zeros(PX.shape, bool)
    n = len(wk)
    for e in range(n):
        x1, y1 = wk[e]; x2, y2 = wk[(e + 1) % n]
        if y1 == y2:
            continue
        c = ((y1 > PY) != (y2 > PY)) & (PX < (x2 - x1) * (PY - y1) / (y2 - y1) + x1)
        w ^= c
    return w


def trasuj(okno, siec, r, start, cele, warstwy=("F.Cu", "B.Cu"), koszt_via=4.0, cel_przelotka=None, max_kroki=3_000_000):
    """start: (pkt, warstwa); cele: lista (pkt, warstwa, promień_przyjęcia) albo cel_przelotka: maska (via w niej = cel).
    Zwraca listę węzłów [(i, j, L)] albo None."""
    wolne = {L: okno.wolne(L, siec, r) for L in warstwy}
    wv = okno.wolne_przelotki(siec)
    (sp, sL) = start
    si, sj = okno.ij(sp)
    # start i cele leżą w miedzi tej samej sieci: odblokuj małe koła wokół nich
    for (p, L, rr) in [(sp, sL, 0.3)] + [(c[0], c[1], c[2]) for c in cele]:
        ci, cj = okno.ij(p)
        k = int(rr / H) + 1
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if di * di + dj * dj <= k * k and 0 <= ci + di < okno.nx and 0 <= cj + dj < okno.ny:
                    for LL in ([L] if L in wolne else []):
                        wolne[LL][ci + di, cj + dj] = True
    cel_set = {}
    for (p, L, rr) in cele:
        ci, cj = okno.ij(p)
        k = max(1, int(rr / H))
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if di * di + dj * dj <= k * k:
                    for LL in ([L] if L != "*" else warstwy):
                        cel_set[(ci + di, cj + dj, LL)] = True
    ti = [okno.ij(c[0]) for c in cele]

    def hcost(i, j):
        if not ti:
            return 0
        return min(math.hypot(i - a, j - b) for a, b in ti) * H

    ruchy = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
    s0 = (si, sj, sL)
    g = {s0: 0.0}
    prev = {}
    pq = [(hcost(si, sj), 0.0, s0, None)]
    kroki = 0
    while pq:
        f, gc, s, kier = heapq.heappop(pq)
        if gc > g.get(s, 1e9) + 1e-9:
            continue
        i, j, L = s
        if s in cel_set or (cel_przelotka is not None and L == "VIA_CEL"):
            path = [s]
            while s in prev:
                s = prev[s]
                path.append(s)
            return path[::-1]
        kroki += 1
        if kroki > max_kroki:
            return None
        for di, dj, c in ruchy:
            ni, nj = i + di, j + dj
            if not (0 <= ni < okno.nx and 0 <= nj < okno.ny) or not wolne[L][ni, nj]:
                continue
            kara = 0.0 if kier in (None, (di, dj)) else 0.02   # mniej zakrętów
            ns = (ni, nj, L)
            ng = gc + c * H + kara
            if ng < g.get(ns, 1e9):
                g[ns] = ng; prev[ns] = s
                heapq.heappush(pq, (ng + hcost(ni, nj), ng, ns, (di, dj)))
        if wv[i, j]:
            for L2 in warstwy:
                if L2 != L and wolne[L2][i, j]:
                    ns = (i, j, L2)
                    ng = gc + koszt_via
                    if ng < g.get(ns, 1e9):
                        g[ns] = ng; prev[ns] = s
                        heapq.heappush(pq, (ng + hcost(i, j), ng, ns, None))
            if cel_przelotka is not None and cel_przelotka[i, j]:
                ns = (i, j, "VIA_CEL")
                ng = gc + koszt_via
                if ng < g.get(ns, 1e9):
                    g[ns] = ng; prev[ns] = s
                    heapq.heappush(pq, (ng, ng, ns, None))
    return None


def na_odcinki(okno, path):
    """Węzły → odcinki (scalone po kierunku) i przelotki."""
    odc, via = [], []
    cur = [path[0]]
    for s in path[1:]:
        if s[2] != cur[-1][2]:
            via.append(okno.xy(s[0], s[1]))
            if len(cur) > 1:
                odc.append(cur)
            cur = [s] if s[2] != "VIA_CEL" else []
            continue
        cur.append(s)
    if len(cur) > 1:
        odc.append(cur)
    wynik = []
    for c in odc:
        pts = [c[0]]
        for k in range(1, len(c) - 1):
            a, b, d = pts[-1], c[k], c[k + 1]
            if (b[0] - a[0]) * (d[1] - b[1]) != (b[1] - a[1]) * (d[0] - b[0]):
                pts.append(b)
        pts.append(c[-1])
        for k in range(len(pts) - 1):
            wynik.append((okno.xy(pts[k][0], pts[k][1]), okno.xy(pts[k + 1][0], pts[k + 1][1]), c[0][2]))
    return wynik, via
