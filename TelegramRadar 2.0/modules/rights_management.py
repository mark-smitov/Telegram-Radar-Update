from telethon.tl.functions.channels import EditAdminRequest, GetParticipantRequest
from telethon.tl.types import (
    ChatAdminRights, ChannelParticipantAdmin, ChannelParticipantCreator
)
from rich.table import Table
from rich.panel import Panel
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

DEFAULT_ADMIN = ChatAdminRights(
    change_info=False,
    post_messages=True,
    edit_messages=False,
    delete_messages=True,
    ban_users=False,
    invite_users=True,
    pin_messages=False,
    add_admins=False,
    anonymous=False,
    manage_call=False,
    other=False,
    manage_topics=False,
)

def _rights_from_input() -> ChatAdminRights:
    console.print(f"[{MC}]Настройте права (y/n):[/]")
    def q(label: str, default="n") -> bool:
        return ask(label, default).lower() == "y"
    return ChatAdminRights(
        change_info    = q("Изменять информацию"),
        post_messages  = q("Публиковать сообщения", "y"),
        edit_messages  = q("Редактировать сообщения"),
        delete_messages= q("Удалять сообщения", "y"),
        ban_users      = q("Блокировать пользователей"),
        invite_users   = q("Приглашать пользователей", "y"),
        pin_messages   = q("Закреплять сообщения"),
        add_admins     = q("Добавлять администраторов"),
        anonymous      = q("Аноним"),
        manage_call    = q("Управлять звонками"),
        other          = False,
        manage_topics  = q("Управлять темами"),
    )

async def run(client):
    header("⚙️   Управление Правами")

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

    console.print(f"""
[{MC}][1][/] Назначить администратора
[{MC}][2][/] Снять администратора
[{MC}][3][/] Просмотреть права участника
""")
    action = ask("Действие", "1")

    raw = ask("Username или ID пользователя")
    try:
        uid  = int(raw) if raw.lstrip("-").isdigit() else raw
        user = await client.get_entity(uid)
    except Exception as e:
        console.print(f"[red]Ошибка получения пользователя: {e}[/]"); pause(); return

    if action == "1":
        rights = _rights_from_input()
        rank   = ask("Звание (пусто = без звания)", "")
        try:
            await client(EditAdminRequest(group.entity, user, rights, rank=rank))
            console.print(f"[green][OK] Права обновлены для {user.id}[/]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    elif action == "2":
        empty_rights = ChatAdminRights()
        try:
            await client(EditAdminRequest(group.entity, user, empty_rights, rank=""))
            console.print(f"[green][OK] Права сняты с {user.id}[/]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    elif action == "3":
        try:
            part = await client(GetParticipantRequest(group.entity, user))
            p    = part.participant
            if isinstance(p, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                r = getattr(p, "admin_rights", None)
                if r:
                    lines = [f"  {k}: {'[OK]' if v else '[NO]'}" for k, v in r.to_dict().items() if k != "_"]
                    console.print(Panel("\n".join(lines), title="Права", border_style=MC))
                else:
                    console.print("[yellow]Права не заданы[/]")
            else:
                console.print("[yellow]Обычный участник — нет особых прав[/]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")

    pause()
