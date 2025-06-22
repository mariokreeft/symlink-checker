import os
import shutil
import sys

SYMLINKED_DIR = "/Volumes/MMKMINI/SYMLINKED"
APPS_DIR = "/Applications"
SKIPLIST_FILE = os.path.join(os.path.dirname(__file__), "skiplist.txt")

# Kleuren voor terminal
class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def kleurtekst(tekst, kleur):
    if sys.stdout.isatty():
        return kleur + tekst + Colors.END
    return tekst

def lees_skiplist():
    if not os.path.exists(SKIPLIST_FILE):
        return set()
    with open(SKIPLIST_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def voeg_toe_aan_skiplist(app_naam):
    with open(SKIPLIST_FILE, 'a') as f:
        f.write(app_naam + '\n')

def is_symlink(path):
    return os.path.islink(path)

def check_permissions():
    # Probeer te schrijven in /Applications
    testpad = os.path.join(APPS_DIR, ".symcheck_test")
    try:
        with open(testpad, 'w') as f:
            f.write('test')
        os.remove(testpad)
    except Exception:
        print(kleurtekst("[WAARSCHUWING] Je hebt geen schrijfrechten in /Applications! Voer dit script uit met 'sudo' als je apps wilt verplaatsen.", Colors.WARNING))

def main():
    check_permissions()
    alles_automatisch = False
    skiplist = lees_skiplist()
    in_orde = []
    bijzonderheden = []
    for item in os.listdir(SYMLINKED_DIR):
        if item.startswith('.'):
            continue
        if not item.endswith('.app'):
            continue
        if item in skiplist:
            bijzonderheden.append(f"[SKIP] {item} staat in de skiplist, wordt overgeslagen.")
            continue
        origineel_path = os.path.join(SYMLINKED_DIR, item)
        app_path = os.path.join(APPS_DIR, item)
        if not os.path.exists(app_path):
            bijzonderheden.append(f"[!] {item} bestaat niet in {APPS_DIR}")
            continue
        if is_symlink(app_path):
            in_orde.append(item)
            continue
        bijzonderheden.append(f"[!] {item} is GEEN symlink meer in {APPS_DIR}")
        if alles_automatisch:
            antwoord = 'j'
        else:
            print("-" * 50)
            print(kleurtekst(f"[!] {item} is GEEN symlink meer in {APPS_DIR}", Colors.FAIL))
            print(f"Wat wil je doen met {item}?")
            print("  [j] Ja, verplaats en maak symlink")
            print("  [n] Nee, overslaan")
            print("  [b] Blijvend overslaan (toevoegen aan skiplist)")
            print("  [a] Alles automatisch ja")
            print("  [s] Stoppen")
            antwoord = input("Keuze (j/n/b/a/s): ").lower()
        if antwoord == 'a':
            alles_automatisch = True
            antwoord = 'j'
        if antwoord == 's':
            bijzonderheden.append("[STOP] Script gestopt door gebruiker.")
            break
        if antwoord == 'b':
            voeg_toe_aan_skiplist(item)
            bijzonderheden.append(f"[SKIP] {item} toegevoegd aan skiplist.")
            continue
        if antwoord == 'j':
            nieuwe_locatie = os.path.join(SYMLINKED_DIR, item)
            try:
                # Verwijder eventueel het oude origineel
                if os.path.exists(nieuwe_locatie):
                    if os.path.isdir(nieuwe_locatie) and not os.path.islink(nieuwe_locatie):
                        shutil.rmtree(nieuwe_locatie)
                    else:
                        os.remove(nieuwe_locatie)
                shutil.move(app_path, nieuwe_locatie)
                os.symlink(nieuwe_locatie, app_path)
                bijzonderheden.append(f"[OK] {item} verwerkt: verplaatst en symlink opnieuw aangemaakt.")
            except Exception as e:
                bijzonderheden.append(f"[FOUT] Probleem met {item}: {e}")
        elif antwoord == 'n':
            bijzonderheden.append(f"[N] {item} handmatig overgeslagen.")
    print("\nKlaar!\n")
    if in_orde:
        print("In orde:")
        print(", ".join(in_orde))
    if bijzonderheden:
        print("\nBijzonderheden:")
        for b in bijzonderheden:
            print(b)

if __name__ == "__main__":
    main()
