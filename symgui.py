#!/usr/bin/env python3
"""
Symlink Checker - NiceGUI Web Interface
Een web-based GUI voor het beheren van symlinks tussen SYMLINKED en /Applications
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Set
from nicegui import ui, app
from dataclasses import dataclass

# Config bestanden
CONFIG_FILE = Path(__file__).parent / "config.json"
SKIPLIST_FILE = Path(__file__).parent / "skiplist.txt"


@dataclass
class AppStatus:
    """Status van een app"""
    name: str
    status: str  # 'ok', 'missing', 'real_app', 'error'
    message: str = ""


def load_config() -> Dict[str, str]:
    """Laad configuratie uit JSON bestand"""
    default_config = {
        "symlinked_dir": "/Volumes/MMKMINI/SYMLINKED",
        "apps_dir": "/Applications"
    }
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config: Dict[str, str]) -> None:
    """Sla configuratie op in JSON bestand"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_skiplist() -> Set[str]:
    """Laad skiplist uit bestand"""
    if not SKIPLIST_FILE.exists():
        return set()
    with open(SKIPLIST_FILE, 'r') as f:
        return {line.strip() for line in f if line.strip()}


def save_skiplist(skiplist: Set[str]) -> None:
    """Sla skiplist op in bestand"""
    with open(SKIPLIST_FILE, 'w') as f:
        for app in sorted(skiplist):
            f.write(f"{app}\n")


def add_to_skiplist(app_name: str) -> None:
    """Voeg app toe aan skiplist"""
    skiplist = load_skiplist()
    skiplist.add(app_name)
    save_skiplist(skiplist)


def remove_from_skiplist(app_name: str) -> None:
    """Verwijder app uit skiplist"""
    skiplist = load_skiplist()
    skiplist.discard(app_name)
    save_skiplist(skiplist)


def check_symlinks(config: Dict[str, str], skiplist: Set[str]) -> List[AppStatus]:
    """Controleer alle symlinks"""
    results = []
    symlinked_dir = Path(config['symlinked_dir'])
    apps_dir = Path(config['apps_dir'])

    if not symlinked_dir.exists():
        return [AppStatus("ERROR", "error", f"SYMLINKED directory niet gevonden: {symlinked_dir}")]

    # Haal alle .app bundels op
    apps = sorted([f for f in symlinked_dir.iterdir() if f.name.endswith('.app')])

    for app_path in apps:
        app_name = app_path.name

        # Skip apps in skiplist
        if app_name in skiplist:
            results.append(AppStatus(app_name, "skipped", "In skiplist"))
            continue

        target_path = apps_dir / app_name

        # Check of symlink bestaat
        if not target_path.exists():
            results.append(AppStatus(app_name, "missing", "Symlink niet gevonden"))
            continue

        # Check of het een symlink is
        if not target_path.is_symlink():
            results.append(AppStatus(app_name, "real_app", "Echte app in /Applications"))
            continue

        # Check of symlink naar juiste locatie wijst
        if target_path.resolve() == app_path.resolve():
            results.append(AppStatus(app_name, "ok", "✓ Symlink OK"))
        else:
            results.append(AppStatus(app_name, "wrong_target",
                                   f"Wijst naar verkeerde locatie: {target_path.resolve()}"))

    return results


def move_and_symlink(app_name: str, config: Dict[str, str]) -> tuple[bool, str]:
    """Verplaats echte app naar SYMLINKED en maak symlink"""
    try:
        symlinked_dir = Path(config['symlinked_dir'])
        apps_dir = Path(config['apps_dir'])

        source = apps_dir / app_name
        target = symlinked_dir / app_name

        # Verplaats echte app
        if target.exists():
            shutil.rmtree(target)

        shutil.move(str(source), str(target))

        # Maak symlink
        os.symlink(target, source)

        return True, f"✓ {app_name} succesvol verplaatst en symlink aangemaakt"

    except Exception as e:
        return False, f"✗ Fout bij {app_name}: {str(e)}"


def create_symlink(app_name: str, config: Dict[str, str]) -> tuple[bool, str]:
    """Maak symlink voor missing app"""
    try:
        symlinked_dir = Path(config['symlinked_dir'])
        apps_dir = Path(config['apps_dir'])

        source = symlinked_dir / app_name
        target = apps_dir / app_name

        if not source.exists():
            return False, f"✗ {app_name} niet gevonden in SYMLINKED"

        # Maak symlink
        os.symlink(source, target)

        return True, f"✓ Symlink aangemaakt voor {app_name}"

    except Exception as e:
        return False, f"✗ Fout bij {app_name}: {str(e)}"


# Global state
state = {
    'config': load_config(),
    'skiplist': load_skiplist(),
    'results': [],
    'scanning': False
}


@ui.page('/')
def main_page():
    """Hoofd pagina met overzicht en scan functionaliteit"""

    def scan_apps():
        """Scan alle apps"""
        state['scanning'] = True
        scan_btn.disable()
        results_container.clear()

        with results_container:
            ui.label('Scannen...').classes('text-xl')

        # Voer scan uit
        state['results'] = check_symlinks(state['config'], state['skiplist'])
        state['scanning'] = False

        # Toon resultaten
        show_results()
        scan_btn.enable()

    def show_results():
        """Toon scan resultaten"""
        results_container.clear()

        if not state['results']:
            with results_container:
                ui.label('Geen resultaten. Klik op "Scan Apps" om te beginnen.').classes('text-gray-500')
            return

        # Statistieken
        ok_count = sum(1 for r in state['results'] if r.status == 'ok')
        problem_count = sum(1 for r in state['results'] if r.status in ['missing', 'real_app', 'wrong_target'])
        skipped_count = sum(1 for r in state['results'] if r.status == 'skipped')

        with results_container:
            # Stats cards
            with ui.row().classes('w-full gap-4 mb-4'):
                with ui.card().classes('flex-1 bg-green-50'):
                    ui.label(f'{ok_count}').classes('text-3xl font-bold text-green-600')
                    ui.label('OK').classes('text-gray-600')

                with ui.card().classes('flex-1 bg-yellow-50'):
                    ui.label(f'{problem_count}').classes('text-3xl font-bold text-yellow-600')
                    ui.label('Problemen').classes('text-gray-600')

                with ui.card().classes('flex-1 bg-gray-50'):
                    ui.label(f'{skipped_count}').classes('text-3xl font-bold text-gray-600')
                    ui.label('Overgeslagen').classes('text-gray-600')

            # Resultaten tabel
            ui.label('Resultaten').classes('text-2xl font-bold mb-4')

            # Groepeer per status
            problems = [r for r in state['results'] if r.status in ['missing', 'real_app', 'wrong_target']]
            ok_apps = [r for r in state['results'] if r.status == 'ok']
            skipped_apps = [r for r in state['results'] if r.status == 'skipped']

            # Toon problemen eerst
            if problems:
                ui.label('⚠️ Apps met problemen').classes('text-xl font-bold text-yellow-600 mt-4')
                for result in problems:
                    show_problem_card(result)

            # Toon OK apps (ingeklapt)
            if ok_apps:
                with ui.expansion('✓ Apps OK', icon='check_circle').classes('w-full mt-4'):
                    ui.label(', '.join(r.name for r in ok_apps)).classes('text-sm text-gray-600')

            # Toon skipped apps (ingeklapt)
            if skipped_apps:
                with ui.expansion('⊘ Overgeslagen apps', icon='block').classes('w-full mt-4'):
                    for result in skipped_apps:
                        with ui.row().classes('w-full items-center gap-2 p-2'):
                            ui.label(result.name).classes('flex-1')
                            ui.button('Verwijder uit skiplist',
                                    on_click=lambda r=result: remove_from_skiplist_and_rescan(r.name),
                                    icon='delete').props('flat dense').classes('text-red-500')

    def show_problem_card(result: AppStatus):
        """Toon kaart voor probleem app"""
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-center gap-4'):
                # App naam en status
                with ui.column().classes('flex-1'):
                    ui.label(result.name).classes('text-lg font-bold')

                    if result.status == 'missing':
                        ui.label('⚠️ Symlink niet gevonden').classes('text-yellow-600')
                    elif result.status == 'real_app':
                        ui.label('⚠️ Echte app in /Applications').classes('text-orange-600')
                    elif result.status == 'wrong_target':
                        ui.label('⚠️ Wijst naar verkeerde locatie').classes('text-red-600')

                    ui.label(result.message).classes('text-sm text-gray-600')

                # Acties
                with ui.row().classes('gap-2'):
                    if result.status == 'real_app':
                        ui.button('Verplaats & Symlink',
                                on_click=lambda r=result: handle_move_and_symlink(r.name),
                                icon='sync').props('color=primary')

                    elif result.status == 'missing':
                        ui.button('Maak Symlink',
                                on_click=lambda r=result: handle_create_symlink(r.name),
                                icon='add_link').props('color=primary')

                    ui.button('Skiplist',
                            on_click=lambda r=result: handle_add_to_skiplist(r.name),
                            icon='block').props('flat color=grey')

    def handle_move_and_symlink(app_name: str):
        """Handle move and symlink actie"""
        success, message = move_and_symlink(app_name, state['config'])

        if success:
            ui.notify(message, type='positive')
            scan_apps()
        else:
            ui.notify(message, type='negative')

    def handle_create_symlink(app_name: str):
        """Handle create symlink actie"""
        success, message = create_symlink(app_name, state['config'])

        if success:
            ui.notify(message, type='positive')
            scan_apps()
        else:
            ui.notify(message, type='negative')

    def handle_add_to_skiplist(app_name: str):
        """Voeg toe aan skiplist"""
        add_to_skiplist(app_name)
        state['skiplist'].add(app_name)
        ui.notify(f'{app_name} toegevoegd aan skiplist', type='info')
        scan_apps()

    def remove_from_skiplist_and_rescan(app_name: str):
        """Verwijder uit skiplist en scan opnieuw"""
        remove_from_skiplist(app_name)
        state['skiplist'].discard(app_name)
        ui.notify(f'{app_name} verwijderd uit skiplist', type='info')
        scan_apps()

    # UI Layout
    with ui.header().classes('items-center justify-between bg-blue-600'):
        ui.label('🔗 Symlink Checker').classes('text-2xl font-bold text-white')
        with ui.row():
            ui.button('Configuratie', on_click=lambda: ui.navigate.to('/config'),
                     icon='settings').props('flat color=white')
            ui.button('Skiplist', on_click=lambda: ui.navigate.to('/skiplist'),
                     icon='list').props('flat color=white')

    with ui.column().classes('w-full max-w-6xl mx-auto p-4 gap-4'):
        # Info card
        with ui.card().classes('w-full'):
            ui.label('Symlink Checker controleert of je apps correct gesymlinkt zijn').classes('text-lg')
            with ui.row().classes('gap-2 text-sm text-gray-600'):
                ui.label(f"📁 SYMLINKED: {state['config']['symlinked_dir']}")
                ui.label(f"📱 Apps: {state['config']['apps_dir']}")

        # Scan knop
        scan_btn = ui.button('🔍 Scan Apps', on_click=scan_apps, icon='search').props('size=lg').classes('w-full')

        # Resultaten container
        results_container = ui.column().classes('w-full gap-4')


@ui.page('/config')
def config_page():
    """Configuratie pagina"""

    def save_and_return():
        """Sla configuratie op en ga terug"""
        state['config']['symlinked_dir'] = symlinked_input.value
        state['config']['apps_dir'] = apps_input.value
        save_config(state['config'])
        ui.notify('Configuratie opgeslagen!', type='positive')
        ui.navigate.to('/')

    # UI Layout
    with ui.header().classes('items-center bg-blue-600'):
        with ui.row().classes('w-full items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
            ui.label('⚙️ Configuratie').classes('text-2xl font-bold text-white')

    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label('Configuratie Instellingen').classes('text-3xl font-bold')

        with ui.card().classes('w-full'):
            ui.label('SYMLINKED Directory').classes('font-bold mb-2')
            ui.label('De map waar je originele .app bundels staan').classes('text-sm text-gray-600 mb-2')
            symlinked_input = ui.input(
                value=state['config']['symlinked_dir'],
                placeholder='/Volumes/MMKMINI/SYMLINKED'
            ).classes('w-full').props('outlined')

        with ui.card().classes('w-full'):
            ui.label('Applications Directory').classes('font-bold mb-2')
            ui.label('De map waar de symlinks komen (meestal /Applications)').classes('text-sm text-gray-600 mb-2')
            apps_input = ui.input(
                value=state['config']['apps_dir'],
                placeholder='/Applications'
            ).classes('w-full').props('outlined')

        with ui.row().classes('gap-4'):
            ui.button('💾 Opslaan en Terug', on_click=save_and_return, icon='save').props('color=primary size=lg')
            ui.button('Annuleren', on_click=lambda: ui.navigate.to('/'), icon='cancel').props('flat')


@ui.page('/skiplist')
def skiplist_page():
    """Skiplist beheer pagina"""

    def refresh_list():
        """Ververs skiplist"""
        skiplist_container.clear()

        skiplist = load_skiplist()
        state['skiplist'] = skiplist

        with skiplist_container:
            if not skiplist:
                ui.label('Geen apps in skiplist').classes('text-gray-500 italic')
            else:
                for app_name in sorted(skiplist):
                    with ui.card().classes('w-full'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label(app_name).classes('text-lg')
                            ui.button('Verwijderen',
                                    on_click=lambda name=app_name: remove_and_refresh(name),
                                    icon='delete').props('flat color=red')

    def remove_and_refresh(app_name: str):
        """Verwijder uit skiplist en ververs"""
        remove_from_skiplist(app_name)
        ui.notify(f'{app_name} verwijderd uit skiplist', type='positive')
        refresh_list()

    def clear_skiplist():
        """Leeg hele skiplist"""
        save_skiplist(set())
        state['skiplist'] = set()
        ui.notify('Skiplist geleegd', type='info')
        refresh_list()

    # UI Layout
    with ui.header().classes('items-center bg-blue-600'):
        with ui.row().classes('w-full items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
            ui.label('📋 Skiplist Beheer').classes('text-2xl font-bold text-white')

    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Skiplist').classes('text-3xl font-bold')
            ui.button('Leeg Skiplist', on_click=clear_skiplist, icon='delete_sweep').props('color=red flat')

        ui.label('Apps in deze lijst worden bij scans overgeslagen').classes('text-gray-600 mb-4')

        skiplist_container = ui.column().classes('w-full gap-4')
        refresh_list()


# Start de app
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Symlink Checker',
        favicon='🔗',
        dark=None,  # Auto dark mode
        reload=False,
        show=True,
        port=8080
    )
