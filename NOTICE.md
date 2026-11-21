# NOTICE

**Pilot Wnet**: an open-hardware studio controller for a radio station.
Copyright 2026 Radio Wnet Sp. z o.o.

This repository follows the REUSE specification (<https://reuse.software>). `REUSE.toml` declares the copyright and licence of every file, and the full licence texts are in `LICENSES/`. This notice summarises them and lists the third-party material.

## Licences at a glance

| What | Licence (SPDX identifier) |
|---|---|
| Hardware design: KiCad project and project library (`pcb/`), including the scripts that generate the design (`pcb/obwod.py`, `pcb/plytka.py`, `pcb/v01/`) and their CSV/JSON data, BOMs and ERC/DRC reports; enclosure and part geometry and the cutting-sheet generator (`projekt/`) | CERN Open Hardware Licence Version 2 – Strongly Reciprocal (`CERN-OHL-S-2.0`) |
| Software: MicroPython firmware and tests (`firmware/micropython/`), MeshCore helper files (`firmware/meshcore/`), draft mesh CI (`firmware/ci/`), SPICE tests and decks (`sim/`), Blender generator (`blender/`), GitHub workflows | MIT License (`MIT`) |
| Documentation: README files, `docs/`, `research/`, `DECYZJE.md`, `zamowienie/`, `CONTRIBUTING.md`, this notice, GitHub templates | Creative Commons Attribution-ShareAlike 4.0 International (`CC-BY-SA-4.0`) |
| Repository housekeeping (`.gitignore` files, `REUSE.toml`) | CC0 1.0 Universal (`CC0-1.0`) |
| Meshtastic board variant (`firmware/meshtastic/`) | GNU General Public License v3.0 only (`GPL-3.0-only`) |
| Two footprints derived from the KiCad libraries (section 1) | `CC-BY-SA-4.0 WITH KiCad-libraries-exception` |
| E22-900M22S symbol and footprint from the EasyEDA/LCSC library (section 5) | `LicenseRef-EasyEDA-Library` (no licence granted) |
| Board, schematic and netlist (`pcb/kicad/pilot_wnet.kicad_pcb`, `.kicad_sch`, `.net`), which embed copies of the E22 data | `CERN-OHL-S-2.0 AND LicenseRef-EasyEDA-Library` |
| `DCO.txt` (Developer Certificate of Origin 1.1, The Linux Foundation and its contributors) | `LicenseRef-DCO` (verbatim copying only) |

## Hardware licence notice

Copyright 2026 Radio Wnet Sp. z o.o.

This source describes Open Hardware and is licensed under the CERN-OHL-S v2.

You may redistribute and modify this source and make products using it under the terms of the CERN-OHL-S v2 (<https://ohwr.org/cern_ohl_s_v2.txt>).

This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.

Source Location: <SOURCE-LOCATION-URL — to be filled in before publication>

As per CERN-OHL-S v2 section 4, should You produce hardware based on this source, You must where practicable maintain the Source Location visible on the PCB silkscreen or on the enclosure of the Pilot Wnet or other products you make using this source.

The Rev A board does not carry the Source Location on its silkscreen yet; adding it is part of Rev B.

## Third-party material in this repository

### 1. KiCad libraries (CC-BY-SA-4.0 with the KiCad libraries exception)

The schematic, netlist and board files in `pcb/kicad/` contain copies of symbols and footprints from the official KiCad 10 libraries (KiCad Libraries Team, <https://gitlab.com/kicad/libraries>). Those libraries are licensed under CC-BY-SA-4.0 with an exception: for electronic designs that use the libraries, and for files generated from such designs, the copyright holder waives Article 3 of the licence (<https://www.kicad.org/libraries/license/>, `LICENSES/KiCad-libraries-exception.txt`). The design files are therefore distributed under CERN-OHL-S-2.0. We thank the KiCad Libraries Team. The 3D models referenced through `${KICAD10_3DMODEL_DIR}` are not included; they ship with KiCad.

Two footprints in `pcb/lib/pilot_jlc.pretty/` are modified copies of KiCad library footprints, distributed as library files. The exception does not cover library parts redistributed as a library, so these two files keep the library licence, `CC-BY-SA-4.0 WITH KiCad-libraries-exception` (`LICENSES/CC-BY-SA-4.0.txt`, `LICENSES/KiCad-libraries-exception.txt`). Original work: KiCad Libraries Team.

| File | Original | Changes by Radio Wnet (2026) |
|---|---|---|
| `ESP32-S3-WROOM-1_Pilot.kicad_mod` | `RF_Module:ESP32-S3-WROOM-1` | courtyard narrowed (the RF keep-out zone is kept), 0.3 mm thermal vias added, renamed |
| `USB_C_Receptacle_HRO_TYPE-C-31-M-12_Pilot.kicad_mod` | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | silkscreen lines crossing the board edge moved to F.Fab, renamed |

### 2. Meshtastic board variant (GPL-3.0-only)

`firmware/meshtastic/variants/esp32s3/diy/pilot_wnet/platformio.ini` and `variant.h` are derived from `variants/esp32s3/t-eth-elite/` of the Meshtastic firmware (<https://github.com/meshtastic/firmware>, branch `develop`, retrieved 2026-10-18). The header of each file names the upstream file and lists the changes. Original work: Meshtastic contributors. Both files are distributed under the GNU General Public License v3.0 only (`LICENSES/GPL-3.0-only.txt`), matching the upstream declaration. They are meant to be copied into the Meshtastic source tree; firmware built from that tree is covered by the GPL and must be distributed with its source code.

Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk.

This project is not affiliated with or endorsed by the Meshtastic project. The name is used only to identify compatible firmware and is not part of the product name; no Meshtastic logo is used (<https://meshtastic.org/docs/legal/licensing-and-trademark/>).

### 3. MeshCore build environment (MIT)

`firmware/meshcore/platformio_pilot_wnet.ini` is derived from the `[LilyGo_TETH_Elite_sx1262]` section of `variants/lilygo_teth_elite/platformio.ini` in MeshCore (<https://github.com/meshcore-dev/MeshCore>, branch `main`, retrieved 2026-10-18). The file header keeps the original notice.

Copyright (c) 2025 Scott Powell / rippleradios.com. MIT License (`LICENSES/MIT.txt`).

### 4. micropython-lib (MIT)

The method `PilotHID.desc_cfg` in `firmware/micropython/lib/pilot_hid.py` is adapted from `HIDInterface.desc_cfg` in the micropython-lib package `usb-device-hid` (<https://github.com/micropython/micropython-lib>). It was changed to use 64-byte interrupt packets.

Copyright (c) 2023 Angus Gratton. MIT License (`LICENSES/MIT.txt`).

### 5. Ebyte E22-900M22S library data (until Rev B)

`pcb/lib/pilot_jlc.kicad_sym` (symbol) and `pcb/lib/pilot_jlc.pretty/WIRELM-SMD_E22-900M22S.kicad_mod` (footprint) were converted with easyeda2kicad from the EasyEDA/LCSC component library (LCSC part C411293); the pin types in the symbol and the 3D model path in the footprint were then edited. Copies of this symbol and footprint (part U6) are also embedded in `pcb/kicad/pilot_wnet.kicad_sch`, `pilot_wnet.kicad_pcb` and `pilot_wnet.net`.

The terms for redistributing this data are not established, so it is **not** covered by the licences of this project (`LicenseRef-EasyEDA-Library`, see `LICENSES/LicenseRef-EasyEDA-Library.txt`). It is included only so that the KiCad project can be opened and checked. The symbol and footprint will be redrawn from the Ebyte datasheet in Rev B.

**The E22 3D model is not included.** The footprint still refers to a model file in `pcb/lib/pilot_jlc.3dshapes/`, which is absent, so a 3D export reports the model as missing and shows no E22 body.

## Not included (obtain separately)

- MicroPython and the micropython-lib packages `usb-device-hid`, `aioble`, `lora-sync` and `lora-sx126x` (MIT), installed on the board with `mpremote mip install`.
- The Meshtastic and MeshCore source trees, which the draft CI fetches at pinned commits.
- The 3D models of the KiCad libraries and of the E22 module.
- Brand fonts, logos and the top-panel artwork of Radio Wnet.
- The tools used to produce files in this repository (KiCad, SKiDL, KiKit, Freerouting, ngspice, Blender, PlatformIO, easyeda2kicad). They are not distributed here, and their licences do not cover the design data made with them.
- The host application for the studio computer: the host implementation is not public (yet).

## Trademarks

"Radio Wnet", "Pilot Wnet" and the Radio Wnet logo identify Radio Wnet Sp. z o.o. Other product and company names (for example Espressif, ESP32, WIZnet, Ebyte, Texas Instruments, JLCPCB, LCSC, EasyEDA, Sanwa, Seimitsu, Meshtastic® and MeshCore) belong to their respective owners. None of the licences in this repository grants trademark rights (see also CERN-OHL-S v2, section 8.2). Products made from this design must not suggest that they come from Radio Wnet or are endorsed by it.

## Quotations and factual data

The reports in `research/` contain short quotations from manufacturers' documentation and web pages. Each quotation is marked and linked to its source, and is used under the right of quotation (Art. 29 of the Polish Act on Copyright and Related Rights; Art. 10 of the Berne Convention). The quotations remain the property of their authors; CC-BY-SA-4.0 covers only the text written for this project. Part numbers, prices, stock levels and technical parameters are factual data taken from the cited sources and were valid on the date stated.

## AI assistance

A large part of this repository was prepared by AI agents (Claude, by Anthropic) working under human direction: the design scripts and the KiCad files they generate, the MicroPython firmware and its tests, the SPICE tests, the enclosure and Blender generators, the research reports, the decision register, the ordering notes, the audit summary (`docs/AUDYT_REV_A.md`) and the documentation, including this notice. This section is the general disclosure; many documents also say so in their headers or footers. No hardware engineer has reviewed the Rev A design; a person must review it before any boards are ordered or built.

## No warranty

Everything in this repository is provided "as is", without warranty of any kind, as stated in the respective licences.
