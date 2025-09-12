# Symlink Checker - Projectdocumentatie

## Projectoverzicht

Symlink Checker is een Python command line tool voor macOS die symlinks van applicaties beheert tussen twee locaties:
- **Bron**: `/Volumes/MMKMINI/SYMLINKED` (originele apps)
- **Doel**: `/Applications` (symlinks)

## Hoofdfunctionaliteiten

- Controleert of `.app` bestanden in SYMLINKED correct gesymlinkt zijn naar `/Applications`
- Detecteert wanneer symlinks zijn vervangen door echte apps
- Interactief menu voor het verwerken van gedetecteerde problemen
- Skiplist functionaliteit voor het blijvend overslaan van apps
- Kleurgecodeerde terminal output voor betere gebruikservaring

## Bestandsstructuur

- `symlink_checker.py` - Hoofdscript
- `skiplist.txt` - Apps die overgeslagen moeten worden
- `README.md` - Uitgebreide gebruikersdocumentatie
- `LICENSE` - MIT licentie

## Technische Details

### Belangrijke Paden
```python
SYMLINKED_DIR = "/Volumes/MMKMINI/SYMLINKED"
APPS_DIR = "/Applications"
SKIPLIST_FILE = os.path.join(os.path.dirname(__file__), "skiplist.txt")
```

### Gebruikersinteractie
Het script biedt een interactief menu met opties:
- `[j]` Ja - verplaats app en maak nieuwe symlink
- `[n]` Nee - overslaan voor deze sessie
- `[b]` Blijvend overslaan - voeg toe aan skiplist
- `[a]` Alles automatisch ja - batchmodus
- `[s]` Stoppen - beëindig het script

### Kleuren Systeem
Gebruikt ANSI kleurcodes voor terminal output:
- Groen: OK status
- Geel: Waarschuwingen
- Rood: Fouten/problemen

## Veiligheidsoverwegingen

- Script vereist vaak `sudo` rechten voor schrijftoegang tot `/Applications`
- Controleert schrijfrechten voordat operaties worden uitgevoerd
- Maakt backup van bestaande apps door ze naar SYMLINKED te verplaatsen

## Gebruikspatroon

1. Script detecteert apps die geen symlink meer zijn
2. Gebruiker kiest actie per app
3. Script verplaatst echte app terug naar SYMLINKED
4. Maakt nieuwe symlink aan in `/Applications`
5. Toont overzicht van resultaten

## Ontwikkelingsnotities

- Alleen `.app` bundles worden verwerkt
- Verborgen bestanden (beginnend met `.`) worden genegeerd
- Gebruikt Python's `shutil` voor bestandsoperaties
- `os.path.islink()` voor symlink detectie

## Skiplist Beheer

- `skiplist.txt` bevat één app naam per regel
- Apps in skiplist worden automatisch overgeslagen
- Gebruikers kunnen apps toevoegen via `[b]` optie