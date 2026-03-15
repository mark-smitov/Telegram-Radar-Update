from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from datetime import datetime, timezone
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

FULL_BAN = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN = ChatBannedRights(until_date=None)

async def run(client):
    header("[BAN]   Блокировка Участника / Бота")

    groups = [d for d in await client.get_dialogs() if d.is_group or d.is_channel]
    if not groups:
        console.print("[red]Группы не найдены[/]"); pause(); return

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=4)
    tbl.add_column("Название", style=AC)
    for i, g in enumerate(groups, 1):
        tbl.add_row(str(i), g.name or "N/A")
    console.print(tbl)

    try:
        idx   = int(ask("Выберите группу")) - 1
        group = groups[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    action = ask("Действие: [1] Заблокировать  [2] Разблокировать", "1")
    ban    = action.strip() != "2"

    raw     = ask("Username или ID (через запятую)")
    targets = [t.strip() for t in raw.split(",") if t.strip()]

    res_tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    res_tbl.add_column("Цель",      style=AC)
    res_tbl.add_column("Результат", style=AC)

    for t in targets:
        try:
            uid  = int(t) if t.lstrip("-").isdigit() else t
            user = await client.get_entity(uid)
            await client(EditBannedRequest(
                channel=group.entity,
                participant=user,
                banned_rights=FULL_BAN if ban else UNBAN,
            ))
            verb = "[red][OK] Заблокирован[/]" if ban else "[green][OK] Разблокирован[/]"
            res_tbl.add_row(str(t), verb)
        except Exception as e:
            res_tbl.add_row(str(t), f"[red]Ошибка: {e}[/]")

    console.print(res_tbl)
    pause()
