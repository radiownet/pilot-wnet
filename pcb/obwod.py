# -*- coding: utf-8 -*-
"""Pilot Wnet — płytka Rev A: opis obwodu w kodzie (SKiDL 3.0, KiCad 10). Źródło prawdy schematu.

Uruchamiane w Pythonie KiCada (venv z pcbnew) — patrz pcb/README.md:
    python obwod.py --wyjscie kicad
Wynik: pilot_wnet.net (lista połączeń KiCada) i bom_obwod.csv; schemat rysuje schemat.py.

Architektura i przydział pinów: research/R3_architektura_elektroniki.md (Rev A, piny zgodne z LilyGO
T-ETH-Elite, żeby Meshtastic i MeshCore budowały się z niewielkiej różnicy wariantu). Wartości elementów
i numery LCSC: CZESCI niżej; każda pozycja z karty producenta albo z biblioteki JLCPCB (źródła w
pcb/README.md). Pozycje z dopiskiem DNP są na płytce, ale fabryka ich nie montuje.
"""
import argparse
import csv
import os
import re
import sys

from skidl import KICAD10, POWER, Net, Part, generate_netlist, lib_search_paths, set_default_tool, footprint_search_paths

TU = os.path.dirname(os.path.abspath(__file__))
KICAD_SYM = os.environ.get("KICAD10_SYMBOL_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
KICAD_FP = os.environ.get("KICAD10_FOOTPRINT_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

# --------------------------------------------------------------------------- części (jedna tabela)
# klucz: (wartość, footprint KiCada, numer LCSC/JLCPCB, uwaga)
F0402R = "Resistor_SMD:R_0402_1005Metric"
F0402C = "Capacitor_SMD:C_0402_1005Metric"
F0603C = "Capacitor_SMD:C_0603_1608Metric"
F0805C = "Capacitor_SMD:C_0805_2012Metric"
CZESCI = {
    # rezystory 0402 1 % (UNI-ROYAL; numery i typy z biblioteki JLCPCB, odczyt 18.10.2026)
    "R0": ("0", F0402R, "C17168", ""),
    "R10": ("10 1%", F0402R, "C25077", "TCT gniazda RJ45 (referencja WIZnet)"),
    "R22": ("22", F0402R, "C25092", "szeregowe USB przy module (HDG Espressif)"),
    "R49R9": ("49.9 1%", F0402R, "C25120", ""),
    "R200": ("200", F0402R, "C25087", ""),
    "R330": ("330", F0402R, "C25104", ""),
    "R1K": ("1k", F0402R, "C11702", ""),
    "R4K7": ("4.7k", F0402R, "C25900", ""),
    "R5K1": ("5.1k", F0402R, "C25905", ""),
    "R10K": ("10k", F0402R, "C25744", ""),
    "R12K4": ("12.4k 1%", F0402R, "C11692", "EXRES1 W5500"),
    "R22K": ("22k 1%", F0402R, "C25768", "dzielnik FB: 0,6 × (1 + 100/22) = 3,327 V"),
    "R100K": ("100k", F0402R, "C25741", ""),
    "R1M": ("1M", F0402R, "C26083", "równolegle do kwarcu W5500"),
    # kondensatory
    "C6P8": ("6.8pF C0G", F0402C, "C237286", "feed-forward TLV62569 (opcja)"),
    "C18P": ("18pF C0G", F0402C, "C1549", ""),
    "C10N": ("10nF", F0402C, "C15195", ""),
    "C6N8": ("6.8nF", F0402C, "C318580", "sprzężenie RX Ethernet"),
    "C22N": ("22nF", F0402C, "C1532", "TCT Ethernet"),
    "C100N": ("100nF", F0402C, "C1525", ""),
    "C1U": ("1uF", F0402C, "C52923", ""),
    "C4U7": ("4.7uF", F0603C, "C19666", "TOCAP W5500"),
    "C10U": ("10uF 25V", F0805C, "C15850", ""),
    "C22U": ("22uF 25V", F0805C, "C45783", ""),
    "C1N2KV": ("1nF 2kV", "Capacitor_SMD:C_1808_4520Metric", "C76916", "ekran RJ45 -> GND"),
    "FB600": ("600R@100MHz 1.3A", "Inductor_SMD:L_0603_1608Metric", "C85833", "Murata BLM18KG601SN1D, 3V3 -> 3V3A"),
    # półprzewodniki i moduły
    "ESP32": ("ESP32-S3-WROOM-1-N16R8", "pilot_jlc:ESP32-S3-WROOM-1_Pilot", "C2913202", "antena PCB przy tylnej krawędzi (DECYZJE D3)"),
    "W5500": ("W5500", "Package_QFP:LQFP-48_7x7mm_P0.5mm", "C32843", ""),
    "XTAL25": ("25MHz CL18pF", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "C70593", "YXC X322525MRB4SI, CL = 18 pF jak w karcie W5500"),
    "RJ45": ("HR911105A", "Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal", "C12074", "THT"),
    "E22": ("E22-900M22S", "pilot_jlc:WIRELM-SMD_E22-900M22S", "C411293", "SX1262 868 MHz, TCXO; stan w JLCPCB niski"),
    "INV": ("74LVC1G04GW", "Package_TO_SOT_SMD:SOT-353_SC-70-5", "C10237", "RXEN = NOT DIO2"),
    "UFL": ("U.FL-R-SMT-1(10)", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", "C88373", "antena LoRa 868 MHz"),
    "BUCK": ("TLV62569DBVR", "Package_TO_SOT_SMD:SOT-23-5", "C141836", "5 V -> 3,3 V, 2 A"),
    "L2U2": ("2.2uH", "Inductor_SMD:L_Changjiang_FNR4030S", "C167869", "FNR4030S2R2MT: Isat 5,8 A (LCSC 19.11; było C167219 = 3,3 uH 7x6,6 mm)"),
    "USBC": ("TYPE-C-31-M-12", "pilot_jlc:USB_C_Receptacle_HRO_TYPE-C-31-M-12_Pilot", "C165948", ""),
    "USBLC6": ("USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "C7519", ""),
    "TVS5": ("SMF5.0A", "Diode_SMD:D_SMF", "C151296", "jednokierunkowy"),
    "PTC": ("1.1A hold", "Fuse:Fuse_1206_3216Metric", "C126818", "Littelfuse 1206L110THYR: 1,1 A hold, 2,2 A trip, 8 V (LCSC 19.11; było C70069 = 250 mA)"),
    "PCA": ("PCA9685PW", "Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm", "C2678753", "PWM diod przycisków"),
    "NFET": ("AO3400A", "Package_TO_SOT_SMD:SOT-23", "C20917", ""),
    "ESD4": ("SRV05-4", "Package_TO_SOT_SMD:SOT-23-6", "C13612", ""),
    "LEDG": ("zielona", "LED_SMD:LED_0603_1608Metric", "C12065", ""),  # 20.11: C72043 bez stanu w JLC/LCSC
    "SW": ("TS-1187A-B-A-B", "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", "C318884", ""),
    "XH4": ("B4B-XH-A", "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C144395", "THT"),
    "XH5": ("B5B-XH-A", "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical", "C157991", "THT"),
    "SH4": ("SM04B-SRSS-TB", "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal", "C160404", "Qwiic"),
    "PIN6": ("1x6 2.54", "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C37208", "THT"),
}
# elementy rysowane w schemacie, ale niemontowane przez fabrykę (DNP)
DNP = set()


def nazwij(pin, nazwa):
    """Sieć z nazwą zamiast automatycznej N$… (czytelny schemat i płytka)."""
    n = Net(nazwa)
    n += pin
    return n


class Fabryka:
    """Tworzy części z tabeli CZESCI z polami LCSC i opisem, liczy BOM."""

    def __init__(self):
        self.lista = []

    def part(self, lib, sym, klucz, ref, dnp=False, **kw):
        wartosc, fp, lcsc, uwaga = CZESCI[klucz]
        p = Part(lib, sym, value=wartosc, footprint=fp, ref=ref, tag=ref, **kw)
        p.fields["LCSC"] = lcsc
        if dnp:
            p.fields["DNP"] = "1"
            DNP.add(ref)
        self.lista.append((ref, klucz, dnp))
        return p

    def R(self, klucz, ref, a, b, dnp=False):
        r = self.part("Device", "R", klucz, ref, dnp)
        r[1] += a
        r[2] += b
        return r

    def C(self, klucz, ref, a, b, dnp=False):
        c = self.part("Device", "C", klucz, ref, dnp)
        c[1] += a
        c[2] += b
        return c


def buduj():
    f = Fabryka()
    GND, V5, V3 = Net("GND"), Net("+5V"), Net("+3V3")
    VBUS_C = Net("VBUS_C")
    for n in (GND, V5, V3):
        n.drive = POWER

    # ------------------------------------------------------------------- USB-C, ochrona, 5 V
    j1 = f.part("Connector", "USB_C_Receptacle_USB2.0_16P", "USBC", "J1")
    j1["VBUS"] += VBUS_C
    j1["GND"] += GND
    j1["SHIELD"] += GND
    f.R("R5K1", "R1", nazwij(j1["CC1"], "USB_CC1"), GND)
    f.R("R5K1", "R2", nazwij(j1["CC2"], "USB_CC2"), GND)
    usb_dp, usb_dm = Net("USB_D+"), Net("USB_D-")
    j1["D+"] += usb_dp
    j1["D-"] += usb_dm
    ptc = f.part("Device", "Polyfuse", "PTC", "F1")
    ptc[1] += VBUS_C
    ptc[2] += V5
    d1 = f.part("Device", "D_Zener", "TVS5", "D1")   # symbol jednokierunkowy (K/A); D_TVS w KiCadzie jest dwukierunkowy
    d1["K"] += V5
    d1["A"] += GND
    u2 = f.part("Power_Protection", "USBLC6-2SC6", "USBLC6", "U2")
    u2[1] += usb_dm  # I/O1 (piny 1 i 6 to jedna linia)
    u2[6] += usb_dm
    u2[3] += usb_dp  # I/O2 (piny 3 i 4)
    u2[4] += usb_dp
    u2["VBUS"] += V5
    u2["GND"] += GND

    # ------------------------------------------------------------------- 3,3 V (TLV62569, VFB = 0,6 V)
    u3 = f.part("Regulator_Switching", "TLV62569DBV", "BUCK", "U3")
    sw, fb = Net("BUCK_SW"), Net("BUCK_FB")
    u3["VIN"] += V5
    u3["EN"] += V5
    u3["GND"] += GND
    u3["SW"] += sw
    u3["FB"] += fb
    l1 = f.part("Device", "L", "L2U2", "L1")
    l1[1] += sw
    l1[2] += V3
    # TI SLVSDG1C: CIN 4,7–10 µF, COUT 10–47 µF (łącznie z odsprzęganiem modułów na szynie), L 2,2 µH
    f.C("C10U", "C1", V5, GND)
    f.C("C100N", "C2", V5, GND)
    f.C("C22U", "C3", V3, GND)
    f.R("R100K", "R3", V3, fb)    # Vout = 0,6 × (1 + 100k/22k) = 3,327 V (obliczenie)
    f.R("R22K", "R4", fb, GND)
    f.C("C6P8", "C4", V3, fb, dnp=True)   # feed-forward wg TI „optional”

    # ------------------------------------------------------------------- ESP32-S3-WROOM-1U-N16R8
    u1 = f.part("RF_Module", "ESP32-S3-WROOM-1", "ESP32", "U1")
    u1["3V3"] += V3
    u1["GND"] += GND
    f.C("C22U", "C5", V3, GND)
    f.C("C100N", "C6", V3, GND)
    en = Net("ESP_EN")
    u1["EN"] += en
    f.R("R10K", "R5", V3, en)
    f.C("C1U", "C7", en, GND)
    sw_rst = f.part("Switch", "SW_Push", "SW", "SW1")
    sw_rst[1] += en
    sw_rst[2] += GND
    # USB: 22 Ω szeregowo i miejsca na kondensatory (DNP) przy module (ESP32-S3 HDG)
    m_dm, m_dp = Net("USB_D-_M"), Net("USB_D+_M")
    f.R("R22", "R6", usb_dm, m_dm)
    f.R("R22", "R7", usb_dp, m_dp)
    f.C("C18P", "C8", m_dm, GND, dnp=True)
    f.C("C18P", "C9", m_dp, GND, dnp=True)
    u1["USB_D-"] += m_dm
    u1["USB_D+"] += m_dp
    io = lambda n: u1[f"IO{n}"]

    # ------------------------------------------------------------------- wejścia: 6 przycisków + 4 kierunki
    # GPIO wg R3 §6.2; złącze → ESD → 1 kΩ → GPIO z podciąganiem 10 kΩ i 10 nF
    # START na GPIO42, nie GPIO0 (DECYZJE D9)
    WEJSCIA = [("START", 42), ("STOP", 3), ("JOY_UP", 4), ("JOY_DOWN", 5), ("JOY_LEFT", 6), ("JOY_RIGHT", 7),
               ("SPRAWDZ", 12), ("WYSLIJ", 15), ("PLAY", 39), ("REC", 41)]
    zl = {}
    for i, (nazwa, g) in enumerate(WEJSCIA):
        n_zl, n_gp = Net(f"IN_{nazwa}"), Net(f"BTN_{nazwa}")
        n_gp += io(g)
        f.R("R1K", f"R{10 + i}", n_zl, n_gp)
        f.R("R10K", f"R{20 + i}", V3, n_gp)
        f.C("C10N", f"C{10 + i}", n_gp, GND)
        zl[nazwa] = n_zl
    sw_boot = f.part("Switch", "SW_Push", "SW", "SW2")   # BOOT = GPIO0, tylko przycisk na płytce
    sw_boot[1] += nazwij(io(0), "ESP_IO0_BOOT")
    f.R("R10K", "R9", V3, io(0))
    sw_boot[2] += GND
    # ESD przy złączach: 3 × SRV05-4 = 12 kanałów (10 wejść + SDA/SCL)
    sda, scl = Net("I2C_SDA"), Net("I2C_SCL")
    kanaly = [zl[n] for n, _ in WEJSCIA] + [sda, scl]
    for k in range(3):
        u = f.part("Power_Protection", "SRV05-4", "ESD4", f"U{10 + k}")
        u["VP"] += V3
        u["VN"] += GND
        for j, pin in enumerate(("IO1", "IO2", "IO3", "IO4")):
            u[pin] += kanaly[4 * k + j]

    # ------------------------------------------------------------------- podświetlenie: PCA9685 + 6 × AO3400A
    sda += io(17)
    scl += io(18)
    f.R("R4K7", "R30", V3, sda)
    f.R("R4K7", "R31", V3, scl)
    u5 = f.part("Driver_LED", "PCA9685PW", "PCA", "U5", dnp=True)   # tor LED bez montażu (DECYZJE D1)
    u5["VDD"] += V3
    u5["VSS"] += GND
    f.C("C100N", "C20", V3, GND, dnp=True)
    for a in ("A0", "A1", "A2", "A3", "A4", "A5", "~{OE}", "EXTCLK"):
        u5[a] += GND        # adres 0x40, wyjścia włączone, zegar wewnętrzny
    u5["SDA"] += sda
    u5["SCL"] += scl
    PRZYCISKI = ["REC", "PLAY", "WYSLIJ", "SPRAWDZ", "START", "STOP"]
    led_k = {}
    for i, nazwa in enumerate(PRZYCISKI):
        g, k = Net(f"LED_{nazwa}_G"), Net(f"LED_{nazwa}_K")
        u5[f"LED{i}"] += g
        q = f.part("Transistor_FET", "AO3400A", "NFET", f"Q{1 + i}", dnp=True)
        q["G"] += g
        q["S"] += GND
        q["D"] += k
        f.R("R100K", f"R{40 + i}", g, GND, dnp=True)   # diody wyłączone, gdy PCA9685 milczy (np. firmware mesh)
        led_k[nazwa] = k

    # ------------------------------------------------------------------- złącza przycisków i joysticka (JST XH)
    for i, nazwa in enumerate(PRZYCISKI):
        j = f.part("Connector_Generic", "Conn_01x04", "XH4", f"J{10 + i}")
        j[1] += zl[nazwa]
        j[2] += GND
        j[3] += V5          # LED+ (diody 5 V w przyciskach — R2)
        j[4] += led_k[nazwa]
    jj = f.part("Connector_Generic", "Conn_01x05", "XH5", "J16")
    jj[1] += GND            # pinout wiązki Sanwa JLF-H: 1 GND, 2 góra, 3 dół, 4 lewo, 5 prawo (R2)
    jj[2] += zl["JOY_UP"]
    jj[3] += zl["JOY_DOWN"]
    jj[4] += zl["JOY_LEFT"]
    jj[5] += zl["JOY_RIGHT"]

    # ------------------------------------------------------------------- OLED i rozszerzenia (Qwiic, nagłówki)
    for ref in ("J17", "J18"):       # J17 = OLED, J18 = czujniki aplikacji MicroPython
        q = f.part("Connector_Generic", "Conn_01x04", "SH4", ref)
        q[1] += GND
        q[2] += V3
        q[3] += sda
        q[4] += scl
    exp13 = Net("EXP_IO13")
    exp13 += io(13)
    je = f.part("Connector_Generic", "Conn_01x06", "PIN6", "J19")
    for k, n in enumerate((V3, GND, sda, scl, exp13, V5), 1):
        je[k] += n
    txd, rxd = Net("UART0_TX"), Net("UART0_RX")
    u1["TXD0"] += txd
    u1["RXD0"] += rxd
    js = f.part("Connector_Generic", "Conn_01x06", "PIN6", "J20")   # serwis: ratunek, gdy firmware wyłączy USB
    for k, n in enumerate((GND, V3, en, io(0), txd, rxd), 1):
        js[k] += n
    led = Net("LED_STATUS")
    led += io(38)
    led_a = Net("LED_STATUS_A")
    f.R("R1K", "R50", led, led_a)
    dl = f.part("Device", "LED", "LEDG", "D2")
    dl["A"] += led_a
    dl["K"] += GND
    vs = Net("VSYS_SENSE")             # 5 V / 2 na ADC1_CH0
    vs += io(1)
    f.R("R100K", "R51", V5, vs)
    f.R("R100K", "R52", vs, GND)
    f.C("C100N", "C21", vs, GND)                 # filtr wejścia ADC (HDG)

    # ------------------------------------------------------------------- Ethernet: W5500 + HR911105A
    # Topologia z referencji WIZnet dla gniazda z transformatorem (w5500_sch_v110_use_mag) i WIZ850io V1.1,
    # piny gniazda z karty HanRun HR911105A (C12074) — wyciąg w pcb/README.md.
    u4 = f.part("Interface_Ethernet", "W5500", "W5500", "U4")
    eth = {"~{SCS}": ("ETH_CS", 45), "SCLK": ("ETH_SCLK", 48), "MISO": ("ETH_MISO", 47),
           "MOSI": ("ETH_MOSI", 21), "~{INT}": ("ETH_INT", 14)}
    en_eth = {}
    for pin, (siec, g) in eth.items():
        n = Net(siec)
        u4[pin] += n
        n += io(g)
        en_eth[siec] = n
    f.R("R4K7", "R68", V3, en_eth["ETH_CS"])      # CS w stanie wysokim przy resecie (GPIO45 ma słabe ściąganie)
    f.R("R4K7", "R69", V3, en_eth["ETH_INT"])
    v3a = Net("+3V3A")
    v3a.drive = POWER
    fb1 = f.part("Device", "FerriteBead_Small", "FB600", "FB1")
    fb1[1] += V3
    fb1[2] += v3a
    u4["VDD"] += V3
    u4["AVDD"] += v3a
    u4["GND"] += GND
    u4["AGND"] += GND
    u4["RSVD"] += GND                               # pin 23 „must be tied to GND”, 38–42 jak w WIZ850io
    for i in range(6):
        f.C("C100N", f"C{30 + i}", v3a, GND)          # po jednym przy każdym AVDD (4, 8, 11, 15, 17, 21)
    f.C("C10U", "C36", v3a, GND)
    f.C("C100N", "C44", V3, GND)                    # VDD (pin 28): 100 nF + 10 µF
    f.C("C10U", "C45", V3, GND)
    f.R("R12K4", "R60", nazwij(u4["EXRES1"], "ETH_EXRES1"), GND)
    f.C("C10N", "C37", nazwij(u4["1V2O"], "ETH_1V2O"), GND)
    f.C("C4U7", "C38", nazwij(u4["TOCAP"], "ETH_TOCAP"), GND)
    rst = Net("ETH_RST")
    u4["~{RST}"] += rst
    f.R("R10K", "R61", V3, rst)
    f.C("C1U", "C39", rst, GND)                     # reset przy włączeniu: ok. 5–7 ms niskiego (wymagane ≥ 500 µs)
    for pm in ("PMODE0", "PMODE1", "PMODE2"):
        u4[pm] += V3                                # 111 = auto-negocjacja, wszystkie tryby
    xi, xo, xo2 = Net("ETH_XI"), Net("ETH_XO"), Net("ETH_XO_Y")
    u4["XI/CLKIN"] += xi
    u4["XO"] += xo
    y1 = f.part("Device", "Crystal_GND24", "XTAL25", "Y1")
    y1[1] += xi
    y1[3] += xo2
    y1["G"] += GND
    f.R("R1M", "R59", xi, xo)                       # karta W5500 rys. 3: 1 MΩ i 0 Ω szeregowo na XO
    f.R("R0", "R58", xo, xo2)
    f.C("C18P", "C40", xi, GND)
    f.C("C18P", "C41", xo2, GND)
    j2 = f.part("Connector", "RJ45_Hanrun_HR911105A_Horizontal", "RJ45", "J2")
    # TX: tłumiące 0 Ω, terminacja 2 × 49,9 Ω do 3V3A, odczep TCT 10 Ω z 3V3A i 22 nF do masy
    td_p, td_n, tct = Net("ETH_TD+"), Net("ETH_TD-"), Net("ETH_TCT")
    f.R("R0", "R62", nazwij(u4["TXP"], "ETH_TXP_U"), td_p)
    f.R("R0", "R63", nazwij(u4["TXN"], "ETH_TXN_U"), td_n)
    f.R("R49R9", "R64", td_p, v3a)
    f.R("R49R9", "R65", td_n, v3a)
    j2["TD+"] += td_p
    j2["TD-"] += td_n
    j2["TCT"] += tct
    f.R("R10", "R57", v3a, tct)
    f.C("C22N", "C42", tct, GND)
    # RX: tłumiące 0 Ω, 2 × 49,9 Ω do punktu środkowego (= RCT gniazda) z 10 nF do masy, 6,8 nF do RD±
    rx_p, rx_n, rx_mid = Net("ETH_RXP"), Net("ETH_RXN"), Net("ETH_RX_MID")
    f.R("R0", "R56", nazwij(u4["RXP"], "ETH_RXP_U"), rx_p)
    f.R("R0", "R55", nazwij(u4["RXN"], "ETH_RXN_U"), rx_n)
    f.R("R49R9", "R54", rx_p, rx_mid)
    f.R("R49R9", "R53", rx_n, rx_mid)
    f.C("C10N", "C43", rx_mid, GND)
    j2["RCT"] += rx_mid
    rd_p, rd_n = Net("ETH_RD+"), Net("ETH_RD-")
    f.C("C6N8", "C46", rx_p, rd_p)
    f.C("C6N8", "C47", rx_n, rd_n)
    j2["RD+"] += rd_p
    j2["RD-"] += rd_n
    # masa gniazda: pin 8 (CHS GND) do masy płytki; ekran na wyspę CH_GND, 1 nF / 2 kV do masy, 0 Ω DNP do testów EMC
    j2[8] += GND
    chgnd = Net("CH_GND")
    j2["SH"] += chgnd
    f.C("C1N2KV", "C48", chgnd, GND)
    f.R("R0", "R82", chgnd, GND, dnp=True)
    # diody gniazda (aktywne niskim): zielona 9→10 = LINK, żółta 12→11 = ACT; anody do 3V3, katody przez 330 Ω
    link, act = Net("ETH_LINKLED"), Net("ETH_ACTLED")
    u4["LINKLED"] += link
    u4["ACTLED"] += act
    k_link, k_act = Net("ETH_LED_LINK_K"), Net("ETH_LED_ACT_K")
    j2[9] += V3
    j2[10] += k_link
    j2[12] += V3
    j2[11] += k_act
    f.R("R330", "R66", k_link, link)
    f.R("R330", "R67", k_act, act)

    # ------------------------------------------------------------------- LoRa: E22-900M22S (SX1262, TCXO przez DIO3)
    u6 = f.part("pilot_jlc", "E22-900M22S", "E22", "U6", dnp=True)   # lutowany ręcznie (DECYZJE D4)
    # zasilanie radia przez koralik ferrytowy (Ebyte AN2023005: tętnienia przetwornicy pogarszają odbiór)
    v3rf = Net("+3V3_RF")
    v3rf.drive = POWER
    fb2 = f.part("Device", "FerriteBead_Small", "FB600", "FB2")
    fb2[1] += V3
    fb2[2] += v3rf
    u6["VCC"] += v3rf
    u6["GND"] += GND
    f.C("C10U", "C50", v3rf, GND)
    f.C("C100N", "C51", v3rf, GND)
    lora = [("NSS", "LORA_NSS", 40), ("SCK", "LORA_SCK", 10), ("MOSI", "LORA_MOSI", 11), ("MISO", "LORA_MISO", 9),
            ("BUSY", "LORA_BUSY", 16), ("DIO1", "LORA_DIO1", 8)]
    for i, (pin, siec, g) in enumerate(lora):
        a, b = Net(siec), Net(siec + "_M")
        u6[pin] += a
        f.R("R200", f"R{70 + i}", a, b)             # 200 Ω ochronne wg karty Ebyte (R3 §5.2)
        b += io(g)
    nrst = Net("LORA_NRST")
    u6["NRST"] += nrst
    f.R("R0", "R76", nrst, nazwij(io(2), "LORA_NRST_M"))   # Rev A: NRESET na GPIO2 (R3 §6.4)
    io46 = nazwij(io(46), "ESP_IO46")
    f.R("R0", "R77", nrst, io46, dnp=True)          # zgodność binarna z T-ETH-Elite (GPIO46)
    f.R("R10K", "R78", io46, GND)                   # GPIO46 = 0 przy rozruchu
    dio2, rxen = Net("LORA_DIO2"), Net("LORA_RXEN")
    u6["DIO2"] += dio2
    u6["TXEN"] += dio2                              # sposób 1: DIO2 → TXEN, NOT DIO2 → RXEN
    u7 = f.part("74xGxx", "74LVC1G04", "INV", "U7")
    u7["VCC"] += V3
    u7["GND"] += GND
    u7[2] += dio2
    rx_inv = Net("LORA_RXEN_INV")
    u7[4] += rx_inv
    f.C("C100N", "C52", V3, GND)
    f.R("R0", "R79", rx_inv, rxen)
    f.R("R0", "R80", exp13, rxen, dnp=True)         # tryb oszczędny: RXEN z GPIO13 (wtedy bez R79)
    u6["RXEN"] += rxen
    # Antena przez złącze IPEX na module (pigtail → SMA na ściance, DECYZJE D7). Pad ANT (pin 21) bez połączenia:
    # na 2 warstwach JLCPCB nie kontroluje impedancji, a moduł ma własne złącze (wyciąg z karty Ebyte w README).
    return f


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--wyjscie", required=True)
    a.add_argument("--bez-schematu", action="store_true", help="(zgodność wstecz; schemat robi schemat.py)")
    arg = a.parse_args()
    set_default_tool(KICAD10)
    lib_search_paths[KICAD10] += [KICAD_SYM, os.path.join(TU, "lib")]
    footprint_search_paths[KICAD10] += [KICAD_FP, os.path.join(TU, "lib")]
    os.makedirs(arg.wyjscie, exist_ok=True)
    f = buduj()
    generate_netlist(file_=os.path.join(arg.wyjscie, "pilot_wnet.net"))
    with open(os.path.join(arg.wyjscie, "bom_obwod.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ref", "wartosc", "footprint", "lcsc", "dnp", "uwaga"])
        for ref, klucz, dnp in sorted(f.lista, key=lambda t: (t[0].rstrip("0123456789"), int("".join(c for c in t[0] if c.isdigit()) or 0))):
            wartosc, fp, lcsc, uwaga = CZESCI[klucz]
            w.writerow([ref, wartosc, fp, lcsc, "1" if dnp else "", uwaga])
    # schemat: pcb/schemat.py (z listy połączeń, bez przewodów) — schematizer 0.2.0 zwierał sieci (ERC 18.10.2026)
    print("OK", len(f.lista), "części")


if __name__ == "__main__":
    main()
