# -*- coding: utf-8 -*-
"""Pilot Wnet — wersja arcade: model i wizualizacja w Blenderze (tryb wsadowy, bez MCP).

Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python generuj_arcade.py -- --geometria ..\\projekt\\arcade.toml --marka radio_wnet ^
      --wyjscie %USERPROFILE%\\Documents\\PilotWnet\\arcade

Opcjonalnie `--grafika <plik.png>`: grafika blatu z logo marki. To plik spoza repozytorium — generator
grafiki marki (branding/grafika_blatu.py) i logo, które jest znakiem towarowym, nie wchodzą do repo.

Jedyne źródło wymiarów: projekt/arcade.toml (tylko czytany). Układ świata (mm): z = 0 to blat
stołu, x w prawo, y od użytkownika do tyłu. Układ blatu (u, v, w): u wzdłuż x, v po skosie do tyłu,
w prostopadle do blatu, początek w środku górnej powierzchni pleksi.
Wynik: pilot_arcade.blend, render_*.png, kontrole.json (luzy i zgodność z płytką).
"""

import argparse
import json
import math
import os
import sys
import time
import tomllib

import bmesh
import bpy
from mathutils import Matrix, Vector

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T0 = time.perf_counter()
MM = 0.001  # scena w metrach, dane w mm


def log(*a):
    print(f"[{time.perf_counter() - T0:6.1f}s]", *a, flush=True)


def argumenty():
    a = argparse.ArgumentParser()
    a.add_argument("--geometria", required=True)
    a.add_argument("--marka", default="radio_wnet")
    a.add_argument("--wyjscie", required=True)
    a.add_argument("--probki", type=int, default=48)
    a.add_argument("--bez-renderu", action="store_true")
    a.add_argument("--grafika", default="",
                   help="opcjonalny PNG z grafiką marki (tekstura folii pod pleksi); plik spoza repozytorium")
    return a.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


# ----------------------------------------------------------------------------- materiały

def hex_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def _wejscie(bsdf, *nazwy):
    for n in nazwy:
        if n in bsdf.inputs:
            return bsdf.inputs[n]
    return None


def material(nazwa, kolor, szorstkosc=0.5, metal=0.0, przezr=0.0, ior=1.49, powloka=0.0):
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = hex_lin(kolor) if isinstance(kolor, str) else kolor
    b.inputs["Roughness"].default_value = szorstkosc
    b.inputs["Metallic"].default_value = metal
    w = _wejscie(b, "Transmission Weight", "Transmission")
    if w is not None:
        w.default_value = przezr
    w = _wejscie(b, "IOR")
    if w is not None:
        w.default_value = ior
    w = _wejscie(b, "Coat Weight", "Clearcoat")
    if w is not None:
        w.default_value = powloka
    m.diffuse_color = hex_lin(kolor) if isinstance(kolor, str) else kolor
    return m


def material_drewno(nazwa="sklejka"):
    """Sklejka brzozowa: jasne drewno ze słojami (szum + fala), bez tekstur z dysku."""
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.0, 40.0, 2.0)
    fala = nt.nodes.new("ShaderNodeTexWave")
    fala.inputs["Scale"].default_value = 3.0
    fala.inputs["Distortion"].default_value = 6.0
    szum = nt.nodes.new("ShaderNodeTexNoise")
    szum.inputs["Scale"].default_value = 30.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].color = hex_lin("#C9A27A")
    rampa.color_ramp.elements[1].color = hex_lin("#E9D2AE")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], fala.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], szum.inputs["Vector"])
    nt.links.new(fala.outputs["Fac"], mix.inputs["A"])
    nt.links.new(szum.outputs["Fac"], mix.inputs["B"])
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(mix.outputs["Result"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.62
    m.diffuse_color = hex_lin("#D8B98F")
    return m


# ----------------------------------------------------------------------------- bryły

def nowy_obiekt(bm, nazwa, kol, mat=None):
    me = bpy.data.meshes.new(nazwa)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nazwa, me)
    kol.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def prostopadloscian(sx, sy, sz, M=Matrix(), kol=None, nazwa="blok", mat=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx * MM, sy * MM, sz * MM), verts=bm.verts)
    bmesh.ops.transform(bm, matrix=skaluj(M), verts=bm.verts)
    return nowy_obiekt(bm, nazwa, kol, mat)


def walec(r, h, M=Matrix(), kol=None, nazwa="walec", mat=None, n=48, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=n, radius1=r * MM,
                          radius2=(r if r2 is None else r2) * MM, depth=h * MM)
    bmesh.ops.transform(bm, matrix=skaluj(M), verts=bm.verts)
    return nowy_obiekt(bm, nazwa, kol, mat)


def kula(r, M=Matrix(), kol=None, nazwa="kula", mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=r * MM)
    bmesh.ops.transform(bm, matrix=skaluj(M), verts=bm.verts)
    ob = nowy_obiekt(bm, nazwa, kol, mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def pryzma(profil_yz, x0, x1, kol, nazwa, mat=None):
    """Bryła o profilu w płaszczyźnie YZ (mm), wyciągnięta wzdłuż x od x0 do x1."""
    bm = bmesh.new()
    dol = [bm.verts.new((x0 * MM, y * MM, z * MM)) for y, z in profil_yz]
    gora = [bm.verts.new((x1 * MM, y * MM, z * MM)) for y, z in profil_yz]
    bm.faces.new(list(reversed(dol)))
    bm.faces.new(gora)
    n = len(profil_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((dol[i], dol[j], gora[j], gora[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return nowy_obiekt(bm, nazwa, kol, mat)


def skaluj(M):
    """Macierz w mm → metry (przesunięcie)."""
    M = M.copy()
    M.translation = M.translation * MM
    return M


def roznica(cel, narzedzia):
    for i, t in enumerate(narzedzia):
        mod = cel.modifiers.new(f"r{i}", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = t
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(cel.evaluated_get(dg))
    stara = cel.data
    cel.modifiers.clear()
    cel.data = me
    bpy.data.meshes.remove(stara)
    for t in narzedzia:
        bpy.data.objects.remove(t, do_unlink=True)


def kolekcja(nazwa):
    k = bpy.data.collections.new(nazwa)
    bpy.context.scene.collection.children.link(k)
    return k


# ----------------------------------------------------------------------------- geometria

class G:
    def __init__(self, d):
        self.d = d
        o = d["obudowa"]
        self.W, self.D = o["szerokosc"], o["glebokosc"]
        self.hf, self.hb = o["wys_przod"], o["wys_tyl"]
        self.t, self.tb = o["sciana"], o["dno"]
        bl = d["blat"]
        self.stos = bl["pleksi"] + bl["grafika"] + bl["plyta"]
        self.kat = math.atan2(self.hb - self.hf, self.D)
        # blat: górna powierzchnia pleksi przechodzi przez (y=-D/2, z=hf) i (y=D/2, z=hb)
        sr = Vector((0.0, 0.0, (self.hf + self.hb) / 2))
        self.T = Matrix.Translation(sr) @ Matrix.Rotation(self.kat, 4, "X")
        self.dl_blatu = self.D / math.cos(self.kat)

    def P(self, u, v, w=0.0):
        """Punkt blatu (u, v, w) → świat (mm)."""
        return self.T @ Vector((u, v, w))

    def M(self, u, v, w=0.0):
        return self.T @ Matrix.Translation((u, v, w))

    def z_blatu_spod(self, y):
        """Wysokość spodu stosu blatu nad stołem dla danego y (mm)."""
        z_gora = self.hf + (y + self.D / 2) * (self.hb - self.hf) / self.D
        return z_gora - self.stos / math.cos(self.kat)


def buduj_obudowe(g, k, mat_d):
    W, D, t, tb = g.W, g.D, g.t, g.tb
    sp = g.stos / math.cos(g.kat)
    prof = [(-D / 2, 0.0), (D / 2, 0.0), (D / 2, g.hb - sp), (-D / 2, g.hf - sp)]
    czesci = {
        "bok_lewy": pryzma(prof, -W / 2, -W / 2 + t, k, "bok_lewy", mat_d),
        "bok_prawy": pryzma(prof, W / 2 - t, W / 2, k, "bok_prawy", mat_d),
    }
    hf_s, hb_s = g.hf - sp, g.hb - sp
    czesci["przod"] = pryzma([(-D / 2, tb), (-D / 2 + t, tb), (-D / 2 + t, g.z_blatu_spod(-D / 2 + t)), (-D / 2, hf_s)],
                             -W / 2 + t, W / 2 - t, k, "przod", mat_d)
    czesci["tyl"] = pryzma([(D / 2 - t, tb), (D / 2, tb), (D / 2, hb_s), (D / 2 - t, g.z_blatu_spod(D / 2 - t))],
                           -W / 2 + t, W / 2 - t, k, "tyl", mat_d)
    czesci["dno"] = prostopadloscian(W - 2 * t, D - 2 * t, tb, Matrix.Translation((0, 0, tb / 2)), k, "dno", mat_d)
    # wycięcia w tylnej ścianie
    ty = g.d["tyl"]
    yb = D / 2 - t / 2
    narz = [prostopadloscian(ty["usb_c"]["w"], t * 3, ty["usb_c"]["h"], Matrix.Translation((ty["usb_c"]["x"], yb, ty["usb_c"]["z"])), k, "c_usb"),
            prostopadloscian(ty["rj45"]["w"], t * 3, ty["rj45"]["h"], Matrix.Translation((ty["rj45"]["x"], yb, ty["rj45"]["z"])), k, "c_rj45"),
            walec(ty["sma"]["d"] / 2, t * 3, Matrix.Translation((ty["sma"]["x"], yb, ty["sma"]["z"])) @ Matrix.Rotation(math.pi / 2, 4, "X"), k, "c_sma")]
    roznica(czesci["tyl"], narz)
    return czesci


def otwory_blatu(g, k, w0, w1, z_oled=True):
    narz = []
    h = (w1 - w0) + 4
    wm = (w0 + w1) / 2
    for p in g.d["przycisk"]:
        narz.append(walec(p["srednica"] / 2, h, g.M(p["u"], p["v"], wm), k, f"c_{p['nazwa']}"))
    j = g.d["joystick"]
    narz.append(walec(j["otwor"] / 2, h, g.M(j["u"], j["v"], wm), k, "c_joy"))
    if z_oled:
        o = g.d["oled"]
        ow, oh = g.d["blat"]["okno_oled"]
        narz.append(prostopadloscian(ow, oh, h, g.M(o["u"], o["v"], wm), k, "c_oled"))
    return narz


def buduj_blat(g, k, marka, mats):
    bl = g.d["blat"]
    L = g.dl_blatu
    warstwy = {}
    w = 0.0
    for nazwa, gr, mat in (("pleksi", bl["pleksi"], mats["pleksi"]), ("grafika", bl["grafika"], mats["grafika"]),
                           ("plyta_nosna", bl["plyta"], mats["plyta"])):
        ob = prostopadloscian(g.W, L, gr, g.M(0, 0, w - gr / 2), k, nazwa, mat)
        # pleksi ciągła nad ekranem OLED, pozostałe warstwy z oknem
        roznica(ob, otwory_blatu(g, k, w - gr, w, z_oled=(nazwa != "pleksi")))
        warstwy[nazwa] = (ob, w - gr, w)
        w -= gr
    return warstwy


def ikona(g, k, p, mat):
    """Przezroczysta naklejka z ikoną na kapturku przycisku (cienka warstwa nad kapturkiem)."""
    s = p["srednica"] * 0.30
    pw = g.d["przycisk_wspolne"]["wys_nad"] + 0.15
    M = g.M(p["u"], p["v"], pw)
    typ = p.get("ikona", "brak")
    if typ == "kolo":
        return [walec(s * 0.55, 0.3, M, k, f"ikona_{p['nazwa']}", mat)]
    if typ == "kwadrat":
        return [prostopadloscian(s, s, 0.3, M, k, f"ikona_{p['nazwa']}", mat)]
    if typ == "trojkat":
        bm = bmesh.new()
        pts = [(-s * 0.45, -s * 0.55), (-s * 0.45, s * 0.55), (s * 0.6, 0.0)]
        dol = [bm.verts.new((x, y, -0.15)) for x, y in pts]
        gora = [bm.verts.new((x, y, 0.15)) for x, y in pts]
        bm.faces.new(list(reversed(dol)))
        bm.faces.new(gora)
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((dol[i], dol[j], gora[j], gora[i]))
        bmesh.ops.scale(bm, vec=(MM, MM, MM), verts=bm.verts)
        bmesh.ops.transform(bm, matrix=skaluj(M), verts=bm.verts)
        return [nowy_obiekt(bm, f"ikona_{p['nazwa']}", k, mat)]
    if typ == "koperta":
        return [prostopadloscian(s * 1.3, s * 0.85, 0.3, M, k, f"ikona_{p['nazwa']}", mat)]
    if typ == "ptaszek":
        a = prostopadloscian(s * 0.45, s * 0.16, 0.3, M @ Matrix.Translation((-s * 0.25, -s * 0.05, 0)) @ Matrix.Rotation(-0.8, 4, "Z"), k, f"ikona_{p['nazwa']}_a", mat)
        b = prostopadloscian(s * 0.85, s * 0.16, 0.3, M @ Matrix.Translation((s * 0.12, s * 0.1, 0)) @ Matrix.Rotation(0.9, 4, "Z"), k, f"ikona_{p['nazwa']}_b", mat)
        return [a, b]
    return []


def naloz_grafike(g, ob, png):
    """Tekstura folii: UV z układu blatu (u, v) → ((u + W/2)/W, (v + L/2)/L), jak X/Y w generatorze grafiki
    marki (branding/grafika_blatu.py, poza repozytorium)."""
    Ti = g.T.inverted()
    uv = ob.data.uv_layers.new(name="blat")
    for petla in ob.data.loops:
        p = Ti @ ((ob.matrix_world @ ob.data.vertices[petla.vertex_index].co) / MM)
        uv.data[petla.index].uv = ((p.x + g.W / 2) / g.W, (p.y + g.dl_blatu / 2) / g.dl_blatu)
    m = bpy.data.materials.new("grafika_marki")
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    # połysk pleksi leżącej na folii jako cienka powłoka; mocniejsza powłoka odbija lampy i wybiela grafikę
    b.inputs["Roughness"].default_value = 0.6
    for nazwy, wartosc in ((("Specular IOR Level", "Specular"), 0.2), (("Coat Weight", "Clearcoat"), 0.25), (("Coat Roughness", "Clearcoat Roughness"), 0.05)):
        w = _wejscie(b, *nazwy)
        if w is not None:
            w.default_value = wartosc
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(png)
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    ob.data.materials.clear()
    ob.data.materials.append(m)


def buduj_przyciski(g, k, mats):
    pw = g.d["przycisk_wspolne"]
    obiekty = []
    for p in g.d["przycisk"]:
        r = p["srednica"] / 2
        # OBSC: kapturek z przezroczystego barwionego tworzywa, wkładka z ikoną pod spodem
        m = material(f"przycisk_{p['nazwa']}", p["kolor"], 0.25, powloka=0.6, przezr=0.45 if "OBSC" in p.get("czesc", "") else 0.0)
        obiekty.append(walec(r + pw["kolnierz"], 1.2, g.M(p["u"], p["v"], 0.6), k, f"kolnierz_{p['nazwa']}", m))
        obiekty.append(walec(r - 1.6, pw["wys_nad"], g.M(p["u"], p["v"], pw["wys_nad"] / 2), k, f"kapturek_{p['nazwa']}", m, r2=r - 2.0))
        obiekty.append(walec(r - 0.5, pw["glebokosc_pod"], g.M(p["u"], p["v"], -g.stos - pw["glebokosc_pod"] / 2), k, f"korpus_{p['nazwa']}", mats["korpus"]))
        obiekty += ikona(g, k, p, mats["ikona"])
    return obiekty


def buduj_joystick(g, k, mats):
    j = g.d["joystick"]
    u, v = j["u"], j["v"]
    ob = [walec(j["otwor"] / 2 + 3.5, 1.0, g.M(u, v, 0.5), k, "joy_oslona", mats["czarny"]),
          walec(4.0, j["wys_nad"], g.M(u, v, j["wys_nad"] / 2), k, "joy_trzon", mats["metal"]),
          kula(j["kula"] / 2, g.M(u, v, j["wys_nad"]), k, "joy_kula", mats["kula"])]
    pm = j["plytka_mont"]
    ob.append(prostopadloscian(pm[0], pm[1], 1.6, g.M(u, v, -g.stos - 0.8), k, "joy_plytka_mont", mats["metal"]))
    ob.append(prostopadloscian(44.0, 44.0, j["wys_pod"] - 1.6, g.M(u, v, -g.stos - 1.6 - (j["wys_pod"] - 1.6) / 2), k, "joy_korpus", mats["czarny"]))
    return ob


def buduj_oled(g, k, mats):
    o = g.d["oled"]
    w = -g.d["blat"]["pleksi"] - g.d["blat"]["grafika"] - g.d["blat"]["plyta"]
    e = o["ekran"]
    return [prostopadloscian(e[0] + 6, e[1] + 14, 1.6, g.M(o["u"], o["v"], w - 3.0), k, "oled_plytka", mats["pcb"]),
            prostopadloscian(e[0], e[1], 1.2, g.M(o["u"], o["v"], w - 1.6), k, "oled_ekran", mats["ekran"])]


def buduj_plytke(g, k, mats):
    p = g.d["plytka"]
    z0 = g.tb + p["dystans"]
    X, Y = p["x"], p["y"]
    M0 = Matrix.Translation((X, Y, z0 + p["grub"] / 2))
    ob = {"pcb": prostopadloscian(p["szer"], p["gleb"], p["grub"], M0, k, "pcb", mats["pcb"])}
    top = z0 + p["grub"]
    blok = lambda n, sx, sy, sz, x, y, mat: prostopadloscian(sx, sy, sz, Matrix.Translation((X + x, Y + y, top + sz / 2)), k, n, mat)
    ob["esp32s3_modul"] = blok("esp32s3_modul", 18.0, 25.5, 3.1, -30.0, -5.0, mats["metal"])
    ob["lora_modul"] = blok("lora_modul", 16.0, 16.0, 2.8, 25.0, 0.0, mats["metal"])
    ob["w5500"] = blok("w5500", 7.0, 7.0, 1.0, 0.0, 20.0, mats["czarny"])
    ty = g.d["tyl"]
    yb = g.D / 2 - g.t
    ob["rj45"] = prostopadloscian(16.0, 21.0, 13.5, Matrix.Translation((ty["rj45"]["x"], yb - 10.5 + 1.0, top + 6.75)), k, "rj45", mats["metal"])
    ob["usb_c"] = prostopadloscian(9.0, 7.5, 3.2, Matrix.Translation((ty["usb_c"]["x"], yb - 3.75 + 0.5, top + 1.6)), k, "usb_c", mats["metal"])
    ob["sma"] = walec(3.2, 9.0 + g.t + 3.0, Matrix.Translation((ty["sma"]["x"], yb + (g.t + 3.0) / 2 - 3.0, ty["sma"]["z"])) @ Matrix.Rotation(math.pi / 2, 4, "X"), k, "sma", mats["zloto"])
    ob["antena"] = walec(5.0, 110.0, Matrix.Translation((ty["sma"]["x"], g.D / 2 + 9.0, ty["sma"]["z"] + 55.0)), k, "antena_868", mats["czarny"], r2=3.5)
    for i, (dx, dy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        cx, cy = X + dx * (p["szer"] / 2 - 4), Y + dy * (p["gleb"] / 2 - 4)
        ob[f"dystans_{i}"] = walec(3.0, p["dystans"], Matrix.Translation((cx, cy, g.tb + p["dystans"] / 2)), k, f"dystans_{i}", mats["mosiadz"], n=6)
    return ob


def buduj_stopki(g, k, mats):
    s = g.d["stopki"]
    ob = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            ob.append(walec(s["srednica"] / 2, s["wys"], Matrix.Translation((dx * (g.W / 2 - s["odsuniecie"]), dy * (g.D / 2 - s["odsuniecie"]), -s["wys"] / 2)), k, "stopka", mats["guma"]))
    return ob


# ----------------------------------------------------------------------------- kontrole

def aabb_swiat(ob):
    V = [ob.matrix_world @ v.co for v in ob.data.vertices]
    return [min(c[i] for c in V) / MM for i in range(3)], [max(c[i] for c in V) / MM for i in range(3)]


def kontrole(g, przyciski, joystick, plytka, obudowa):
    wynik = {"luzy_mm": {}, "uwagi": []}
    gora_pcb = max(aabb_swiat(o)[1][2] for n, o in plytka.items() if n not in ("antena", "sma"))
    for ob in przyciski + joystick:
        if not ob.name.startswith(("korpus_", "joy_korpus")):
            continue
        mn, mx = aabb_swiat(ob)
        p_mn, p_mx = aabb_swiat(plytka["pcb"])
        nad_pcb = not (mx[0] < p_mn[0] or mn[0] > p_mx[0] or mx[1] < p_mn[1] or mn[1] > p_mx[1])
        luz = mn[2] - (gora_pcb if nad_pcb else g.tb)
        wynik["luzy_mm"][ob.name] = round(luz, 1)
        if luz < 3.0:
            wynik["uwagi"].append(f"{ob.name}: luz {luz:.1f} mm < 3 mm nad {'płytką' if nad_pcb else 'dnem'}")
    # złącza w osi wycięć tylnej ściany
    ty = g.d["tyl"]
    for nazwa, klucz in (("rj45", "rj45"), ("usb_c", "usb_c")):
        mn, mx = aabb_swiat(plytka[nazwa])
        zc = (mn[2] + mx[2]) / 2
        wynik["luzy_mm"][f"{nazwa}_os_z_vs_wyciecie"] = round(zc - ty[klucz]["z"], 1)
        if abs(zc - ty[klucz]["z"]) > 1.0:
            wynik["uwagi"].append(f"{nazwa}: środek {zc:.1f} mm, wycięcie {ty[klucz]['z']} mm")
    wynik["blat_kat_deg"] = round(math.degrees(g.kat), 2)
    wynik["wnetrze_mm"] = [g.W - 2 * g.t, g.D - 2 * g.t]
    return wynik


# ----------------------------------------------------------------------------- render

def scena(args, g):
    sc = bpy.context.scene
    for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = e
            break
        except TypeError:
            continue
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1100
    try:
        sc.eevee.taa_render_samples = args.probki
    except AttributeError:
        pass
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.view_settings.exposure = -0.8
    sw = sc.world or bpy.data.worlds.new("swiat")
    sc.world = sw
    sw.use_nodes = True
    bg = next(n for n in sw.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = hex_lin("#1E2328")
    bg.inputs["Strength"].default_value = 0.35
    k = kolekcja("scena")
    stol = prostopadloscian(1600, 1200, 10, Matrix.Translation((0, 0, -5 - g.d["stopki"]["wys"])), k, "stol", material("stol", "#2E3338", 0.8))
    for nazwa, loc, moc, rozm in (("klucz", (-350, -420, 520), 70, 300), ("wypelnienie", (480, -200, 260), 22, 400), ("kontra", (0, 520, 420), 45, 250)):
        sw_ = bpy.data.lights.new(nazwa, "AREA")
        sw_.energy = moc
        sw_.size = rozm * MM
        o = bpy.data.objects.new(nazwa, sw_)
        o.location = Vector(loc) * MM
        k.objects.link(o)
        kier = (Vector((0, 0, 50)) * MM - o.location).to_track_quat("-Z", "Y")
        o.rotation_euler = kier.to_euler()
    return k, stol


def kamera(k, nazwa, loc, cel=(0, 0, 40), lens=50, ortho=None):
    c = bpy.data.cameras.new(nazwa)
    c.lens = lens
    c.clip_start = 0.01
    if ortho:
        c.type = "ORTHO"
        c.ortho_scale = ortho * MM
    o = bpy.data.objects.new(nazwa, c)
    o.location = Vector(loc) * MM
    o.rotation_euler = (Vector(cel) * MM - o.location).to_track_quat("-Z", "Y").to_euler()
    k.objects.link(o)
    return o


def render(cam, sciezka):
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)
    log("render", os.path.basename(sciezka))


def main():
    args = argumenty()
    d = tomllib.load(open(args.geometria, "rb"))
    g = G(d)
    os.makedirs(args.wyjscie, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = {
        "pleksi": material("pleksi", "#FFFFFF", 0.04, przezr=1.0, ior=1.49),
        "grafika": material("grafika", "#14181C", 0.45),
        "plyta": material("plyta_nosna", "#3A3A3A", 0.7),
        "korpus": material("korpus_przycisku", "#1A1A1A", 0.6),
        "ikona": material("ikona_naklejka", "#FFFFFF", 0.3),
        "czarny": material("czarny", "#111111", 0.45),
        "metal": material("metal", "#B8BEC4", 0.3, metal=1.0),
        "kula": material("kula", "#E0524A", 0.2, powloka=0.8),
        "pcb": material("pcb", "#0E3B2E", 0.4),
        "ekran": material("ekran", "#0A0F14", 0.15),
        "zloto": material("zloto", "#D4A64A", 0.25, metal=1.0),
        "mosiadz": material("mosiadz", "#B08D57", 0.35, metal=1.0),
        "guma": material("guma", "#202020", 0.9),
    }
    # EEVEE nie pokazuje warstw pod materiałem z transmisją (wychodzi czarny), więc pleksi = alfa + powłoka
    pl = next(n for n in mats["pleksi"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    _wejscie(pl, "Transmission Weight", "Transmission").default_value = 0.0
    pl.inputs["Alpha"].default_value = 0.06
    _wejscie(pl, "Coat Weight", "Clearcoat").default_value = 0.0
    mats["pleksi"].use_backface_culling = True
    if hasattr(mats["pleksi"], "use_transparency_overlap"):
        mats["pleksi"].use_transparency_overlap = False
    try:
        mats["pleksi"].surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        mats["pleksi"].blend_method = "BLEND"
    mat_d = material_drewno()
    k_ob = kolekcja("01_obudowa_sklejka")
    k_bl = kolekcja("02_blat_warstwy")
    k_cz = kolekcja("03_czesci_arcade")
    k_pl = kolekcja("04_plytka_esp32")
    k_st = kolekcja("05_stopki")
    obudowa = buduj_obudowe(g, k_ob, mat_d)
    blat = buduj_blat(g, k_bl, args.marka, mats)
    if args.grafika:
        naloz_grafike(g, blat["grafika"][0], os.path.abspath(args.grafika))
    przyciski = buduj_przyciski(g, k_cz, mats)
    joy = buduj_joystick(g, k_cz, mats)
    oled = buduj_oled(g, k_cz, mats)
    plytka = buduj_plytke(g, k_pl, mats)
    stopki = buduj_stopki(g, k_st, mats)
    kon = kontrole(g, przyciski, joy, plytka, obudowa)
    log("kontrole:", json.dumps(kon, ensure_ascii=False))
    json.dump(kon, open(os.path.join(args.wyjscie, "kontrole.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not args.bez_renderu:
        ks, stol = scena(args, g)
        # pleksi (alfa) tylko w widoku rozstrzelonym; w pozostałych jej połysk przejmuje powłoka grafiki
        blat["pleksi"][0].hide_render = bool(args.grafika)
        render(kamera(ks, "kam_34", (-420, -520, 430)), os.path.join(args.wyjscie, "render_34.png"))
        render(kamera(ks, "kam_gora", (0, 0, 900), (0, 0, 0), ortho=420), os.path.join(args.wyjscie, "render_gora.png"))
        render(kamera(ks, "kam_tyl", (380, 560, 260), (20, 0, 30)), os.path.join(args.wyjscie, "render_tyl.png"))
        # przekrój: bez blatu i przedniej ściany, widok do wnętrza
        ukryj = [o for o, *_ in blat.values()] + [obudowa["przod"], obudowa["bok_lewy"]] + oled
        for o in ukryj:
            o.hide_render = True
        render(kamera(ks, "kam_wnetrze", (-380, -420, 380), (20, 30, 20)), os.path.join(args.wyjscie, "render_wnetrze.png"))
        for o in ukryj:
            o.hide_render = False
        # rozstrzelony: warstwy blatu w górę wzdłuż normalnej blatu
        n = (g.T.to_3x3() @ Vector((0, 0, 1))).normalized()
        przes = {"pleksi": 150, "grafika": 105, "plyta_nosna": 60}
        blat["pleksi"][0].hide_render = False
        for nazwa, (o, *_r) in blat.items():
            o.location += n * przes[nazwa] * MM
        for o in przyciski + joy[:3]:
            o.location += n * 190 * MM
        render(kamera(ks, "kam_rozstrz", (-520, -640, 620), (0, 0, 110)), os.path.join(args.wyjscie, "render_rozstrzelony.png"))
        for nazwa, (o, *_r) in blat.items():
            o.location -= n * przes[nazwa] * MM
        for o in przyciski + joy[:3]:
            o.location -= n * 190 * MM
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(args.wyjscie, "pilot_arcade.blend"))
    log("zapisano", args.wyjscie)


if __name__ == "__main__":
    main()
