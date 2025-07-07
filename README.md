# symlink_checker

**Een command line tool om symlinks van je apps te beheren tussen `/Volumes/MMKMINI/SYMLINKED` (de originele apps) en `/Applications` (de symlinks).**

---

## Functies

- Controleert of voor elke `.app` in de SYMLINKED-map een symlink in `/Applications` bestaat.
- Als de symlink in `/Applications` is vervangen door een echte app, kun je kiezen om deze terug te verplaatsen naar SYMLINKED en een nieuwe symlink aan te maken.
- Je kunt apps blijvend overslaan via een skiplist.
- Aan het einde krijg je een overzicht van alle in orde zijnde apps en alle bijzonderheden.

## Installatie

1. Zorg dat je Python 3 geïnstalleerd hebt.
2. Clone deze repository:
   ```bash
   git clone https://github.com/jouwgebruikersnaam/symlink-checker.git
   cd symlink-checker
   ```
3. (Optioneel) Maak een virtuele omgeving aan:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

## Gebruik

1. **Plaats het script** `symlink_checker.py` in een map, bijvoorbeeld `/Volumes/MMKMINI/Mario/ai/symcheck`.
2. **Open een terminal** en ga naar deze map:
   ```bash
   cd /Volumes/MMKMINI/Mario/ai/symcheck
   ```
3. **Voer het script uit:**
   ```bash
   python3 symlink_checker.py
   ```
   > **Let op:** Voor het verplaatsen van apps uit `/Applications` zijn meestal beheerdersrechten nodig. Gebruik dan:
   > ```bash
   > sudo python3 symlink_checker.py
   > ```

## Interactieve opties

- `[j]` Ja, verplaats en maak symlink
- `[n]` Nee, overslaan
- `[b]` Blijvend overslaan (toevoegen aan skiplist)
- `[a]` Alles automatisch ja (batchmodus)
- `[s]` Stoppen

## Skiplist

- Apps die je blijvend wilt overslaan, worden toegevoegd aan `skiplist.txt` in dezelfde map als het script.
- Apps in deze lijst worden bij volgende runs automatisch overgeslagen.

## Overzicht na afloop

- Alle apps die in orde zijn (symlink in `/Applications`) worden op één regel, komma-gescheiden, getoond.
- Alle bijzonderheden (fouten, niet gevonden, verwerkt, overgeslagen, skiplist, etc.) worden op een eigen regel getoond.

## Alleen `.app`-bundels

- Het script controleert alleen items die eindigen op `.app` in de SYMLINKED-map.

## Vereisten

- Python 3
- Schrijfrechten op `/Applications` (voor verplaatsen/symlinks maken)

## Bijdragen

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue om te bespreken wat je wilt veranderen.

## Licentie

Dit project is open source en wordt aangeboden onder de MIT-licentie. Zie het LICENSE-bestand voor meer informatie.

## Disclaimer

Gebruik dit script met zorg. Het verplaatst en verwijdert bestanden/mappen. Maak altijd een backup van belangrijke data.
