# -*- coding: utf-8 -*-
"""Skrypt PlatformIO (pre) dla środowiska PilotWnet_sx1262_repeater: przerywa budowę, gdy zmienna
PILOT_MC_ADMIN_HASLO jest pusta albo nieustawiona — inaczej przekaźnik dostałby puste hasło administratora.
Wartości hasła nie wypisuje. Umieszczenie: <MeshCore>/variants/pilot_wnet/wymagaj_hasla.py.
"""
import os

Import("env")  # noqa: F821 — funkcja SCons wstrzykiwana przez PlatformIO

if not os.environ.get("PILOT_MC_ADMIN_HASLO", "").strip():
    print("pilot_wnet: brak PILOT_MC_ADMIN_HASLO — przekaźnik MeshCore nie zostanie zbudowany z pustym hasłem")
    env.Exit(1)  # noqa: F821
