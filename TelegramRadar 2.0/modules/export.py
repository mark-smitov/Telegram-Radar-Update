import json
import csv
import os
from datetime import datetime
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

FORMATS = ["txt", "csv", "json", "html", "pdf"]

async def run(client):
    header("[EXP]   Экспорт Данных")

    dialogs = await client.get_dialogs()
    groups  = [d for d in dialogs if d.is_group or d.is_channel]

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=4)
    tbl.add_column("Название", style=AC)
    for i, g in enumerate(groups, 1):
        tbl.add_row(str(i), g.name or "N/A")
    console.print(tbl)

    try:
        idx  = int(ask("Выберите чат/группу")) - 1
        chat = groups[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    limit = int(ask("Количество сообщений (0 = все)", "200") or "200")
    limit = None if limit == 0 else limit

    console.print(f"\n[{MC}]Форматы: {', '.join(f'[{i+1}] {f}' for i, f in enumerate(FORMATS))}[/]")
    try:
        fmt_idx = int(ask("Формат")) - 1
        fmt = FORMATS[fmt_idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    console.print(f"[{MC}]Загрузка сообщений...[/]")
    messages = []
    async for msg in client.iter_messages(chat.entity, limit=limit):
        messages.append({
            "id":      msg.id,
            "date":    msg.date.strftime("%Y-%m-%d %H:%M:%S"),
            "from_id": msg.sender_id,
            "text":    msg.raw_text or "",
        })
    messages.reverse()

    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"export_{chat.name}_{ts}.{fmt}"

    if fmt == "txt":
        with open(fname, "w", encoding="utf-8") as f:
            for m in messages:
                f.write(f"[{m['date']}] (id={m['from_id']}): {m['text']}\n")

    elif fmt == "csv":
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["id", "date", "from_id", "text"])
            w.writeheader(); w.writerows(messages)

    elif fmt == "json":
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    elif fmt == "html":
        rows = "".join(
            f"<tr><td>{m['date']}</td><td>{m['from_id']}</td>"
            f"<td>{m['text'].replace('<','&lt;')}</td></tr>"
            for m in messages
        )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>Export {chat.name}</title>"
            "<style>body{font-family:monospace;background:#0d0d0d;color:#ddd}"
            "table{border-collapse:collapse;width:100%}"
            "td,th{padding:4px 8px;border:1px solid #333}th{background:#1a1a2e}</style>"
            "</head><body>"
            f"<h2>Экспорт: {chat.name}</h2>"
            "<table><tr><th>Дата</th><th>От</th><th>Текст</th></tr>"
            f"{rows}</table></body></html>"
        )
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)

    elif fmt == "pdf":
        try:
            from fpdf import FPDF
        except ImportError:
            console.print("[yellow]Установка fpdf2...[/]")
            os.system("pip install fpdf2 -q --break-system-packages")
            from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=9)
        pdf.cell(0, 8, f"Export: {chat.name}", ln=True)
        pdf.ln(2)
        for m in messages:
            line = f"[{m['date']}] {m['from_id']}: {m['text'][:120]}"
            pdf.multi_cell(0, 6, line)
        pdf.output(fname)

    console.print(f"[green][OK] Сохранено:[/] {fname}  ({len(messages)} сообщений)")
    pause()
