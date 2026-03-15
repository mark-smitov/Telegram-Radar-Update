from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import UserPrivacyRestrictedError, UserAlreadyParticipantError
from rich.table import Table
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

async def run(client):
    header("➕  Добавить Участника / Бота")

    groups = [d for d in await client.get_dialogs() if d.is_group or d.is_channel]
    if not groups:
        console.print("[red]Группы не найдены[/]"); pause(); return

    tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    tbl.add_column("#", style=MC, width=4)
    tbl.add_column("Название", style=AC)
    for i, g in enumerate(groups, 1):
        tbl.add_row(str(i), g.name or "N/A")
    console.print(tbl)

    try:
        idx   = int(ask("Выберите группу")) - 1
        group = groups[idx]
    except (ValueError, IndexError):
        pause("Неверный выбор."); return

    raw = ask("Введите username или ID (через запятую для нескольких)")
    targets = [t.strip() for t in raw.split(",") if t.strip()]

    results: list[tuple[str, str]] = []
    for t in targets:
        try:
            uid = int(t) if t.lstrip("-").isdigit() else t
            user = await client.get_entity(uid)
            await client(InviteToChannelRequest(group.entity, [user]))
            results.append((str(t), "[green][OK] Добавлен[/]"))
        except UserAlreadyParticipantError:
            results.append((str(t), "[yellow]Уже участник[/]"))
        except UserPrivacyRestrictedError:
            results.append((str(t), "[red]Приватность запрещает[/]"))
        except Exception as e:
            results.append((str(t), f"[red]Ошибка: {e}[/]"))

    res_tbl = Table(border_style=MC, box=box.SIMPLE_HEAD)
    res_tbl.add_column("Цель",      style=AC)
    res_tbl.add_column("Результат", style=AC)
    for target, status in results:
        res_tbl.add_row(target, status)
    console.print(res_tbl)
    pause()
