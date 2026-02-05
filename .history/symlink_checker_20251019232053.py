import os
import shutil
import json
import asyncio
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header, Footer, Button, Input, ListView, ListItem, Label, Static,
    ProgressBar, DataTable
)
from textual.screen import Screen
from textual import on, work
from textual.message import Message


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
SKIPLIST_FILE = os.path.join(os.path.dirname(__file__), "skiplist.txt")


def load_config():
    default_config = {
        "symlinked_dir": "/Volumes/MMKMINI/SYMLINKED",
        "apps_dir": "/Applications"
    }   
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


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


class CheckComplete(Message):
    def __init__(self, in_orde: List[str], bijzonderheden: List[str]):
        super().__init__()
        self.in_orde = in_orde
        self.bijzonderheden = bijzonderheden


class DirModal(Screen):
    DEFAULT_CSS = """
    DirModal {
        align: center middle;
    }
    """

    def __init__(self, title: str, current: str, key: str):
        super().__init__()
        self.title = title
        self.current = current
        self.key = key

    @property
    def is_modal(self) -> bool:
        return True

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(self.title),
            Input(value=self.current, id="dir_input"),
            Horizontal(
                Button("Save", id="save", variant="success"),
                Button("Cancel", id="cancel", variant="error"),
                Button("Afsluiten", id="exit", variant="error")
            )
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event):
        if event.button.id == "save":
            new_dir = self.query_one(Input).value
            if os.path.isdir(new_dir):
                config = load_config()
                config[self.key] = new_dir
                save_config(config)
                self.app.post_message(DirUpdated(new_dir, self.key))
                self.app.notify("✓ Directory bijgewerkt", severity="success")
            else:
                self.app.notify("✗ Ongeldige directory", severity="error")
        elif event.button.id == "exit":
            self.app.exit()
        self.dismiss()

    def key_q(self):
        """Afsluiten met Q toets"""
        self.app.exit()

    def key_escape(self):
        """Afsluiten met Escape toets"""
        self.app.exit()

    def key_up(self):
        """Navigeer omhoog met pijltjestoets"""
        self.run_action("focus_previous")

    def key_down(self):
        """Navigeer omlaag met pijltjestoets"""
        self.run_action("focus_next")

    def key_left(self):
        """Navigeer links met pijltjestoets"""
        # Voor horizontale menu's: ga naar vorige knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de vorige
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index > 0:
                buttons[current_index - 1].focus()
            else:
                self.run_action("focus_previous")

    def key_right(self):
        """Navigeer rechts met pijltjestoets"""
        # Voor horizontale menu's: ga naar volgende knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de volgende
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index < len(buttons) - 1:
                buttons[current_index + 1].focus()
            else:
                self.run_action("focus_next")


class DirUpdated(Message):
    def __init__(self, dir_path: str, key: str):
        super().__init__()
        self.dir_path = dir_path
        self.key = key


class SkiplistScreen(Screen):
    def compose(self) -> ComposeResult:
        skiplist = sorted(lees_skiplist())
        yield Vertical(
            Label("Skiplist"),
            ListView(*[ListItem(Horizontal(Label(item, classes="skiplist-item"), Button("Verwijder", id=f"remove_{item}", classes="remove-button"))) for item in skiplist], id="skiplist_list"),
            Input(placeholder="Voeg app toe", id="add_input"),
            Horizontal(
                Button("Voeg toe", id="add"),
                Button("Terug", id="back", variant="primary"),
                Button("Afsluiten", id="exit", variant="error")
            )
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event):
        if event.button.id == "add":
            app = self.query_one("#add_input", Input).value.strip()
            if app:
                voeg_toe_aan_skiplist(app)
                self.query_one(ListView).append(ListItem(Horizontal(Label(app, classes="skiplist-item"), Button("Verwijder", id=f"remove_{app}", classes="remove-button"))))
                self.app.notify(f"✓ {app} toegevoegd", severity="success")
                self.query_one("#add_input").value = ""
        elif event.button.id.startswith("remove_"):
            app = event.button.id[7:]
            skiplist = lees_skiplist()
            if app in skiplist:
                skiplist.remove(app)
                with open(SKIPLIST_FILE, 'w') as f:
                    f.write('\n'.join(sorted(skiplist)) + '\n')
                list_view = self.query_one(ListView)
                for item in list_view.children:
                    if isinstance(item, ListItem) and item.children and item.children[0].renderable == app:
                        list_view.remove(item)
                        break
                self.app.notify(f"✓ {app} verwijderd", severity="success")
        elif event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "exit":
            self.app.exit()

    def key_q(self):
        """Afsluiten met Q toets"""
        self.app.exit()

    def key_escape(self):
        """Afsluiten met Escape toets"""
        self.app.exit()

    def key_up(self):
        """Navigeer omhoog met pijltjestoets"""
        self.run_action("focus_previous")

    def key_down(self):
        """Navigeer omlaag met pijltjestoets"""
        self.run_action("focus_next")

    def key_left(self):
        """Navigeer links met pijltjestoets"""
        # Voor horizontale menu's: ga naar vorige knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de vorige
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index > 0:
                buttons[current_index - 1].focus()
            else:
                self.run_action("focus_previous")

    def key_right(self):
        """Navigeer rechts met pijltjestoets"""
        # Voor horizontale menu's: ga naar volgende knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de volgende
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index < len(buttons) - 1:
                buttons[current_index + 1].focus()
            else:
                self.run_action("focus_next")


class ResultsScreen(Screen):
    def __init__(self, in_orde: List[str], bijzonderheden: List[str]):
        self.in_orde = in_orde
        self.bijzonderheden = bijzonderheden
        super().__init__()

    def compose(self) -> ComposeResult:
        total = len(self.in_orde) + len(self.bijzonderheden)
        valid = len(self.in_orde)
        issues = len(self.bijzonderheden)
        percentage = (valid / total * 100) if total > 0 else 0
        summary = f"Total Apps: {total} | Valid: {valid} ({percentage:.0f}%) | Issues: {issues}"
        table = DataTable()
        table.add_columns("App Name", "Status", "Details")
        for app in self.in_orde:
            table.add_row(app, "✓ Valid", "Symlink OK")
        for msg in self.bijzonderheden:
            if "[SKIP]" in msg:
                app = msg.split("] ")[1].split(" staat")[0]
                table.add_row(app, "⚠️ Skipped", msg)
            elif "[!]" in msg:
                app = msg.split("] ")[1].split(" bestaat")[0] if "bestaat niet" in msg else msg.split("] ")[1].split(" is GEEN")[0]
                table.add_row(app, "✗ Broken", msg)
            elif "[OK]" in msg:
                app = msg.split("] ")[1].split(" verwerkt")[0]
                table.add_row(app, "✓ Fixed", msg)
            elif "[FOUT]" in msg:
                app = msg.split("] ")[1].split(" Probleem")[0]
                table.add_row(app, "✗ Error", msg)
            elif "[N]" in msg:
                app = msg.split("] ")[1].split(" handmatig")[0]
                table.add_row(app, "⚠️ Skipped", msg)
        yield Vertical(
            Label("Resultaten"),
            Label(summary),
            Container(table, classes="results-container"),
            Horizontal(
                Button("Terug", id="back", variant="primary"),
                Button("Afsluiten", id="exit", variant="error")
            )
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "exit":
            self.app.exit()

    def key_q(self):
        """Afsluiten met Q toets"""
        self.app.exit()

    def key_escape(self):
        """Afsluiten met Escape toets"""
        self.app.exit()

    def key_up(self):
        """Navigeer omhoog met pijltjestoets"""
        self.run_action("focus_previous")

    def key_down(self):
        """Navigeer omlaag met pijltjestoets"""
        self.run_action("focus_next")

    def key_left(self):
        """Navigeer links met pijltjestoets"""
        self.run_action("focus_previous")

    def key_right(self):
        """Navigeer rechts met pijltjestoets"""
        self.run_action("focus_next")


class SymlinkCheckerApp(App):
    CSS = """
    Screen {
        background: #1e1e2e;
    }
    
    #menu {
        height: 100%;
        padding: 0 1;
    }
    
    /* Directory container */
    .dirs-container {
        background: #313244;
        border: round #89b4fa;
        padding: 0 1;
        margin: 0 0 1 0;
        height: auto;
        overflow: auto;
    }
    
    #dirs_label {
        color: #cdd6f4;
        text-align: left;
        height: auto;
    }

    /* Top toolbar */
    #toolbar {
        height: 3;
        padding: 0;
        margin: 0 0 0 0;
        content-align: left middle;
    }
    
    /* Button styling */
    Button {
        margin: 0 1;
        height: 3;
        min-width: 12;
        width: 12;
        padding: 0 2;
        background: #45475a;
        color: #cdd6f4;
        border: round #6c7086;
        content-align: center middle;
    }
    
    Button:hover {
        background: #585b70;
        border: round #89b4fa;
    }
    
    Button:focus {
        border: round #f38ba8;
    }
    
    Button:disabled {
        opacity: 0.6;
        content-align: center middle;
        width: 12;
        min-width: 12;
    }
    
    Button.-primary {
        background: #89b4fa;
        color: #1e1e2e;
        border: round #b4befe;
    }
    
    Button.-primary:hover {
        background: #b4befe;
    }
    
    Button.-success {
        background: #a6e3a1;
        color: #1e1e2e;
    }
    
    Button.-success:hover {
        background: #b8e8b3;
    }
    
    Button.-error {
        background: #f38ba8;
        color: #1e1e2e;
    }
    
    Button.-error:hover {
        background: #f5a3b8;
    }
    
    Horizontal {
        height: auto;
    }
    
    /* Progress bar */
    ProgressBar {
        background: #313244;
        border: round #89b4fa;
        margin: 1 0;
    }
    
    ProgressBar > .bar--bar {
        color: #a6e3a1;
    }
    
    /* Status labels */
    .status-text {
        background: #313244;
        padding: 1 2;
        margin: 0 0 1 0;
        border: round #89b4fa;
        color: #cdd6f4;
    }
    
    /* Activity log */
    #activity_log {
        height: 20;
        border: round #89b4fa;
        background: #313244;
        min-height: 20;
        max-height: 20;
        margin: 0 0;
    }
    
    #activity_log > ListItem {
        padding: 0 1;
        color: #cdd6f4;
    }
    
    #activity_log > ListItem:hover {
        background: #45475a;
    }
    
    /* DataTable */
    DataTable {
        border: round #89b4fa;
        background: #313244;
    }
    
    DataTable > .datatable--header {
        background: #45475a;
        color: #89b4fa;
        text-style: bold;
    }
    
    /* Input fields */
    Input {
        border: round #89b4fa;
        background: #313244;
        padding: 1 2;
        margin: 1 0;
        color: #cdd6f4;
    }
    
    Input:focus {
        border: round #f38ba8;
    }
    
    /* Notifications */
    .notification.success {
        background: #a6e3a1;
        color: #1e1e2e;
    }
    
    .notification.error {
        background: #f38ba8;
        color: #1e1e2e;
    }
    
    .notification.warning {
        background: #f9e2af;
        color: #1e1e2e;
    }
    
    /* Skiplist */
    .skiplist-item {
        color: #9399b2;
    }
    
    .remove-button {
        background: #f38ba8;
        color: #1e1e2e;
        min-width: 12;
    }
    
    .remove-button:hover {
        background: #f5a3b8;
    }
    
    ListView {
        height: 60%;
        border: round #89b4fa;
        background: #313244;
    }
    
    #skiplist_list {
        height: 10;
        margin: 1 0;
    }
    
    /* Results container */
    .results-container {
        height: 20;
        max-height: 20;
        overflow-y: auto;
        border: round #89b4fa;
        background: #313244;
        margin: 1 0;
    }
    
    /* Modal */
    DirModal {
        align: center middle;
    }
    
    DirModal > Vertical {
        background: #313244;
        border: thick #89b4fa;
        padding: 2;
        width: 60;
    }
    
    DirModal Label {
        text-align: center;
        text-style: bold;
        color: #89b4fa;
        margin-bottom: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.title = "Symlink Checker TUI"
        self.config = load_config()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Container(
                    Static(f"📁 Symlink: {self.config['symlinked_dir']}\n📂 Apps: {self.config['apps_dir']}", id="dirs_label"),
                    classes="dirs-container"
                ),
                Horizontal(
                    Button("🔍 Check", id="run_check", variant="primary"),
                    Button("⚙️ Symlink", id="set_sym"),
                    Button("⚙️ Apps", id="set_apps"),
                    Button("📋 Skip", id="skiplist"),
                    Button("❌ Exit", id="exit", variant="error"),
                    id="toolbar"
                ),
                ListView(id="activity_log"),
                id="menu"
            )
        )
        yield Footer()

    @on(Button.Pressed, "#run_check")
    async def run_check(self):
        await self._perform_check()

    async def _perform_check(self):
        in_orde = []
        bijzonderheden = []
        # Auto-process mode: always fix broken symlinks without user interaction
        alles_automatisch = True
        dir_path = self.config["symlinked_dir"]
        apps_path = self.config["apps_dir"]
        skiplist = lees_skiplist()
        items = [item for item in os.listdir(dir_path) if item.endswith('.app') and not item.startswith('.')]
        total = len(items)
        if total == 0:
            self.notify("⚠️ Geen .app items gevonden in de directory.", severity="warning")
            return
        progress = ProgressBar(total=total)
        status_label = Label("⏳ Checking: " + items[0] if items else "", classes="status-text")
        details_label = Label("", classes="status-text")
        self.mount(progress)
        self.mount(status_label)
        self.mount(details_label)
        activity_log = self.query_one("#activity_log", ListView)
        activity_log.clear()
        current = 0
        for item in items:
            current += 1
            progress.advance(1)
            status_label.update(f"⏳ Checking: {item} ({current}/{total})")
            details_label.update("")
            await asyncio.sleep(0.01)  # Allow UI to update

            if item in skiplist:
                msg = f"[SKIP] {item} staat in de skiplist, wordt overgeslagen."
                bijzonderheden.append(msg)
                details_label.update(msg)
                new_item = ListItem(Label(msg))
                activity_log.append(new_item)
                new_item.scroll_visible()
                await asyncio.sleep(0.1)
                continue

            app_path = os.path.join(apps_path, item)
            if not os.path.exists(app_path):
                msg = f"[!] {item} bestaat niet in {apps_path}"
                bijzonderheden.append(msg)
                details_label.update(msg)
                new_item = ListItem(Label(msg))
                activity_log.append(new_item)
                new_item.scroll_visible()
                await asyncio.sleep(0.1)
                continue

            if is_symlink(app_path):
                in_orde.append(item)
                details_label.update(f"✓ {item} is een geldige symlink")
                new_item = ListItem(Label(f"✓ {item} is een geldige symlink"))
                activity_log.append(new_item)
                new_item.scroll_visible()
                await asyncio.sleep(0.1)
                continue

            msg = f"[!] {item} is GEEN symlink meer in {apps_path}"
            bijzonderheden.append(msg)
            details_label.update(msg)
            new_item = ListItem(Label(msg))
            activity_log.append(new_item)
            new_item.scroll_visible()
            await asyncio.sleep(0.1)

            # Auto-process: always fix broken symlinks
            antwoord = 'j'
            if antwoord == 'j':
                nieuwe_locatie = os.path.join(dir_path, item)
                try:
                    details_label.update(f"📦 Verplaatsen: {item}...")
                    await asyncio.sleep(0.05)
                    new_item = ListItem(Label(f"📦 Verplaatsen: {item}..."))
                    activity_log.append(new_item)
                    new_item.scroll_visible()

                    if os.path.exists(nieuwe_locatie):
                        details_label.update(f"🗑️ Verwijderen oude: {item}...")
                        await asyncio.sleep(0.05)
                        new_item = ListItem(Label(f"🗑️ Verwijderen oude: {item}..."))
                        activity_log.append(new_item)
                        new_item.scroll_visible()
                        if os.path.isdir(nieuwe_locatie) and not os.path.islink(nieuwe_locatie):
                            shutil.rmtree(nieuwe_locatie)
                        else:
                            os.remove(nieuwe_locatie)

                    details_label.update(f"📤 Verplaatsen naar: {item}...")
                    await asyncio.sleep(0.05)
                    new_item = ListItem(Label(f"📤 Verplaatsen naar: {item}..."))
                    activity_log.append(new_item)
                    new_item.scroll_visible()
                    shutil.move(app_path, nieuwe_locatie)

                    details_label.update(f"🔗 Symlink aanmaken: {item}...")
                    await asyncio.sleep(0.05)
                    new_item = ListItem(Label(f"🔗 Symlink aanmaken: {item}..."))
                    activity_log.append(new_item)
                    new_item.scroll_visible()
                    os.symlink(nieuwe_locatie, app_path)

                    msg = f"[OK] {item} verwerkt: verplaatst en symlink opnieuw aangemaakt."
                    bijzonderheden.append(msg)
                    details_label.update(f"✓ {item} succesvol verwerkt!")
                    new_item = ListItem(Label(f"✓ {item} succesvol verwerkt!"))
                    activity_log.append(new_item)
                    new_item.scroll_visible()
                    await asyncio.sleep(0.1)
                except Exception as e:
                    msg = f"[FOUT] Probleem met {item}: {e}"
                    bijzonderheden.append(msg)
                    details_label.update(f"✗ Fout bij {item}: {str(e)}")
                    new_item = ListItem(Label(f"✗ Fout bij {item}: {str(e)}"))
                    activity_log.append(new_item)
                    new_item.scroll_visible()
                    await asyncio.sleep(0.1)
            elif antwoord == 'n':
                bijzonderheden.append(f"[N] {item} handmatig overgeslagen.")

        progress.remove()
        status_label.remove()
        details_label.remove()
        self.post_message(CheckComplete(in_orde, bijzonderheden))

    @on(CheckComplete)
    def show_results(self, msg: CheckComplete):
        self.push_screen(ResultsScreen(msg.in_orde, msg.bijzonderheden))

    @on(Button.Pressed, "#set_sym")
    def set_sym_dir(self):
        self.push_screen(DirModal("Symlink Directory instellen", self.config["symlinked_dir"], "symlinked_dir"))

    @on(Button.Pressed, "#set_apps")
    def set_apps_dir(self):
        self.push_screen(DirModal("Apps Directory instellen", self.config["apps_dir"], "apps_dir"))

    @on(DirUpdated)
    def update_dir_labels(self, msg: DirUpdated):
        if msg.key == "symlinked_dir":
            self.config["symlinked_dir"] = msg.dir_path
        elif msg.key == "apps_dir":
            self.config["apps_dir"] = msg.dir_path
        self.query_one("#dirs_label", Static).update(f"📁 Symlink: {self.config['symlinked_dir']}\n📂 Apps: {self.config['apps_dir']}")

    @on(Button.Pressed, "#skiplist")
    def open_skiplist(self):
        self.push_screen(SkiplistScreen())

    @on(Button.Pressed, "#exit")
    def exit_app(self):
        self.exit()

    def on_confirm_quit(self, event):
        event.confirm = True

    def key_q(self):
        """Afsluiten met Q toets"""
        self.exit()

    def key_escape(self):
        """Afsluiten met Escape toets"""
        self.exit()

    def key_up(self):
        """Navigeer omhoog met pijltjestoets"""
        self.run_action("focus_previous")

    def key_down(self):
        """Navigeer omlaag met pijltjestoets"""
        self.run_action("focus_next")

    def key_left(self):
        """Navigeer links met pijltjestoets"""
        # Voor horizontale menu's: ga naar vorige knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de vorige
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index > 0:
                buttons[current_index - 1].focus()
            else:
                self.run_action("focus_previous")

    def key_right(self):
        """Navigeer rechts met pijltjestoets"""
        # Voor horizontale menu's: ga naar volgende knop
        current_focus = self.focused
        if current_focus and hasattr(current_focus, 'id'):
            # Zoek de huidige knop en ga naar de volgende
            buttons = self.query("Button")
            current_index = None
            for i, button in enumerate(buttons):
                if button == current_focus:
                    current_index = i
                    break
            
            if current_index is not None and current_index < len(buttons) - 1:
                buttons[current_index + 1].focus()
            else:
                self.run_action("focus_next")


if __name__ == "__main__":
    import sys
    
    # Controleer of het script met root rechten wordt uitgevoerd
    if os.geteuid() != 0:
        print("❌ Dit script vereist root rechten.")
        print("Voer het script uit met: sudo python3 symlink_checker.py")
        sys.exit(1)
    
    app = SymlinkCheckerApp()
    app.run()
