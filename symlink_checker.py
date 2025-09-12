import os
import shutil
import json
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header, Footer, Button, Input, ListView, ListItem, Label, Static, 
    ProgressBar
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
                self.app.notify("Directory bijgewerkt", severity="success")
            else:
                self.app.notify("Ongeldige directory", severity="error")
        elif event.button.id == "exit":
            self.app.exit()
        self.dismiss()

    def key_q(self):
        """Afsluiten met Q toets"""
        self.app.exit()

    def key_escape(self):
        """Afsluiten met Escape toets"""
        self.app.exit()


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
            ListView(*[ListItem(Label(item)) for item in skiplist], id="skiplist_list"),
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
                self.query_one(ListView).append(ListItem(Label(app)))
                self.app.notify(f"{app} toegevoegd", severity="success")
                self.query_one("#add_input").value = ""
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


class ResultsScreen(Screen):
    def __init__(self, in_orde: List[str], bijzonderheden: List[str]):
        self.in_orde = in_orde
        self.bijzonderheden = bijzonderheden
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Resultaten"),
            Label(f"In orde ({len(self.in_orde)}):"),
            ListView(*[ListItem(Label(app)) for app in self.in_orde], id="in_orde_list"),
            Label("Bijzonderheden:"),
            ListView(*[ListItem(Label(b)) for b in self.bijzonderheden], id="bijzonderheden_list"),
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


class SymlinkCheckerApp(App):
    CSS = """
    SymlinkCheckerApp {
        align: center middle;
    }
    #menu {
        height: 100%;
    }
    Button {
        margin: 1;
    }
    ListView {
        height: 60%;
    }
    #in_orde_list {
        height: 8;
    }
    #bijzonderheden_list {
        height: 8;
    }
    #skiplist_list {
        height: 10;
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
                Label(f"Symlink Dir: {self.config['symlinked_dir']}", id="sym_dir_label"),
                Label(f"Apps Dir: {self.config['apps_dir']}", id="apps_dir_label"),
                Horizontal(
                    Button("Voer check uit", id="run_check", variant="primary"),
                    Button("Stel symlink dir in", id="set_sym"),
                    Button("Stel apps dir in", id="set_apps"),
                    Button("Skiplist beheren", id="skiplist"),
                ),
                Horizontal(
                    Button("Afsluiten", id="exit", variant="error"),
                ),
                id="menu"
            )
        )
        yield Footer()

    @on(Button.Pressed, "#run_check")
    def run_check(self):
        self._perform_check()

    def _perform_check(self):
        in_orde = []
        bijzonderheden = []
        alles_automatisch = False
        dir_path = self.config["symlinked_dir"]
        apps_path = self.config["apps_dir"]
        skiplist = lees_skiplist()
        items = [item for item in os.listdir(dir_path) if item.endswith('.app') and not item.startswith('.')]
        total = len(items)
        if total == 0:
            self.notify("Geen .app items gevonden in de directory.", severity="warning")
            return
        progress = ProgressBar(total=total)
        self.mount(progress)
        current = 0
        for item in items:
            current += 1
            progress.advance(1)
            if item in skiplist:
                bijzonderheden.append(f"[SKIP] {item} staat in de skiplist, wordt overgeslagen.")
                continue
            app_path = os.path.join(apps_path, item)
            if not os.path.exists(app_path):
                bijzonderheden.append(f"[!] {item} bestaat niet in {apps_path}")
                continue
            if is_symlink(app_path):
                in_orde.append(item)
                continue
            bijzonderheden.append(f"[!] {item} is GEEN symlink meer in {apps_path}")
            # For demo, auto-yes; in full, use a modal to pause and get input
            antwoord = 'j'  # Auto for test
            if antwoord == 'j':
                nieuwe_locatie = os.path.join(dir_path, item)
                try:
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
        progress.remove()
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
            self.query_one("#sym_dir_label", Label).update(f"Symlink Dir: {msg.dir_path}")
        elif msg.key == "apps_dir":
            self.config["apps_dir"] = msg.dir_path
            self.query_one("#apps_dir_label", Label).update(f"Apps Dir: {msg.dir_path}")

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


if __name__ == "__main__":
    app = SymlinkCheckerApp()
    app.run()
