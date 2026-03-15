import asyncio
from telethon.tl.types import InputMediaUploadedDocument
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("[SEND]   Отправить Сообщение")

    dialogs = await client.get_dialogs()

    console.print(f"[{MC}]Тип получателя:[/]")
    console.print(f"[{MC}][1][/] Выбрать из списка")
    console.print(f"[{MC}][2][/] Ввести username / ID вручную\n")
    mode = ask("Режим", "1")

    if mode == "1":
        tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
        tbl.add_column("#",       style=MC, width=4)
        tbl.add_column("Название", style=AC)
        tbl.add_column("Тип",      style=MC, width=8)
        for i, d in enumerate(dialogs[:80], 1):
            kind = "Канал" if d.is_channel else "Группа" if d.is_group else "ЛС"
            tbl.add_row(str(i), d.name or "N/A", kind)
        console.print(tbl)
        try:
            idx  = int(ask("Выберите")) - 1
            peer = dialogs[idx].entity
        except (ValueError, IndexError):
            pause("Неверный выбор."); return
    else:
        raw  = ask("Username или ID")
        uid  = int(raw) if raw.lstrip("-").isdigit() else raw
        peer = await client.get_entity(uid)

    console.print(f"\n[{MC}][1][/] Отправить текст")
    console.print(f"[{MC}][2][/] Отправить с задержкой (расписание)")
    console.print(f"[{MC}][3][/] Отправить файл\n")
    send_mode = ask("Режим отправки", "1")

    if send_mode == "1":
        text = ask("Текст сообщения")
        if not text:
            pause("Пустое сообщение."); return
        msg = await client.send_message(peer, text)
        console.print(f"[green][OK] Отправлено, ID={msg.id}[/]")

    elif send_mode == "2":
        text  = ask("Текст сообщения")
        delay = int(ask("Задержка в секундах", "5") or "5")
        console.print(f"[{MC}]Отправка через {delay}с...[/]")
        await asyncio.sleep(delay)
        msg = await client.send_message(peer, text)
        console.print(f"[green][OK] Отправлено, ID={msg.id}[/]")

    elif send_mode == "3":
        path = ask("Путь к файлу")
        caption = ask("Подпись (необязательно)", "")
        try:
            msg = await client.send_file(peer, path, caption=caption or None)
            console.print(f"[green][OK] Файл отправлен, ID={msg.id}[/]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    pause()
