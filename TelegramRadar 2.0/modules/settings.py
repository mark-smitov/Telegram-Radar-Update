import os
import json
from pathlib import Path
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

CONFIG_FILE = Path("config.json")

THEMES = {
    "1": ("Синий (по умолчанию)", "deep_sky_blue1"),
    "2": ("Зелёный",              "bright_green"),
    "3": ("Красный",              "bright_red"),
    "4": ("Жёлтый",               "bright_yellow"),
    "5": ("Фиолетовый",           "medium_purple"),
    "6": ("Циан",                 "cyan"),
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}

def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))

async def run(client):
    header("⚙️   Настройки")

    cfg = load_config()

    console.print(f"""
[{MC}][1][/] Сменить цвет темы
[{MC}][2][/] Информация о текущей сессии
[{MC}][3][/] Завершить текущую сессию (выход)
[{MC}][4][/] Список активных сессий
[{MC}][0][/] Назад
""")
    action = ask("Действие", "0")

    if action == "1":
        tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
        tbl.add_column("#", style=MC, width=3)
        tbl.add_column("Название", style=AC)
        tbl.add_column("Код", style=MC)
        for k, (name, code) in THEMES.items():
            tbl.add_row(k, name, f"[{code}]{code}[/]")
        console.print(tbl)
        choice = ask("Номер темы", "1")
        if choice in THEMES:
            cfg["theme"] = THEMES[choice][1]
            save_config(cfg)
            console.print(f"[green][OK] Тема сохранена. Перезапустите утилиту.[/]")
        else:
            console.print("[red]Неверный выбор[/]")

    elif action == "2":
        me = await client.get_me()
        info = Table(border_style=MC, box=box.SIMPLE_HEAD)
        info.add_column("Поле",       style=MC)
        info.add_column("Значение",   style=AC)
        info.add_row("Имя",      f"{me.first_name or ''} {me.last_name or ''}".strip())
        info.add_row("Username", f"@{me.username}" if me.username else "—")
        info.add_row("ID",       str(me.id))
        info.add_row("Телефон",  me.phone or "—")
        info.add_row("Премиум",  "[OK]" if getattr(me, "premium", False) else "[NO]")
        console.print(info)

    elif action == "3":
        confirm = ask("Выйти из аккаунта? (yes/no)", "no")
        if confirm.lower() == "yes":
            await client.log_out()
            console.print("[green][OK] Сессия завершена. Перезапустите утилиту.[/]")

    elif action == "4":
        from telethon.tl.functions.account import GetAuthorizationsRequest
        try:
            auths = await client(GetAuthorizationsRequest())
            tbl = Table(title="Активные сессии", border_style=MC, box=box.SIMPLE_HEAD)
            tbl.add_column("#",          style=MC, width=3)
            tbl.add_column("Устройство", style=AC)
            tbl.add_column("Платформа",  style=AC)
            tbl.add_column("IP",         style=MC)
            tbl.add_column("Текущая",    style=MC, width=8)
            for i, a in enumerate(auths.authorizations, 1):
                tbl.add_row(
                    str(i),
                    a.device_model,
                    a.platform,
                    a.ip,
                    "[OK]" if a.current else "",
                )
            console.print(tbl)
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    pause()
