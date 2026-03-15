import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.types import User
from rich.table import Table
from rich.live import Live
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

_log: list[dict] = []
_stop = False

async def run(client):
    header("[MON]   Мониторинг Группы")

    groups = [d for d in await client.get_dialogs() if d.is_group or d.is_channel]
    if not groups:
        console.print("[red]Группы/каналы не найдены[/]")
        pause(); return

    table = Table(border_style=MC, box=box.SIMPLE_HEAD)
    table.add_column("#", style=MC, width=4)
    table.add_column("Название", style=AC)
    table.add_column("ID", style=MC)
    for i, g in enumerate(groups, 1):
        table.add_row(str(i), g.name or "N/A", str(g.id))
    console.print(table)

    try:
        idx = int(ask("Выберите группу (номер)")) - 1
        group = groups[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    global _log, _stop
    _log = []
    _stop = False

    @client.on(events.NewMessage(chats=group.entity))
    async def handler(event):
        sender = await event.get_sender()
        name = ""
        uid  = event.sender_id
        uname = ""
        if isinstance(sender, User):
            name  = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
            uname = f"@{sender.username}" if sender.username else ""
        _log.append({
            "time":  datetime.now().strftime("%H:%M:%S"),
            "name":  name or "Unknown",
            "id":    uid,
            "user":  uname,
            "text":  (event.raw_text or "")[:60],
        })

    def build_table() -> Table:
        t = Table(title=f"Мониторинг: [bold]{group.name}[/]  (q→выход)",
                  border_style=MC, box=box.SIMPLE_HEAD, expand=True)
        t.add_column("Время",    style=MC,  width=10)
        t.add_column("Имя",      style=AC,  width=20)
        t.add_column("Username", style=MC,  width=18)
        t.add_column("ID",       style=MC,  width=12)
        t.add_column("Сообщение",style=AC)
        for row in _log[-30:]:
            t.add_row(row["time"], row["name"], row["user"], str(row["id"]), row["text"])
        return t

    console.print(f"\n[{MC}]Мониторинг запущен. Нажмите Ctrl+C для остановки.[/]\n")
    try:
        with Live(build_table(), refresh_per_second=2, console=console) as live:
            while True:
                live.update(build_table())
                await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        client.remove_event_handler(handler)

    if _log and ask("Сохранить лог? (y/n)", "n").lower() == "y":
        fname = f"monitor_{group.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            for r in _log:
                f.write(f"[{r['time']}] {r['name']} ({r['user']}, {r['id']}): {r['text']}\n")
        console.print(f"[green]Сохранено: {fname}[/]")

    pause()
