import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from modules._ui import MC, AC, console, header, ask, pause

load_dotenv()

MISTRAL_KEY  = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_URL  = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
MODEL        = "mistral-small-latest"

async def _ask_mistral(session: aiohttp.ClientSession, history: list[dict]) -> str:
    url     = f"{MISTRAL_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":    MODEL,
        "messages": history,
    }
    async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as r:
        if r.status != 200:
            text = await r.text()
            raise RuntimeError(f"API error {r.status}: {text}")
        data = await r.json()
        return data["choices"][0]["message"]["content"]

async def run(client):
    header("[AI]   Чат с Нейросетью  (Mistral AI)")

    if not MISTRAL_KEY:
        console.print("[red]MISTRAL_API_KEY не задан в .env[/]"); pause(); return

    history: list[dict] = [
        {"role": "system", "content": "Ты полезный ассистент. Отвечай на языке пользователя."}
    ]

    console.print(f"[{MC}]Введите 'exit' или 'quit' для выхода. Введите 'clear' для сброса истории.[/]\n")

    async with aiohttp.ClientSession() as session:
        while True:
            user_input = ask("Вы")
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break
            if user_input.lower() == "clear":
                history = history[:1]
                console.print(f"[{MC}]История очищена.[/]")
                continue

            history.append({"role": "user", "content": user_input})

            console.print(f"[{MC}]Mistral думает...[/]")
            try:
                reply = await _ask_mistral(session, history)
            except Exception as e:
                console.print(f"[red]Ошибка API: {e}[/]")
                history.pop()
                continue

            history.append({"role": "assistant", "content": reply})
            console.print(
                Panel(Markdown(reply), title=f"[{MC}]Mistral[/]", border_style=MC, box=box.ROUNDED)
            )

    pause()
