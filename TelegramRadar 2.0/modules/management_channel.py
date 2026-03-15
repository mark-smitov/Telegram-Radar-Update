from telethon.tl.functions.channels import (
    EditTitleRequest, EditPhotoRequest, DeleteChannelRequest,
    GetParticipantsRequest, EditAdminRequest, EditBannedRequest,
)
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch, ChatAdminRights, ChatBannedRights
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("[CH]   Управление Каналом")

    channels = [d for d in await client.get_dialogs() if d.is_channel]
    if not channels:
        console.print("[red]Каналы не найдены[/]"); pause(); return

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=4)
    tbl.add_column("Название", style=AC)
    tbl.add_column("ID", style=MC)
    for i, c in enumerate(channels, 1):
        tbl.add_row(str(i), c.name or "N/A", str(c.id))
    console.print(tbl)

    try:
        idx     = int(ask("Выберите канал")) - 1
        channel = channels[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    entity = channel.entity

    console.print(f"""
[{MC}][1][/] Изменить название
[{MC}][2][/] Список подписчиков
[{MC}][3][/] Получить invite-ссылку
[{MC}][4][/] Выгрузить сообщения канала
[{MC}][5][/] Опубликовать сообщение
[{MC}][6][/] Удалить канал (необратимо!)
[{MC}][0][/] Назад
""")
    action = ask("Действие", "0")

    if action == "1":
        new_title = ask("Новое название")
        if new_title:
            await client(EditTitleRequest(channel=entity, title=new_title))
            console.print("[green][OK] Название изменено[/]")

    elif action == "2":
        result = await client(GetParticipantsRequest(
            channel=entity, filter=ChannelParticipantsSearch(""),
            offset=0, limit=200, hash=0
        ))
        sub_tbl = Table(title=f"Подписчики [{channel.name}] — {result.count}",
                        border_style=MC, box=box.SIMPLE_HEAD)
        sub_tbl.add_column("#",        style=MC, width=4)
        sub_tbl.add_column("Имя",      style=AC, width=25)
        sub_tbl.add_column("Username", style=MC, width=18)
        sub_tbl.add_column("ID",       style=MC)
        for i, u in enumerate(result.users[:200], 1):
            name  = f"{u.first_name or ''} {u.last_name or ''}".strip()
            uname = f"@{u.username}" if u.username else ""
            sub_tbl.add_row(str(i), name, uname, str(u.id))
        console.print(sub_tbl)

    elif action == "3":
        try:
            link = await client(ExportChatInviteRequest(peer=entity))
            console.print(f"[green]Ссылка:[/] {link.link}")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    elif action == "4":
        limit = int(ask("Кол-во сообщений (0 = все)", "500") or "500")
        limit = None if limit == 0 else limit
        msgs  = []
        async for m in client.iter_messages(entity, limit=limit):
            msgs.append(f"[{m.date.strftime('%Y-%m-%d %H:%M:%S')}] {m.raw_text or ''}")
        msgs.reverse()
        fname = f"channel_{channel.name}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(msgs))
        console.print(f"[green][OK] Сохранено: {fname} ({len(msgs)} сообщений)[/]")

    elif action == "5":
        text = ask("Текст публикации")
        if text:
            msg = await client.send_message(entity, text)
            console.print(f"[green][OK] Опубликовано, ID={msg.id}[/]")

    elif action == "6":
        confirm = ask(f"УДАЛИТЬ канал [{channel.name}]? Введите YES для подтверждения", "")
        if confirm == "YES":
            try:
                await client(DeleteChannelRequest(channel=entity))
                console.print("[green][OK] Канал удалён[/]")
            except Exception as e:
                console.print(f"[red]Ошибка: {e}[/]")
        else:
            console.print("[yellow]Отменено[/]")

    pause()
