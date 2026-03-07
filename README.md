# symlink_checker

**Een tool om symlinks van je apps te beheren tussen `/Volumes/MMKMINI/SYMLINKED` (de originele apps) en `/Applications` (de symlinks).**

Verkrijgbaar in **twee versies**:
- 🖥️ **symlink_checker.py** - Terminal UI (Textual)
- 🌐 **symgui.py** - Web Interface (NiceGUI)

---

## 🚀 Quick Start

```bash
# Installeer dependencies
pip install -r requirements.txt

# Start Terminal UI
python3 symlink_checker.py

# OF start Web Interface
python3 symgui.py
# → Open browser naar http://localhost:8080
```

---

## Functies

- Controleert of voor elke `.app` in de SYMLINKED-map een symlink in `/Applications` bestaat.
- Als de symlink in `/Applications` is vervangen door een echte app, kun je kiezen om deze terug te verplaatsen naar SYMLINKED en een nieuwe symlink aan te maken.
- Je kunt apps blijvend overslaan via een skiplist.
- Overzichtelijke rapportage van alle apps en eventuele problemen.

## Installatie

1. Zorg dat je Python 3.8+ geïnstalleerd hebt.
2. Clone deze repository:
   ```bash
   git clone https://github.com/jouwgebruikersnaam/symlink-checker.git
   cd symlink-checker
   ```
3. Maak een virtuele omgeving aan en installeer dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Of installeer alleen wat je nodig hebt:
   ```bash
   # Alleen Terminal UI
   pip install textual

   # Alleen Web Interface
   pip install nicegui
   ```

## Gebruik

### Optie 1: Terminal UI (Textual) - `symlink_checker.py`

1. **Open een terminal** en ga naar de project map:
   ```bash
   cd /Volumes/MMKMINI/Mario/ai/symcheck
   ```
2. **Activeer de virtual environment:**
   ```bash
   source venv/bin/activate
   ```
3. **Voer het script uit:**
   ```bash
   python3 symlink_checker.py
   ```
   > **Let op:** Voor het verplaatsen van apps uit `/Applications` zijn meestal beheerdersrechten nodig. Gebruik dan:
   > ```bash
   > sudo python3 symlink_checker.py
   > ```

### Optie 2: Web Interface (NiceGUI) - `symgui.py`

1. **Open een terminal** en ga naar de project map:
   ```bash
   cd /Volumes/MMKMINI/Mario/ai/symcheck
   ```
2. **Activeer de virtual environment:**
   ```bash
   source venv/bin/activate
   ```
3. **Start de web interface:**
   ```bash
   python3 symgui.py
   ```
4. **Open je browser** en ga naar: `http://localhost:8080`

De web interface opent automatisch in je standaard browser en biedt:
- 📊 Visueel dashboard met statistieken
- 🔍 Real-time scan functionaliteit
- ⚙️ Eenvoudige configuratie pagina
- 📋 Skiplist beheer met één klik
- 🎨 Modern, responsief design

## Welke versie kiezen?

| Feature | Terminal UI<br>`symlink_checker.py` | Web Interface<br>`symgui.py` |
|---------|-------------------------------------|------------------------------|
| **Interface** | Terminal (Textual) | Web Browser |
| **Visuele statistieken** | ⚪ Basis | ✅ Dashboard met cards |
| **Configuratie** | ⚪ Handmatig | ✅ GUI formulier |
| **Skiplist beheer** | ⚪ Tijdens scan | ✅ Dedicated pagina |
| **Batch operaties** | ✅ Auto-mode | ⚪ Per item |
| **Remote access** | ✅ SSH | ✅ Browser (LAN) |
| **Resource gebruik** | ⚡ Minimaal | 🔋 Gemiddeld |
| **Start tijd** | ⚡ Direct | 🔋 ~2 seconden |
| **Best voor** | Power users, scripts | Visuele gebruikers |

### Terminal UI (symlink_checker.py)
**Interactieve opties:**
- `[j]` Ja, verplaats en maak symlink
- `[n]` Nee, overslaan
- `[b]` Blijvend overslaan (toevoegen aan skiplist)
- `[a]` Alles automatisch ja (batchmodus)
- `[s]` Stoppen

### Web Interface (symgui.py)
**Features:**
- 📊 Real-time statistieken (OK / Problemen / Overgeslagen)
- 🎯 Per-app acties met knoppen
- ⚙️ Configuratie pagina voor directories
- 📋 Skiplist beheer pagina
- 🎨 Auto dark mode ondersteuning

## Skiplist

- Apps die je blijvend wilt overslaan, worden toegevoegd aan `skiplist.txt` in dezelfde map als het script.
- Apps in deze lijst worden bij volgende runs automatisch overgeslagen.

## Overzicht na afloop

- Alle apps die in orde zijn (symlink in `/Applications`) worden op één regel, komma-gescheiden, getoond.
- Alle bijzonderheden (fouten, niet gevonden, verwerkt, overgeslagen, skiplist, etc.) worden op een eigen regel getoond.

## Alleen `.app`-bundels

- Het script controleert alleen items die eindigen op `.app` in de SYMLINKED-map.

## Vereisten

- Python 3.8+
- Schrijfrechten op `/Applications` (voor verplaatsen/symlinks maken)
- **Voor Terminal UI:** `textual` package
- **Voor Web Interface:** `nicegui` package (geïnstalleerd in venv)

## Bijdragen

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue om te bespreken wat je wilt veranderen.

## Licentie

Dit project is open source en wordt aangeboden onder de MIT-licentie. Zie het LICENSE-bestand voor meer informatie.

## Disclaimer

Gebruik dit script met zorg. Het verplaatst en verwijdert bestanden/mappen. Maak altijd een backup van belangrijke data.
