import asyncio
import json
import csv
from datetime import datetime
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("[SCRAPE] ️   Скрапинг Сообщений")

    dialogs = await client.get_dialogs()
    chats   = [d for d in dialogs if d.is_group or d.is_channel or d.is_user]

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#",    style=MC, width=4)
    tbl.add_column("Название", style=AC)
    tbl.add_column("Тип",      style=MC)
    for i, d in enumerate(chats[:80], 1):
        kind = "Канал" if d.is_channel else "Группа" if d.is_group else "ЛС"
        tbl.add_row(str(i), d.name or "N/A", kind)
    console.print(tbl)

    try:
        idx  = int(ask("Выберите источник")) - 1
        chat = chats[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    limit   = int(ask("Кол-во сообщений (0 = все)", "1000") or "1000")
    limit   = None if limit == 0 else limit
    keyword = ask("Фильтр по ключевому слову (пусто = все)", "")
    fmt     = ask("Формат сохранения [txt/csv/json]", "json").lower()

    messages = []
    with Progress(
        SpinnerColumn(style=MC),
        TextColumn(f"[{MC}]Скрапинг...[/]"),
        BarColumn(bar_width=30, style=MC),
        console=console
    ) as prog:
        task = prog.add_task("", total=limit or 99999)
        async for msg in client.iter_messages(chat.entity, limit=limit):
            text = msg.raw_text or ""
            if keyword and keyword.lower() not in text.lower():
                continue
            messages.append({
                "id":        msg.id,
                "date":      msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                "sender_id": msg.sender_id,
                "text":      text,
                "media":     bool(msg.media),
                "views":     getattr(msg, "views", None),
                "forwards":  getattr(msg, "forwards", None),
            })
            prog.advance(task)

    messages.reverse()
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"scrape_{chat.name}_{ts}.{fmt}"

    if fmt == "json":
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    elif fmt == "csv":
        with open(fname, "w", newline="", encoding="utf-8") as f:
            if messages:
                w = csv.DictWriter(f, fieldnames=messages[0].keys())
                w.writeheader(); w.writerows(messages)
    else:
        with open(fname, "w", encoding="utf-8") as f:
            for m in messages:
                f.write(f"[{m['date']}] {m['sender_id']}: {m['text']}\n")

    console.print(f"\n[green][OK] Собрано {len(messages)} сообщений → {fname}[/]")
    pause()
