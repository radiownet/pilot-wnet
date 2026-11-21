# -*- coding: utf-8 -*-
"""Ethernet płytki Rev A: W5500 przez SPI (`network.LAN`, MicroPython quickref ESP32).

Wywołanie jak w quickref: `network.LAN(spi=…, phy_type=network.PHY_W5500, phy_addr=0, cs=Pin(…), int=Pin(…))`;
`reset` pomijamy, bo W5500 ma na płytce tylko reset RC. Szybkość SPI ustala się przy kompilacji
MicroPythona (`MICROPY_PY_NETWORK_LAN_SPI_CLOCK_SPEED_MZ`) — zegar w obiekcie SPI jest ignorowany.

Adres MAC. W5500 nie ma własnego adresu (rejestr SHAR po resecie = 0). `ports/esp32/network_lan.c`
w MicroPythonie v1.29.0 po utworzeniu interfejsu odczytuje MAC ze sterownika i — gdy jest zerowy —
bierze `esp_read_mac(…, ESP_MAC_ETH)`, czyli adres z eFuse ESP32-S3. Dokumentacja ESP-IDF v6.1
(„Miscellaneous System APIs”, MAC Address) podaje dla ESP32-S3 przy 4 adresach uniwersalnych
(ustawienie domyślne): Ethernet = adres bazowy + 3 w ostatnim oktecie; przy 2 adresach — adres lokalny
wyprowadzony z MAC Bluetooth. Własny adres można wymusić polem `eth.mac` (→ `lan.config(mac=…)`).
To, że kompilacja ESP32_GENERIC_S3 v1.29.0 ma włączone `CONFIG_ETH_SPI_ETHERNET_W5500` i 4 adresy
uniwersalne — [DO WERYFIKACJI na płytce: `lan.config('mac')` wobec `esptool read_mac`].

Brak auto-MDIX (karta W5500): kabel prosty do przełącznika; prosto do komputera zadziała tylko, gdy
karta komputera ma auto-MDIX — inaczej kabel skrzyżowany (R3 rozdz. 4.4).

Adres IP: `statyczny` z konfiguracji albo `dhcp`; gdy DHCP nie odpowie w `dhcp_czekaj_ms`, a
`link_local` = true, pilot bierze adres 169.254.x.y wyprowadzony z MAC (RFC 3927, zakres
169.254.1.0–169.254.254.255). Uproszczenie: bez sondy ARP wykrywającej konflikt adresów.
"""

import konfig_plytki as K

MASKA_LINK_LOCAL = "255.255.0.0"


def mac_z_tekstu(tekst):
    """"02:12:34:56:78:9a" → 6 bajtów; None dla pustego. Rzuca ValueError dla błędnego."""
    if not tekst:
        return None
    czesci = tekst.replace("-", ":").split(":")
    if len(czesci) != 6:
        raise ValueError("MAC musi mieć 6 oktetów")
    b = bytes(int(c, 16) for c in czesci)
    if b[0] & 0x01:
        raise ValueError("MAC grupowy (bit I/G) jest niedozwolony")
    return b


def adres_link_local(mac):
    """169.254.x.y z dwóch ostatnich oktetów MAC; x w 1–254 (RFC 3927 rozdz. 2.1)."""
    x = 1 + (mac[4] % 254)
    y = mac[5]
    return "169.254.%d.%d" % (x, y)


def utworz(konf_eth=None):
    """Tworzy i włącza interfejs W5500. Zwraca obiekt `network.LAN`."""
    import machine
    import network
    konf_eth = konf_eth or {}
    Pin = machine.Pin
    spi = machine.SPI(K.ETH_SPI_ID, sck=Pin(K.ETH_SCLK), mosi=Pin(K.ETH_MOSI), miso=Pin(K.ETH_MISO))
    lan = network.LAN(spi=spi, phy_type=network.PHY_W5500, phy_addr=K.ETH_PHY_ADDR,
                      cs=Pin(K.ETH_CS), int=Pin(K.ETH_INT))
    mac = mac_z_tekstu(konf_eth.get("mac", ""))
    if mac is not None:
        lan.config(mac=mac)
    lan.active(True)
    if konf_eth.get("tryb") == "statyczny":
        ustaw_statyczny(lan, konf_eth["adres"], konf_eth.get("maska") or "255.255.255.0",
                        konf_eth.get("brama") or "0.0.0.0", konf_eth.get("dns") or "0.0.0.0")
    return lan


def ustaw_statyczny(lan, adres, maska, brama="0.0.0.0", dns="0.0.0.0"):
    """`ifconfig` (starsze API, w v1.29.0 nadal dostępne [DO WERYFIKACJI]) albo `ipconfig`.
    Ustawienie adresu statycznego zatrzymuje klienta DHCP."""
    if hasattr(lan, "ifconfig"):
        lan.ifconfig((adres, maska, brama, dns))
    else:
        dl = sum(bin(int(o)).count("1") for o in maska.split("."))
        lan.ipconfig(addr4="%s/%d" % (adres, dl), gw4=brama)


def adres(lan):
    try:
        return lan.ifconfig()[0]
    except AttributeError:
        return lan.ipconfig("addr4")[0]


def zastosuj_link_local(lan):
    mac = lan.config("mac")
    a = adres_link_local(mac)
    ustaw_statyczny(lan, a, MASKA_LINK_LOCAL)
    return a


def po_czasie_dhcp(lan, konf_eth):
    """Wywoływane, gdy minął czas na DHCP. Zwraca adres albo None."""
    if lan.isconnected():
        return adres(lan)
    if konf_eth.get("link_local", True):
        return zastosuj_link_local(lan)
    return None


async def czekaj_na_adres(lan, konf_eth, krok_ms=100):
    """Asynchronicznie: adres IP interfejsu (DHCP, statyczny albo link-local) albo None."""
    import asyncio
    if konf_eth.get("tryb") == "statyczny":
        return adres(lan)
    czekaj = int(konf_eth.get("dhcp_czekaj_ms", 8000))
    t = 0
    while t < czekaj:
        if lan.isconnected():
            return adres(lan)
        await asyncio.sleep_ms(krok_ms)
        t += krok_ms
    a = po_czasie_dhcp(lan, konf_eth)
    if a is None:
        print("pilot_eth: brak adresu — sprawdź kabel (W5500 nie ma auto-MDIX) i serwer DHCP")
    return a
