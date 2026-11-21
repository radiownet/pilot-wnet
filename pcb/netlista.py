# -*- coding: utf-8 -*-
"""Parser listy połączeń KiCada (format s-wyrażeń z SKiDL generate_netlist) — bez pcbnew (działa w zwykłym Pythonie)."""
import re


def sexp(txt):
    tok = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', txt)
    stos, cur = [], []
    for t in tok:
        if t == "(":
            stos.append(cur)
            cur = []
        elif t == ")":
            g, cur = cur, stos.pop()
            cur.append(g)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def znajdz(w, klucz):
    return [x for x in w if isinstance(x, list) and x and x[0] == klucz]


def wczytaj_netliste(sciezka):
    drzewo = sexp(open(sciezka, encoding="utf-8").read())
    komp, sieci = {}, {}
    for c in znajdz(znajdz(drzewo, "components")[0], "comp"):
        d = {k[0]: k[1] for k in c[1:] if isinstance(k, list) and len(k) == 2 and isinstance(k[1], str)}
        pola = {}
        for fl in znajdz(c, "fields"):
            for f in znajdz(fl, "field"):
                nazwa = next(x[1] for x in f if isinstance(x, list) and x[0] == "name")
                wart = next((x for x in f[1:] if isinstance(x, str)), "")
                pola[nazwa] = wart
        for p in znajdz(c, "property"):
            pd = {x[0]: x[1] for x in p if isinstance(x, list)}
            pola[pd.get("name")] = pd.get("value", "")
        komp[d["ref"]] = {"wartosc": d.get("value", ""), "footprint": d.get("footprint", ""), "pola": pola}
    for n in znajdz(znajdz(drzewo, "nets")[0], "net"):
        nazwa = next(x[1] for x in n if isinstance(x, list) and x[0] == "name")
        sieci[nazwa] = [(next(x[1] for x in w if x[0] == "ref"), next(x[1] for x in w if x[0] == "pin")) for w in znajdz(n, "node")]
    return komp, sieci
