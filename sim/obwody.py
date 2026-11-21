# -*- coding: utf-8 -*-
"""Pilot Wnet Rev A — wspólna część testów SPICE: wartości elementów z pcb/obwod.py i uruchamianie ngspice.

Wartości NIE są tu przepisywane ręcznie. Moduł czyta tekst pcb/obwod.py drzewem składni (ast), bez importu
SKiDL-a: tabela CZESCI daje wartości, a wywołania f.R(...) / f.C(...) w buduj() — który element łączy które
sieci. Testy odwołują się do elementów po oznaczeniu (R5, C7, R61…) albo po parze sieci (V3, n_gp…), więc
zmiana wartości w obwod.py od razu zmienia decki .cir, a zmiana topologii wywraca test „topologia”.

Symulator: ngspice 47 (konsolowy ngspice_con.exe) w trybie wsadowym; wyniki .raw czyta spicelib (RawRead).
Ścieżka do ngspice (sim/README.md): zmienna PILOT_NGSPICE, a bez niej ngspice_con albo ngspice z PATH, w ostateczności
standardowa instalacja Windows C:\\Spice64\\bin\\ngspice_con.exe. Gdy ngspice nie ma, testy
SPICE są pomijane (SkipTest), a testy czysto obliczeniowe działają.
"""
import ast
import json
import os
import re
import shutil
import subprocess

TU = os.path.dirname(os.path.abspath(__file__))
OBWOD = os.environ.get("PILOT_OBWOD", os.path.join(TU, "..", "pcb", "obwod.py"))
WYNIKI = os.path.join(TU, "wyniki")
NGSPICE = (os.environ.get("PILOT_NGSPICE") or shutil.which("ngspice_con") or shutil.which("ngspice")
           or r"C:\Spice64\bin\ngspice_con.exe")

# Tolerancja rezystorów bez dopisku „%” w wartości: obwod.py, komentarz nad tabelą CZESCI („rezystory 0402 1 %
# (UNI-ROYAL …)”). Kondensatorów karta JLCPCB nie podaje w tabeli — dla nich testy liczą osobne scenariusze.
TOL_R_DOMYSLNA = 0.01

_SKALA = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6, "G": 1e9}


# --------------------------------------------------------------------------- odczyt obwod.py

class Element:
    """Jedno wywołanie f.R / f.C z buduj(): klucz tabeli CZESCI, oznaczenie i dwie sieci (tekst wyrażeń)."""

    def __init__(self, rodzaj, klucz, ref, a, b, dnp, linia):
        self.rodzaj, self.klucz, self.ref, self.a, self.b, self.dnp, self.linia = rodzaj, klucz, ref, a, b, dnp, linia

    @property
    def wartosc_tekst(self):
        return czesci()[self.klucz][0]

    @property
    def wartosc(self):
        return wartosc_si(self.wartosc_tekst)

    @property
    def tolerancja(self):
        t = tolerancja(self.wartosc_tekst)
        if t is None and self.rodzaj == "R":
            return TOL_R_DOMYSLNA
        return t

    def __repr__(self):
        return f"{self.ref}({self.klucz}={self.wartosc_tekst}: {self.a} — {self.b}, linia {self.linia})"


_drzewo = None


def _ast():
    global _drzewo
    if _drzewo is None:
        with open(OBWOD, encoding="utf-8") as fh:
            _drzewo = ast.parse(fh.read(), filename=OBWOD)
    return _drzewo


def czesci():
    """Tabela CZESCI z obwod.py: klucz -> (wartość, footprint, LCSC, uwaga). Stałe F0402R itp. podstawione."""
    stale = {}
    tabela = None
    for w in _ast().body:
        if isinstance(w, ast.Assign) and len(w.targets) == 1 and isinstance(w.targets[0], ast.Name):
            nazwa = w.targets[0].id
            if isinstance(w.value, ast.Constant) and isinstance(w.value.value, str):
                stale[nazwa] = w.value.value
            elif nazwa == "CZESCI":
                tabela = w.value
    if tabela is None:
        raise RuntimeError(f"brak tabeli CZESCI w {OBWOD}")

    def wartosc(wezel):
        if isinstance(wezel, ast.Name):
            return stale[wezel.id]
        return ast.literal_eval(wezel)

    return {ast.literal_eval(k): tuple(wartosc(e) for e in v.elts) for k, v in zip(tabela.keys, tabela.values)}


def elementy():
    """Wszystkie wywołania f.R(klucz, ref, a, b[, dnp]) i f.C(...) w funkcji buduj()."""
    buduj = _buduj()
    wynik = []
    for wezel in ast.walk(buduj):
        if not (isinstance(wezel, ast.Call) and isinstance(wezel.func, ast.Attribute)
                and isinstance(wezel.func.value, ast.Name) and wezel.func.value.id == "f"
                and wezel.func.attr in ("R", "C")):
            continue
        arg = wezel.args
        klucz = ast.literal_eval(arg[0])
        ref = ast.literal_eval(arg[1]) if isinstance(arg[1], ast.Constant) else ast.unparse(arg[1])
        dnp = False
        if len(arg) > 4:
            dnp = bool(ast.literal_eval(arg[4]))
        for kw in wezel.keywords:
            if kw.arg == "dnp":
                dnp = bool(ast.literal_eval(kw.value))
        wynik.append(Element(wezel.func.attr, klucz, ref, ast.unparse(arg[2]), ast.unparse(arg[3]), dnp, wezel.lineno))
    return sorted(wynik, key=lambda e: e.linia)


def element(ref):
    """Element o dokładnym oznaczeniu (np. "R5"). Oznaczenia z pętli mają postać f-stringa, np. "f'R{10 + i}'"."""
    traf = [e for e in elementy() if e.ref == ref]
    if len(traf) != 1:
        raise LookupError(f"{ref}: {len(traf)} trafień w {OBWOD}")
    return traf[0]


def miedzy(a, b, rodzaj=None):
    """Jedyny element między sieciami a i b (kolejność dowolna, nazwy jak w kodzie obwod.py)."""
    traf = [e for e in elementy() if {e.a, e.b} == {a, b} and (rodzaj is None or e.rodzaj == rodzaj)]
    if len(traf) != 1:
        raise LookupError(f"{rodzaj or ''} {a}—{b}: {len(traf)} trafień w {OBWOD}: {traf}")
    return traf[0]


def _buduj():
    return next(w for w in _ast().body if isinstance(w, ast.FunctionDef) and w.name == "buduj")


def wejscia():
    """Lista WEJSCIA z buduj(): [(nazwa, numer GPIO), …] — przydział pinów przycisków, który zakładają decki."""
    for w in ast.walk(_buduj()):
        if (isinstance(w, ast.Assign) and len(w.targets) == 1 and isinstance(w.targets[0], ast.Name)
                and w.targets[0].id == "WEJSCIA"):
            return [tuple(x) for x in ast.literal_eval(w.value)]
    raise LookupError(f"brak listy WEJSCIA w buduj() ({OBWOD})")


def gpio_sieci(siec):
    """Numery GPIO dołączone do sieci zapisem `siec += io(N)` w buduj() (np. "vs" -> [1])."""
    wynik = []
    for w in ast.walk(_buduj()):
        if (isinstance(w, ast.AugAssign) and isinstance(w.target, ast.Name) and w.target.id == siec
                and isinstance(w.value, ast.Call) and isinstance(w.value.func, ast.Name)
                and w.value.func.id == "io" and isinstance(w.value.args[0], ast.Constant)):
            wynik.append(w.value.args[0].value)
    return wynik


def wartosc_si(tekst):
    """'10k' -> 1e4, '1uF' -> 1e-6, '22k 1%' -> 22e3, '49.9 1%' -> 49.9, '6.8pF C0G' -> 6.8e-12."""
    m = re.match(r"^([0-9]+(?:[.,][0-9]+)?)(.?)", tekst.split()[0])
    if not m:
        raise ValueError(f"nie umiem odczytać wartości {tekst!r}")
    x = float(m.group(1).replace(",", "."))
    return x * _SKALA.get(m.group(2), 1.0)


def tolerancja(tekst):
    """'22k 1%' -> 0.01; brak dopisku -> None."""
    for s in tekst.split()[1:]:
        if s.endswith("%"):
            return float(s[:-1].replace(",", ".")) / 100
    return None


def obciazenie_kwarcu_pf():
    """CL kwarcu z wartości XTAL25 w CZESCI, np. '25MHz CL18pF' -> 18.0."""
    for s in czesci()["XTAL25"][0].split():
        if s.upper().startswith("CL"):
            return wartosc_si(s[2:]) * 1e12
    raise LookupError("XTAL25 bez CL")


# --------------------------------------------------------------------------- ngspice

def ngspice_dostepny():
    return os.path.isfile(NGSPICE) or shutil.which(NGSPICE) is not None


def wymagaj_ngspice(test):
    import unittest
    if not ngspice_dostepny():
        raise unittest.SkipTest(f"brak ngspice ({NGSPICE}) — ustaw PILOT_NGSPICE albo dodaj ngspice_con/ngspice do PATH")
    try:
        import spicelib  # noqa: F401
    except ImportError:
        raise unittest.SkipTest("brak spicelib w tym Pythonie")


def liczba(x):
    """Zapis liczby dla SPICE bez przyrostków (unika pomyłki m/M)."""
    return f"{x:.9g}"


def uruchom(nazwa, deck):
    """Zapisuje wyniki/<nazwa>.cir, uruchamia ngspice -b, zwraca słownik {nazwa_wektora_małymi: numpy.array}."""
    from spicelib import RawRead
    os.makedirs(WYNIKI, exist_ok=True)
    cir = os.path.join(WYNIKI, nazwa + ".cir")
    raw = os.path.join(WYNIKI, nazwa + ".raw")
    log = os.path.join(WYNIKI, nazwa + ".log")
    with open(cir, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(deck if deck.endswith("\n") else deck + "\n")
    if os.path.exists(raw):
        os.remove(raw)
    p = subprocess.run([NGSPICE, "-b", "-r", raw, "-o", log, cir], capture_output=True, text=True, timeout=600)
    if p.returncode != 0 or not os.path.exists(raw):
        tresc = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
        raise RuntimeError(f"ngspice rc={p.returncode} dla {cir}\n{p.stdout}\n{p.stderr}\n{tresc[-3000:]}")
    r = RawRead(raw, dialect="ngspice", verbose=False)
    wektory = {}
    for n in r.get_trace_names():
        wektory[n.lower()] = r.get_trace(n).get_wave(0)
    return wektory


# --------------------------------------------------------------------------- przebiegi

def przeciecie(t, y, prog, kierunek=+1, od=0.0):
    """Pierwszy czas >= od, w którym y przecina prog (kierunek +1 w górę, -1 w dół); interpolacja liniowa.
    prog może być liczbą albo tablicą tej samej długości co t (np. 0,75 · VDD(t)). None, gdy brak przecięcia."""
    import numpy as np
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    p = np.broadcast_to(np.asarray(prog, dtype=float), y.shape)
    d = (y - p) * kierunek
    for i in range(1, len(t)):
        if t[i] < od or d[i] < 0:
            continue
        if d[i - 1] < 0:
            u = -d[i - 1] / (d[i] - d[i - 1])
            return float(max(od, t[i - 1] + u * (t[i] - t[i - 1])))
        if t[i - 1] < od:      # warunek spełniony już w chwili od — to nie jest przecięcie
            return None
    return None


def wartosc_w(t, y, chwila):
    import numpy as np
    return float(np.interp(chwila, np.asarray(t, dtype=float), np.asarray(y, dtype=float)))


def bisekcja(f, a, b, krokow=14):
    """Największe x w [a, b], dla którego f(x) >= 0, przy założeniu monotoniczności (f(a) >= 0 > f(b))."""
    fa, fb = f(a), f(b)
    if fa < 0:
        return None
    if fb >= 0:
        return b
    for _ in range(krokow):
        m = 0.5 * (a + b)
        if f(m) >= 0:
            a = m
        else:
            b = m
    return a


# --------------------------------------------------------------------------- wyniki

def zapisz_wynik(obwod, dane):
    """Dopisuje wyniki jednego obwodu do wyniki/wyniki.json (słownik obwód -> dane)."""
    os.makedirs(WYNIKI, exist_ok=True)
    plik = os.path.join(WYNIKI, "wyniki.json")
    wszystko = {}
    if os.path.exists(plik):
        try:
            with open(plik, encoding="utf-8") as fh:
                wszystko = json.load(fh)
        except ValueError:
            wszystko = {}
    wszystko.setdefault(obwod, {}).update(dane)
    with open(plik, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(wszystko, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"[{obwod}] " + json.dumps(dane, ensure_ascii=False, sort_keys=True))
