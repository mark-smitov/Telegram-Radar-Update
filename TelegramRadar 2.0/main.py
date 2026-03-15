import os
import sys
import shutil
import asyncio
import importlib
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

load_dotenv()

MC = "deep_sky_blue1"
AC = "white"
DIM = "dim"

if os.name == "nt":
    try:
        os.system("chcp 65001 > nul")
    except Exception:
        pass

for _stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None), getattr(sys, "stdin", None)):
    try:
        if _stream and hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

_term_width = shutil.get_terminal_size((120, 30)).columns
console = Console(
    force_terminal=True,
    color_system="truecolor",
    legacy_windows=False,
    width=_term_width,
)

API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION  = str(Path(__file__).parent / os.getenv("SESSION_NAME", "telegram_radar"))

BANNER_RAW = "\n".join(
    [
        r" /$$$$$$$$        /$$                                                          /$$$$$$$                  /$$                  ",
        r"|__  $$__/       | $$                                                         | $$__  $$                | $$                  ",
        r"   | $$  /$$$$$$ | $$  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$/$$$$       | $$  \\ $$  /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ ",
        r"   | $$ /$$__  $$| $$ /$$__  $$ /$$__  $$ /$$__  $$|____  $$| $$_  $$_  $$      | $$$$$$$/ |____  $$ /$$__  $$ |____  $$ /$$__  $$",
        r"   | $$| $$$$$$$$| $$| $$$$$$$$| $$  \\ $$| $$  \\__/ /$$$$$$$| $$ \\ $$ \\ $$      | $$__  $$  /$$$$$$$| $$  | $$  /$$$$$$$| $$  \\__/",
        r"   | $$| $$_____/| $$| $$_____/| $$  | $$| $$      /$$__  $$| $$ | $$ | $$      | $$  \\ $$ /$$__  $$| $$  | $$ /$$__  $$| $$      ",
        r"   | $$|  $$$$$$$| $$|  $$$$$$$|  $$$$$$$| $$     |  $$$$$$$| $$ | $$ | $$      | $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$      ",
        r"   |__/ \\_______/|__/ \\_______/ \\____  $$|__/      \\_______/|__/ |__/ |__/      |__/  |__/ \\_______/ \\_______/ \\_______/|__/      ",
        r"                                /$$  \\ $$                                                                                         ",
        r"                               |  $$$$$$/                                                                                         ",
        r"                                \\______/                                                                                          ",
    ]
)

MENU_ITEMS = [
    ("Мониторинг Группы",       "modules.monitoring_group",               "run"),
    ("Статистика Группы",       "modules.static_group",                   "run"),
    ("Экспорт данных",          "modules.export",                         "run"),
    ("Добавить участника/бота", "modules.add_member",                     "run"),
    ("Управление правами",      "modules.rights_management",              "run"),
    ("Блокировка участника",    "modules.ban_member",                     "run"),
    ("Настройки",               "modules.settings",                       "run"),
    ("Личные чаты",             "modules.personal_chats",                 "run"),
    ("Скрапинг сообщений",      "modules.scrapping",                      "run"),
    ("Чат с нейросетью",        "modules.chat_ai",                        "run"),
    ("Отправить сообщение",     "modules.send",                           "run"),
    ("Отчет мониторингов",      "modules.reports_all",                    "run"),
    ("Управление каналом",      "modules.management_channel",             "run"),
    ("Выгрузка сообщений",      "modules.export_message_from_favourites", "run"),
    ("Выгрузка медиа",          "modules.export_media_from_favourites",   "run"),
]


def _menu_block(start: int, end: int) -> Table:
    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {MC}", no_wrap=True, width=5)
    t.add_column(style=AC, no_wrap=True)
    if start == 0:
        t.add_row(f"[bold {MC}][00][/]", f"[{AC}]Выход[/]")
    for i in range(start, min(end, len(MENU_ITEMS))):
        t.add_row(f"[{i+1:02d}]", MENU_ITEMS[i][0])
    return t


def _info_block() -> Table:
    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {MC}", no_wrap=True, min_width=12)
    t.add_column(style=AC, no_wrap=False)
    for label, value in [
        ("Channel:", "t.me/adaptBlackSerch"),
        ("Github:",  "github.com/mark-smitov"),
        ("Coder:",   "@vksmitov"),
        ("Version:", "2.0.0"),
    ]:
        t.add_row(label, value)
    return t


def _account_block(me, chats: int, channels: int, groups: int, bio: str) -> Table:
    uname   = f"@{me.username}" if me.username else f"{me.first_name or ''} {me.last_name or ''}".strip() or "—"
    bio_str = (bio[:30] + "...") if len(bio) > 30 else (bio or "—")
    premium = bool(getattr(me, "premium", False))

    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {MC}", no_wrap=True, min_width=12)
    t.add_column(style=AC, no_wrap=False)
    for label, value in [
        ("User:",    uname),
        ("ID:",      str(me.id)),
        ("Premium:", "[green][OK] Да[/]" if premium else "[red][NO] Нет[/]"),
        ("Чаты:",    str(chats)),
        ("Каналы:",  str(channels)),
        ("Группы:",  str(groups)),
        ("Bio:",     bio_str),
    ]:
        t.add_row(label, value)
    return t


def render(me=None, chats: int = 0, channels: int = 0, groups: int = 0, bio: str = "—"):
    os.system("cls" if os.name == "nt" else "clear")

    console.print(Panel(
        Align.center(Text(BANNER_RAW, style=MC, no_wrap=True)),
        border_style=MC,
        box=box.SQUARE,
        padding=(0, 1),
    ))

    grid = Table.grid(expand=True)
    grid.add_column(ratio=2)
    grid.add_column(ratio=2)
    grid.add_column(ratio=2)

    right_col = Table.grid(expand=True)
    right_col.add_column()
    right_col.add_row(Panel(
        _info_block(),
        title=f"[bold {MC}] Информация [/]",
        border_style=MC,
        box=box.SQUARE,
        padding=(0, 2),
    ))
    right_col.add_row(Panel(
        _account_block(me, chats, channels, groups, bio) if me
        else Text("Подключение...", style=DIM, justify="center"),
        title=f"[bold {MC}] Аккаунт [/]",
        border_style=MC if me else DIM,
        box=box.SQUARE,
        padding=(0, 2),
    ))

    grid.add_row(
        Panel(_menu_block(0, 8),  title=f"[bold {MC}] Функции I [/]",  border_style=MC, box=box.SQUARE, padding=(1, 2)),
        Panel(_menu_block(8, 15), title=f"[bold {MC}] Функции II [/]", border_style=MC, box=box.SQUARE, padding=(1, 2)),
        right_col,
    )

    console.print(grid)
    console.print(f"\n[bold {MC}]$root[/] [white]>[/] ", end="")


async def _authorize(client: TelegramClient):
    await client.connect()
    if await client.is_user_authorized():
        return
    try:
        phone = console.input(f"[{MC}]Телефон:[/] ")
    except EOFError:
        raise RuntimeError("Ввод прерван.")
    await client.send_code_request(phone)
    try:
        code = console.input(f"[{MC}]Код из Telegram:[/] ")
    except EOFError:
        raise RuntimeError("Ввод прерван.")
    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        try:
            pw = console.input(f"[{MC}]Пароль 2FA:[/] ")
        except EOFError:
            raise RuntimeError("Ввод прерван.")
        await client.sign_in(password=pw)


async def _fetch_stats(client: TelegramClient):
    from telethon.tl.functions.users import GetFullUserRequest
    me  = await client.get_me()
    bio = "—"
    try:
        full = await client(GetFullUserRequest(me.id))
        bio  = getattr(full.full_user, "about", None) or "—"
    except Exception:
        pass
    dialogs  = await client.get_dialogs(limit=500)
    channels = sum(1 for d in dialogs if d.is_channel and not d.is_group)
    groups   = sum(1 for d in dialogs if d.is_group)
    chats    = sum(1 for d in dialogs if d.is_user and not getattr(d.entity, "bot", False))
    return me, chats, channels, groups, bio


async def main():
    if not API_ID or not API_HASH:
        console.print(Panel(
            "[bold red]Ошибка:[/] API_ID / API_HASH не найдены.\n"
            "Укажите их в файле [bold].env[/].",
            border_style="red", box=box.SQUARE,
        ))
        return

    client = TelegramClient(SESSION, API_ID, API_HASH)
    try:
        await _authorize(client)
    except Exception as e:
        console.print(Panel(
            f"[bold red]Ошибка авторизации:[/] {e}",
            border_style="red", box=box.SQUARE,
        ))
        await client.disconnect()
        return

    me, chats, channels, groups, bio = await _fetch_stats(client)

    while True:
        render(me, chats, channels, groups, bio)
        try:
            raw = input().strip()
            choice = int(raw)
        except EOFError:
            break
        except ValueError:
            continue

        if choice == 0:
            os.system("cls" if os.name == "nt" else "clear")
            console.print(Panel(
                f"[bold {MC}]Сессия сохранена.[/]\nДо свидания!",
                border_style=MC, box=box.SQUARE, expand=False,
            ))
            break

        if not (1 <= choice <= len(MENU_ITEMS)):
            console.print(f"[red]Введите 0–{len(MENU_ITEMS)}[/]")
            await asyncio.sleep(1)
            continue

        label, mod_path, func_name = MENU_ITEMS[choice - 1]
        try:
            mod = importlib.import_module(mod_path)
            importlib.reload(mod)
            await getattr(mod, func_name)(client)
        except Exception as exc:
            console.print(f"[red]Ошибка [{label}]: {exc}[/]")
            input("Enter для продолжения...")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
