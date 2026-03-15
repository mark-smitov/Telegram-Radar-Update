import os
import asyncio
import base64
from datetime import datetime
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

FORMATS = ["html", "pdf"]
MEDIA_DIR = Path("favourites_media")

async def run(client):
    header("[MEDIA] ️   Выгрузка Медиа из Избранного")

    limit = int(ask("Кол-во сообщений для проверки (0 = все)", "500") or "500")
    limit = None if limit == 0 else limit

    console.print(f"[{MC}]Сканирование Избранного...[/]")
    media_msgs = []
    async for msg in client.iter_messages("me", limit=limit):
        if msg.media:
            media_msgs.append(msg)

    console.print(f"[{MC}]Найдено медиа-сообщений: {len(media_msgs)}[/]\n")

    if not media_msgs:
        console.print("[yellow]Медиа не найдено.[/]"); pause(); return

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

    MEDIA_DIR.mkdir(exist_ok=True)
    downloaded: list[dict] = []

    with Progress(
        SpinnerColumn(style=MC),
        TextColumn(f"[{MC}]Загрузка медиа...[/]"),
        BarColumn(bar_width=30, style=MC),
        console=console
    ) as prog:
        task = prog.add_task("", total=len(media_msgs))
        for msg in media_msgs:
            try:
                path = await client.download_media(msg, file=str(MEDIA_DIR))
                if path:
                    downloaded.append({
                        "path": str(path),
                        "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "caption": msg.raw_text or "",
                    })
            except Exception:
                pass
            prog.advance(task)
            await asyncio.sleep(0.05)

    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"favourites_media_{ts}.{fmt}"

    if fmt == "html":
        items_html = ""
        for item in downloaded:
            p    = Path(item["path"])
            ext  = p.suffix.lower()
            date = item["date"]
            cap  = item["caption"].replace("<", "&lt;")
            if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                try:
                    data = base64.b64encode(p.read_bytes()).decode()
                    mt   = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext[1:]}"
                    img_tag = f'<img src="data:{mt};base64,{data}" style="max-width:400px;max-height:400px;">'
                except Exception:
                    img_tag = f'<a href="{p}">{p.name}</a>'
            elif ext in (".mp4", ".mov"):
                try:
                    data = base64.b64encode(p.read_bytes()).decode()
                    img_tag = (f'<video controls style="max-width:400px">'
                               f'<source src="data:video/mp4;base64,{data}"></video>')
                except Exception:
                    img_tag = f'<a href="{p}">{p.name}</a>'
            else:
                img_tag = f'<a href="{p}">{p.name}</a>'
            items_html += (
                f'<div class="item"><div class="date">{date}</div>'
                f'{img_tag}'
                f'{"<p>" + cap + "</p>" if cap else ""}'
                f'</div>'
            )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>Медиа Избранного</title>"
            "<style>body{font-family:sans-serif;background:#0d0d0d;color:#ddd;padding:20px}"
            ".item{border:1px solid #333;border-radius:8px;padding:12px;margin:12px 0}"
            ".date{color:#00bfff;font-size:0.85em;margin-bottom:6px}"
            "img,video{border-radius:4px;display:block;margin-top:6px}</style>"
            "</head><body><h2>[MEDIA] ️ Избранное — медиа</h2>"
            f"{items_html}</body></html>"
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
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 8, "Избранное — медиа", ln=True)
        pdf.ln(2)
        for item in downloaded:
            p   = Path(item["path"])
            ext = p.suffix.lower()
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(0, 6, f"Дата: {item['date']}  Файл: {p.name}", ln=True)
            if item["caption"]:
                pdf.set_font("Helvetica", size=8)
                pdf.multi_cell(0, 5, item["caption"][:200])
            if ext in (".jpg", ".jpeg", ".png"):
                try:
                    pdf.image(str(p), w=80)
                except Exception:
                    pass
            pdf.ln(3)
        pdf.output(fname)

    console.print(f"[green][OK] Сохранено:[/] {fname}  ({len(downloaded)} файлов)")
    console.print(f"[{MC}]Медиа-файлы в папке:[/] {MEDIA_DIR}/")
    pause()
