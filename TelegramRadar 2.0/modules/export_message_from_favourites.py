import os
from datetime import datetime
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

FORMATS = ["txt", "html", "pdf", "markdown"]

async def run(client):
    header("⭐  Выгрузка Сообщений из Избранного")

    limit = int(ask("Кол-во сообщений (0 = все)", "500") or "500")
    limit = None if limit == 0 else limit

    console.print(f"[{MC}]Загрузка из Избранного...[/]")
    messages = []
    async for msg in client.iter_messages("me", limit=limit):
        messages.append({
            "id":   msg.id,
            "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
            "text": msg.raw_text or "",
            "media": bool(msg.media),
        })
    messages.reverse()
    console.print(f"[{MC}]Загружено сообщений: {len(messages)}[/]\n")

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=3)
    tbl.add_column("Формат", style=AC)
    for i, f in enumerate(FORMATS, 1):
        tbl.add_row(str(i), f.upper())
    console.print(tbl)

    try:
        fmt_idx = int(ask("Формат")) - 1
        fmt = FORMATS[fmt_idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"favourites_messages_{ts}.{fmt if fmt != 'markdown' else 'md'}"

    if fmt == "txt":
        with open(fname, "w", encoding="utf-8") as f:
            for m in messages:
                media_tag = " [медиа]" if m["media"] else ""
                f.write(f"[{m['date']}]{media_tag} {m['text']}\n")

    elif fmt == "html":
        rows = "".join(
            f"<tr><td>{m['date']}</td><td>{'[MSG] ' if m['media'] else ''}</td>"
            f"<td>{m['text'].replace('<','&lt;').replace(chr(10),'<br>')}</td></tr>"
            for m in messages
        )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>Избранное</title>"
            "<style>body{font-family:sans-serif;background:#0d0d0d;color:#ddd;padding:20px}"
            "table{border-collapse:collapse;width:100%}td,th{padding:6px 10px;"
            "border:1px solid #333;vertical-align:top}th{background:#1a1a2e}</style>"
            "</head><body><h2>⭐ Избранное — сообщения</h2>"
            "<table><tr><th>Дата</th><th>Медиа</th><th>Текст</th></tr>"
            f"{rows}</table></body></html>"
        )
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)

    elif fmt == "pdf":
        try:
            from fpdf import FPDF
        except ImportError:
            os.system("pip install fpdf2 -q --break-system-packages")
            from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=9)
        pdf.cell(0, 8, "Избранное — сообщения", ln=True)
        pdf.ln(2)
        for m in messages:
            line = f"[{m['date']}] {m['text'][:150]}"
            pdf.multi_cell(0, 5, line)
            pdf.ln(1)
        pdf.output(fname)

    elif fmt == "markdown":
        with open(fname, "w", encoding="utf-8") as f:
            f.write("# ⭐ Избранное — сообщения\n\n")
            for m in messages:
                f.write(f"**{m['date']}**")
                if m["media"]:
                    f.write(" [MSG] ")
                f.write(f"\n\n{m['text']}\n\n---\n\n")

    console.print(f"[green][OK] Сохранено:[/] {fname}  ({len(messages)} записей)")
    pause()
