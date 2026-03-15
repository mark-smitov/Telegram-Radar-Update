from rich.progress import (
    Progress, SpinnerColumn, TextColumn,
    BarColumn, TaskProgressColumn, TimeRemainingColumn,
)
from modules._ui import MC, console

def spinner(label: str = "Загрузка..."):
    return Progress(
        SpinnerColumn(style=MC),
        TextColumn(f"[{MC}]{label}[/]"),
        console=console,
        transient=True,
    )

def progress_bar(label: str = "Прогресс", total: int = 100):
    return Progress(
        SpinnerColumn(style=MC),
        TextColumn(f"[{MC}]{label}[/]"),
        BarColumn(bar_width=40, style=MC, complete_style="green"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    )

async def run_with_spinner(coro, label: str = "Загрузка..."):
    import asyncio
    with spinner(label) as p:
        task = p.add_task("", total=None)
        result = await coro
        p.advance(task)
    return result
