<!-- English or Polish, both are fine. / Można pisać po polsku. -->

## What and why

<!-- Short description. Link the issue or discussion: "Closes #…" or "See #…". Refer to audit finding IDs (docs/AUDYT_REV_A.md) where relevant. -->

## Type of change

- [ ] PCB layout
- [ ] Schematic or parts
- [ ] Firmware
- [ ] Scripts or CI
- [ ] Documentation or translation

## How it was checked

<!-- Commands you ran, KiCad screenshots of the affected layers (before/after), measurements on a real board if you have one. -->

## AI disclosure

- [ ] No AI tools were used.
- [ ] AI-assisted. Tool or model, and what it did:
- What I reviewed by hand:

## Checklist

- [ ] Every commit is signed off under the DCO (`git commit -s`), see CONTRIBUTING.md.
- [ ] KiCad changes: saved with KiCad 10.x; the "KiCad ERC/DRC" check is green (ERC 0 errors; DRC 0 errors, 0 unconnected items, 0 schematic-parity issues); new or changed warnings are explained above; `pcb/wyniki/erc.json` and `pcb/wyniki/drc.json` are refreshed.
- [ ] Connectors, mounting holes and board outline are unchanged, or the change was agreed in #…
- [ ] Project rules kept: track/space ≥ 0.15/0.15 mm, vias ≥ 0.3 mm drill and 0.6 mm diameter (DRC alone allows 0.5 mm vias).
- [ ] GPIO changes: `firmware/micropython/lib/konfig_plytki.py` and `pcb/obwod.py` agree.
- [ ] Firmware changes: tests pass (each `testy/test_*.py` run on its own from `firmware/micropython`, see CONTRIBUTING; the "Firmware tests" check is green), and tests were added or updated.
- [ ] Licences: new files have SPDX headers or a `REUSE.toml` entry (the "REUSE lint" check is green); third-party footprints, symbols, 3D models or code are listed below with source and licence and added to `NOTICE.md`; nothing under NC or ND licences.
- [ ] No secrets or personal data (`pilot_konfig.json`, keys, passwords, private addresses or paths).
- [ ] Radio settings (sub-band, power, duty cycle) are unchanged, or the regulatory effect is described above.
- [ ] Documentation is updated (README, `DECYZJE.md` if a decision changes).

## Third-party material

<!-- Source URL and licence of every added footprint, symbol, 3D model, code or image. Write "none" if there is none. -->
