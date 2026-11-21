# -*- coding: utf-8 -*-
"""main.py — pętla pilota (lib/pilot_aplikacja.py). W trybie serwisowym z boot.py nie startuje.

Flaga trybu serwisowego żyje w module `pilot_konfig` (moduły zaimportowane w boot.py zostają w
sys.modules). Nie importujemy `boot` — to wykonałoby boot.py drugi raz i ponownie zestawiło USB.
Przerwanie: Ctrl-C w REPL (mpremote) zatrzymuje pętlę asyncio; przy włączonym watchdogu
(`watchdog_ms` > 0) płytka zrestartuje się po jego czasie.
"""

import pilot_konfig

if pilot_konfig.TRYB_SERWISOWY:
    print("main: tryb serwisowy — pętla pilota nie startuje")
else:
    import pilot_aplikacja
    pilot_aplikacja.start()
