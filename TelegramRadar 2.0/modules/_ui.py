import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

MC = "deep_sky_blue1"
AC = "white"
console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(title: str):
    clear()
    console.print(
        Panel(f"[bold {MC}]{title}[/]", border_style=MC, box=box.ROUNDED, expand=False)
    )
    console.print()

def pause(msg: str = "Нажмите Enter для продолжения..."):
    console.print(f"\n[{MC}]{msg}[/]")
    input()

def ask(prompt: str, default: str = "") -> str:
    return Prompt.ask(f"[{MC}]{prompt}[/]", default=default)

def pick_dialog(client_sync, dialogs, kind: str = "всех") -> object | None:
    from rich.table import Table
    table = Table(title=f"Выберите из {kind}", border_style=MC, box=box.SIMPLE_HEAD)
    table.add_column("#",    style=MC, width=5)
    table.add_column("Название", style=AC)
    table.add_column("ID",   style=MC)
    for i, d in enumerate(dialogs, 1):
        table.add_row(str(i), d.name or "N/A", str(d.id))
    console.print(table)
    try:
        idx = int(ask("Номер")) - 1
        if 0 <= idx < len(dialogs):
            return dialogs[idx]
    except ValueError:
        pass
    return None
