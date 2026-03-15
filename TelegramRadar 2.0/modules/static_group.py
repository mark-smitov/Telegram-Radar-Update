import asyncio
from collections import Counter
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, User
from rich.table import Table
from rich.progress import track
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("[STAT]   Статистика Группы")

    groups = [d for d in await client.get_dialogs() if d.is_group or d.is_channel]
    if not groups:
        console.print("[red]Группы не найдены[/]"); pause(); return

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=4)
    tbl.add_column("Название", style=AC)
    tbl.add_column("ID", style=MC)
    for i, g in enumerate(groups, 1):
        tbl.add_row(str(i), g.name or "N/A", str(g.id))
    console.print(tbl)

    try:
        idx = int(ask("Выберите группу")) - 1
        group = groups[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    entity = group.entity
    console.print(f"\n[{MC}]Загрузка участников...[/]")

    members: list = []
    offset = 0
    limit  = 200
    while True:
        result = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsSearch(""),
            offset=offset, limit=limit, hash=0
        ))
        if not result.users:
            break
        members.extend(result.users)
        offset += len(result.users)
        if offset >= result.count:
            break
        await asyncio.sleep(0.3)

    mem_table = Table(
        title=f"Участники [{group.name}] — всего: {len(members)}",
        border_style=MC, box=box.SIMPLE_HEAD, expand=True
    )
    mem_table.add_column("#",        style=MC,  width=5)
    mem_table.add_column("Имя",      style=AC,  width=25)
    mem_table.add_column("Username", style=MC,  width=18)
    mem_table.add_column("ID",       style=MC,  width=12)
    mem_table.add_column("Бот",      style=AC,  width=5)
    for i, u in enumerate(members[:500], 1):
        if isinstance(u, User):
            name  = f"{u.first_name or ''} {u.last_name or ''}".strip()
            uname = f"@{u.username}" if u.username else ""
            mem_table.add_row(str(i), name, uname, str(u.id), "[OK]" if u.bot else "")
    console.print(mem_table)

    console.print(f"\n[{MC}]Загрузка сообщений (может занять время)...[/]")
    msg_counter: Counter = Counter()
    total = 0
    async for msg in client.iter_messages(entity, limit=5000):
        total += 1
        if msg.sender_id:
            msg_counter[msg.sender_id] += 1

    console.print(f"\n[{MC}]Всего сообщений проверено: {total}[/]")

    top_table = Table(
        title="Топ-20 по сообщениям",
        border_style=MC, box=box.SIMPLE_HEAD
    )
    top_table.add_column("#",        style=MC, width=4)
    top_table.add_column("ID",       style=MC, width=12)
    top_table.add_column("Сообщений",style=AC, width=12)

    user_map = {u.id: u for u in members if isinstance(u, User)}
    for rank, (uid, cnt) in enumerate(msg_counter.most_common(20), 1):
        u = user_map.get(uid)
        label = f"@{u.username}" if u and u.username else str(uid)
        top_table.add_row(str(rank), label, str(cnt))
    console.print(top_table)

    if ask("Сохранить список участников в CSV? (y/n)", "n").lower() == "y":
        import csv
        fname = f"members_{group.name}.csv"
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["#", "Имя", "Username", "ID", "Бот", "Сообщений"])
            for i, u in enumerate(members, 1):
                if isinstance(u, User):
                    name  = f"{u.first_name or ''} {u.last_name or ''}".strip()
                    uname = f"@{u.username}" if u.username else ""
                    w.writerow([i, name, uname, u.id, u.bot, msg_counter.get(u.id, 0)])
        console.print(f"[green]Сохранено: {fname}[/]")

    pause()
