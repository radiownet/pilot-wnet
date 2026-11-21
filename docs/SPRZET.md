# Pilot Wnet — fizyczny pilot arcade (sprzęt)

To repozytorium to wersja sprzętowa Pilota Wnet: drewniana obudowa w stylu automatu do gier (arcade cabinet / bartop), profesjonalny joystick i przyciski arcade, własna płytka z mikrokontrolerem ESP32‑S3, łączność z komputerem studyjnym przez Bluetooth LE, Wi‑Fi i Ethernet, uruchamianie aplikacji w MicroPythonie oraz rola węzła sieci LoRa 868 MHz (Meshtastic, MeshCore).

Panel ekranowy aplikacji na komputer studyjny i pilot fizyczny dają te same zdarzenia: oba źródła trafiają do tej samej maski przełączników, a ramka pilota jest opisana w [ESP32_PROTOKOL.md](ESP32_PROTOKOL.md). Implementacja hosta (aplikacja na komputer studyjny) nie jest (jeszcze) publiczna.

## Mapa repozytorium

| Katalog / plik | Co zawiera | Jak odtworzyć |
|---|---|---|
| [`research/`](../research/) | raporty R1–R3 i R5: fabryki i promocje, części arcade, architektura elektroniki, krytyka luk (R4 o narzędziach EDA to raport wewnętrzny, niepublikowany) | — (źródła z datą sprawdzenia) |
| [`projekt/arcade.toml`](../projekt/arcade.toml) | jedno źródło wymiarów obudowy, blatu, części i płytki | edycja ręczna |
| [`projekt/arkusze_ciecia.py`](../projekt/arkusze_ciecia.py) | rysunki SVG do cięcia laserowego/CNC (sklejka, pleksi, płyta nośna) | `python -I -B -X utf8 arkusze_ciecia.py --geometria arcade.toml --wyjscie <katalog>` |
| [`blender/generuj_arcade.py`](../blender/generuj_arcade.py) | model 3D i wizualizacje (tryb wsadowy Blendera, bez MCP) | `blender -b --factory-startup --python generuj_arcade.py -- --geometria ..\projekt\arcade.toml --wyjscie <katalog>` |
| [`firmware/micropython/`](../firmware/micropython/) | firmware pilota w MicroPythonie: ramka, wejścia, planista, transporty | testy: zob. niżej |
| [`pcb/`](../pcb/) | projekt płytki (schemat, płytka, DRC, pliki produkcyjne) | patrz [`pcb/README.md`](../pcb/README.md) |
| [`zamowienie/`](../zamowienie/) | instrukcja zamówienia w fabryce (pakiet plików generują skrypty z `pcb/v01/`, poza repozytorium) | patrz [`zamowienie/README.md`](../zamowienie/README.md) |

Wyniki generatorów (rendery, SVG, pliki .blend) trafiają do katalogu podanego w `--wyjscie`, poza repozytorium. Generator naklejek (`branding/`) nie jest częścią tego repozytorium.

Testy firmware uruchamia się plik po pliku, z katalogu `firmware/micropython`:

```bat
for %f in (testy\test_*.py) do python -I -B -X utf8 %f
```

```bash
for t in testy/test_*.py; do python -I -B -X utf8 "$t" || echo "BŁĄD: $t"; done
```

## Zasady

- Wymiary części kupnych (Sanwa, Seimitsu, moduły radiowe, złącza) tylko z kart producentów. Wartość bez źródła ma w `arcade.toml` oznaczenie `[ROBOCZE]`, a w dokumentacji `[DO WERYFIKACJI]`.
- Znaki marek osadzamy jako niezmienione pliki. Nigdy nie odtwarzamy ich krojem ani nie przebarwiamy. Pliki znaków nie są częścią tego repozytorium i nie są objęte jego licencjami.
- Moduł LoRa nadaje tylko w paśmie i z mocą dopuszczalną w UE (868 MHz, ERC/REC 70‑03). Przed użyciem na antenie poza testami trzeba potwierdzić zgodność urządzenia z dyrektywą RED.
- Zamówienie u fabryki składa człowiek. Pakiet zamówienia (zob. [`zamowienie/README.md`](../zamowienie/README.md)) jest gotowy do wgrania, ale agent go nie wysyła i niczego nie kupuje.
