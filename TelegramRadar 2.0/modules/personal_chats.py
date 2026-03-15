import asyncio
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("[CHAT]   Личные Чаты")

    dialogs = [d for d in await client.get_dialogs() if d.is_user]
    if not dialogs:
        console.print("[red]Личные чаты не найдены[/]"); pause(); return

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#",    style=MC, width=4)
    tbl.add_column("Имя",  style=AC)
    tbl.add_column("Username", style=MC)
    for i, d in enumerate(dialogs[:50], 1):
        uname = f"@{d.entity.username}" if d.entity.username else ""
        tbl.add_row(str(i), d.name or "N/A", uname)
    console.print(tbl)

    try:
        idx  = int(ask("Выберите чат")) - 1
        chat = dialogs[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    console.print(f"""
[{MC}][1][/] Выгрузить сообщения (txt)
[{MC}][2][/] Отправить сообщение
[{MC}][3][/] Заблокировать пользователя
[{MC}][4][/] Разблокировать пользователя
[{MC}][5][/] Очистить историю
[{MC}][0][/] Назад
""")
    action = ask("Действие", "0")

    if action == "1":
        limit = int(ask("Кол-во сообщений (0 = все)", "200") or "200")
        limit = None if limit == 0 else limit
        console.print(f"[{MC}]Загрузка...[/]")
        lines = []
        async for msg in client.iter_messages(chat.entity, limit=limit):
            sender = "Я" if msg.out else (chat.name or str(msg.sender_id))
            lines.append(f"[{msg.date.strftime('%Y-%m-%d %H:%M:%S')}] {sender}: {msg.raw_text or ''}")
        lines.reverse()
        fname = f"chat_{chat.name}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        console.print(f"[green][OK] Сохранено: {fname}[/]")

    elif action == "2":
        text = ask("Текст сообщения")
        if text:
            await client.send_message(chat.entity, text)
            console.print(f"[green][OK] Отправлено[/]")

    elif action == "3":
        await client(BlockRequest(id=chat.entity))
        console.print(f"[green][OK] Пользователь заблокирован[/]")

    elif action == "4":
        await client(UnblockRequest(id=chat.entity))
        console.print(f"[green][OK] Пользователь разблокирован[/]")

    elif action == "5":
        confirm = ask("Удалить всю историю? (yes/no)", "no")
        if confirm.lower() == "yes":
            await client(DeleteHistoryRequest(peer=chat.entity, max_id=0, just_clear=False, revoke=False))
            console.print(f"[green][OK] История очищена[/]")

    pause()
