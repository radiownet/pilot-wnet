# Contributing to Pilot Wnet

Thank you for helping. Pilot Wnet is open hardware with firmware and tooling around it, and we work in the open: discussions, reviews and changes happen in this repository. A short summary in Polish is at the end: [Po polsku](#po-polsku).

## Where to start

- **Questions, ideas, your build:** GitHub Discussions.
- **Bugs, design review findings, documentation errors:** Issues. For design review, name the file, sheet or reference designator, and attach screenshots of the relevant layers. Known findings have IDs (for example layout-04) in [docs/AUDYT_REV_A.md](docs/AUDYT_REV_A.md); refer to them.
- **Re-layout Rev B:** the main open task (template `.github/ISSUE_TEMPLATE/relayout-rev-b.md`). It may be paid work: ask in Discussions before you start, so that nobody duplicates the work.
- **Larger changes** (new features, part or package swaps, connector moves, licensing questions): start a Discussion first.

## Developer Certificate of Origin (DCO)

We use the Developer Certificate of Origin 1.1 ([DCO.txt](DCO.txt)) instead of a contributor licence agreement. By adding a `Signed-off-by` line to a commit you certify that you wrote the change or otherwise have the right to submit it under the project's licences. The text is also at <https://developercertificate.org/>.

- Sign off every commit: `git commit -s`. Git adds a `Signed-off-by` line with the name and e-mail address from your `user.name` and `user.email`.
- Forgot it? For the last commit: `git commit --amend -s --no-edit`. For the whole branch: `git rebase --signoff main`, then force-push your branch.
- Commits made in the GitHub web editor need a sign-off too.
- Pull requests with commits that are not signed off are not merged.
- Privacy: the name and e-mail address in the sign-off become a permanent part of the public git history (DCO clause d). You may use your GitHub `noreply` address.
- An AI tool cannot sign off. The person who submits the change signs off and is responsible for it.

## Licences of contributions

A contribution is licensed under the licence of the files it changes (inbound = outbound). The per-file mapping is in `REUSE.toml`:

- hardware design (`pcb/`, including the scripts that generate the design and their data, and `projekt/`): **CERN-OHL-S-2.0**;
- code (MicroPython firmware, MeshCore helpers, simulations, Blender generator, CI workflows): **MIT**;
- documentation (README files, `docs/`, `research/`, `DECYZJE.md`, `zamowienie/`, GitHub templates): **CC-BY-SA-4.0**;
- `firmware/meshtastic/`: **GPL-3.0-only**, a derivative of the upstream Meshtastic firmware.

New files need licence information: either an SPDX header (the `SPDX-FileCopyrightText` and `SPDX-License-Identifier` tags in a comment at the top of the file) or a matching entry in `REUSE.toml`. Run `reuse lint` before you open a pull request; CI runs it too.

Third-party material (footprints, symbols, 3D models, code, images) is accepted only under a licence compatible with the file it goes into. Give its source and licence in the pull request and add it to `NOTICE.md`. Do not add anything under a non-commercial (NC) or no-derivatives (ND) licence: the open source hardware definition does not allow restrictions on selling or modifying. Do not add brand logos. Library data from the EasyEDA/LCSC library (for example converted with easyeda2kicad) has unclear redistribution terms (see `NOTICE.md`): prefer symbols and footprints drawn from the manufacturer's datasheet.

## KiCad rules

- Use **KiCad 10.x**. The board and project files are saved with KiCad 10.0.8; the schematic is written by `pcb/schemat.py` in an older file format, which KiCad 10 opens and converts on save (expect a large one-time diff). Do not save the files with a nightly build or a newer major version: KiCad 10 would no longer open them.
- **ERC: 0 errors. DRC: 0 errors, 0 unconnected items, 0 schematic-parity issues** (DRC with `--schematic-parity`). CI fails on any of these on every pull request ([.github/workflows/kicad.yml](.github/workflows/kicad.yml)). Warnings are checked in review: explain every new warning in the pull request (CI flags any change against the known ones). The 21 `lib_footprint_mismatch` warnings on DNP parts (DRC) and the 6 `lib_symbol_mismatch` warnings (ERC) are known and intentional.
- When you change the design, refresh `pcb/wyniki/erc.json` and `pcb/wyniki/drc.json` with `kicad-cli` (commands in the README).
- **Do not move connectors, mounting holes (H1–H4) or the board outline without a discussion first.** Their positions are frozen to the Rev A board (criterion K11 of the Rev B task). The enclosure files (`projekt/arcade.toml`) still assume a 100 × 100 mm board and older cut-outs; they will be updated to match the board, not the other way round.
- Keep all parts on the top side. Project rules (more conservative than JLCPCB's 4-layer minimums): track/space at least 0.15/0.15 mm, vias at least 0.3 mm drill and 0.6 mm diameter. The board setup in `pilot_wnet.kicad_pro` still allows a 0.5 mm via diameter, so DRC will not catch a 0.5 mm via: check it yourself.
- Prefer parts stocked by JLCPCB/LCSC and keep the LCSC part number in the symbol fields. Discuss part or package swaps first.
- A change of GPIO assignment needs matching firmware changes: `firmware/micropython/lib/konfig_plytki.py` must agree with `pcb/obwod.py` (checked by `testy/test_konfig_plytki.py`).
- Do not run "Update footprints from library" on DNP parts: it restores the solder paste that was removed on purpose.
- For layout changes, add before/after screenshots of the affected layers to the pull request.
- Source of truth: Rev A is generated from scripts (`pcb/obwod.py`, `pcb/plytka.py`). From Rev B the KiCad project is planned to become the source of truth. Until the maintainers confirm this in Discussions, say in the pull request whether you changed the design in KiCad or in the generator.

## AI-assisted contributions

Much of this project was built with AI agents, and AI help is welcome in contributions too, on these conditions:

- **Disclose it** in the pull request: the tool or model, and what it did (for example "placement script written with an AI assistant" or "router run by an agent through kicad-cli").
- **A person reviews it.** You read every line of code you submit and check every design change yourself in KiCad (layers, clearances, datasheets). Say what you checked by hand.
- **You are responsible** for the change and you sign off the DCO, not the AI tool.
- Label documentation written by AI as such (for example "Draft written with AI assistance").
- Do not paste secrets, personal data or other people's confidential material into AI tools.

## Firmware

Tests run in CPython 3.11 or newer with the standard library only; MicroPython modules are mocked in `testy/atrapy.py`. Each test file runs on its own (do not pass several files to one interpreter). From `firmware/micropython`:

```sh
python -I -B -X utf8 testy/test_pilot_ramka.py            # one file
for t in testy/test_*.py; do python -I -B -X utf8 "$t" || echo "FAILED: $t"; done
```

Windows (cmd): `for %f in (testy\test_*.py) do python -I -B -X utf8 %f`

CI (`.github/workflows/firmware.yml`) runs the same loop.

- Add or update tests with every logic change. Mocks are not hardware tests: say in the pull request whether you tried the change on a board.
- **Never commit secrets.** `pilot_konfig.json` (it holds the HMAC key) stays outside the repository and is listed in `.gitignore`; only `pilot_konfig.przyklad.json`, without secret values, is tracked. The MeshCore admin password comes only from the `PILOT_MC_ADMIN_HASLO` environment variable.
- Changes to radio settings (sub-bands, power, duty cycle) need a short note on their regulatory effect.

## Pull requests

- Keep pull requests small, one topic each, and fill in the checklist from the template.
- English and Polish are both fine in issues, pull requests and commit messages.
- Be respectful and stay on topic.

## Po polsku

- **Gdzie zacząć:** pytania i pomysły w GitHub Discussions, błędy i uwagi z przeglądu w Issues (znane znaleziska mają identyfikatory w `docs/AUDYT_REV_A.md`). Główne zadanie to ponowne trasowanie płytki (Rev B); może być płatne, więc przed startem zapytaj w Discussions.
- **DCO 1.1:** każdy commit z podpisem `Signed-off-by`, czyli `git commit -s` (tekst: `DCO.txt`). Imię i adres e-mail z podpisu zostają na stałe w publicznej historii; możesz użyć adresu `noreply` z GitHuba. Podpisuje człowiek, nie narzędzie SI.
- **Licencje:** wkład dostaje licencję zmienianego pliku (mapa w `REUSE.toml`): sprzęt (`pcb/` ze skryptami generującymi projekt, `projekt/`) CERN-OHL-S-2.0, kod MIT, dokumentacja CC-BY-SA-4.0, `firmware/meshtastic/` GPL-3.0-only. Nowe pliki z nagłówkiem SPDX albo wpisem w `REUSE.toml`. Bez materiałów na licencjach NC/ND i bez logotypów. Dane z biblioteki EasyEDA/LCSC mają niejasne warunki rozpowszechniania (zob. `NOTICE.md`): lepiej rysować symbole i footprinty z karty producenta.
- **KiCad:** wersja 10.x; płytka i projekt zapisane w 10.0.8, schemat w starszym formacie ze skryptu. ERC 0 błędów, DRC 0 błędów, 0 niepołączonych i 0 rozbieżności ze schematem (pilnuje tego CI); nowe ostrzeżenia opisz w PR. Złączy, otworów montażowych ani obrysu nie przesuwaj bez wcześniejszej dyskusji: wzorcem jest płytka Rev A, a obudowa zostanie do niej dopasowana. Reguły projektu są ostrzejsze niż minima JLCPCB (ścieżka/odstęp 0,15/0,15 mm, przelotka 0,3/0,6 mm).
- **SI:** zmiany przygotowane z pomocą SI są mile widziane. Ujawnij narzędzie i zakres w opisie PR, sprawdź wynik ręcznie i weź za niego odpowiedzialność.
- **Testy firmware:** z katalogu `firmware/micropython` każdy plik osobno, w pętli: `for t in testy/test_*.py; do python -I -B -X utf8 "$t" || echo "NIEUDANY: $t"; done` (cmd: `for %f in (testy\test_*.py) do python -I -B -X utf8 %f`).
- **Sekrety:** nigdy nie commituj `pilot_konfig.json`, kluczy ani haseł.

---

*This guide was drafted by an AI agent (Claude) working under human direction.*
