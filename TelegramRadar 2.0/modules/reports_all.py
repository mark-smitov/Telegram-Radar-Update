import glob
import os
from datetime import datetime
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

REPORT_FORMATS = ["txt", "html", "pdf"]

def _collect_logs() -> list[dict]:
    records = []
    for path in sorted(glob.glob("monitor_*.txt")):
        group = path.replace("monitor_", "").rsplit("_", 2)[0]
        with open(path, encoding="utf-8") as f:
            for line in f:
                records.append({"source": group, "line": line.rstrip()})
    return records

def _save_txt(records, fname):
    with open(fname, "w", encoding="utf-8") as f:
        for r in records:
            f.write(f"[{r['source']}] {r['line']}\n")

def _save_html(records, fname):
    rows = "".join(
        f"<tr><td>{r['source']}</td><td>{r['line'].replace('<','&lt;')}</td></tr>"
        for r in records
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>Отчёт Мониторингов</title>"
        "<style>body{font-family:monospace;background:#0d0d0d;color:#ddd}"
        "table{border-collapse:collapse;width:100%}"
        "td,th{padding:4px 8px;border:1px solid #333}th{background:#1a1a2e}</style></head><body>"
        "<h2>Отчёт всех мониторингов</h2>"
        "<table><tr><th>Источник</th><th>Запись</th></tr>"
        f"{rows}</table></body></html>"
    )
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)

def _save_pdf(records, fname):
    try:
        from fpdf import FPDF
    except ImportError:
        os.system("pip install fpdf2 -q --break-system-packages")
        from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 8, "Отчёт всех мониторингов", ln=True)
    pdf.ln(2)
    for r in records:
        pdf.multi_cell(0, 5, f"[{r['source']}] {r['line'][:150]}")
    pdf.output(fname)

async def run(client):
    header("[RPT]   Отчёт Всех Мониторингов")

    logs = _collect_logs()

    if not logs:
        console.print(f"[yellow]Нет сохранённых логов мониторинга.[/]")
        console.print(f"[{MC}]Логи сохраняются автоматически при завершении мониторинга.[/]")
        pause(); return

    console.print(f"[{MC}]Найдено записей: {len(logs)}[/]\n")

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=3)
    tbl.add_column("Формат", style=AC)
    for i, f in enumerate(REPORT_FORMATS, 1):
        tbl.add_row(str(i), f.upper())
    console.print(tbl)

    try:
        fmt_idx = int(ask("Формат")) - 1
        fmt = REPORT_FORMATS[fmt_idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"report_all_{ts}.{fmt}"

    if fmt == "txt":
        _save_txt(logs, fname)
    elif fmt == "html":
        _save_html(logs, fname)
    elif fmt == "pdf":
        _save_pdf(logs, fname)

    console.print(f"[green][OK] Отчёт сохранён: {fname}[/]")
    pause()
