```
 /$$$$$$$$        /$$                                                          /$$$$$$$                  /$$                  
|__  $$__/       | $$                                                         | $$__  $$                | $$                  
   | $$  /$$$$$$ | $$  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$/$$$$       | $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
   | $$ /$$__  $$| $$ /$$__  $$ /$$__  $$ /$$__  $$|____  $$| $$_  $$_  $$      | $$$$$$$/ |____  $$ /$$__  $$ |____  $$ /$$__  $$
   | $$| $$$$$$$$| $$| $$$$$$$$| $$  \ $$| $$  \__/ /$$$$$$$| $$ \ $$ \ $$      | $$__  $$  /$$$$$$$| $$  | $$  /$$$$$$$| $$  \__/
   | $$| $$_____/| $$| $$_____/| $$  | $$| $$      /$$__  $$| $$ | $$ | $$      | $$  \ $$ /$$__  $$| $$  | $$ /$$__  $$| $$      
   | $$|  $$$$$$$| $$|  $$$$$$$|  $$$$$$$| $$     |  $$$$$$$| $$ | $$ | $$      | $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$      
   |__/ \_______/|__/ \_______/ \____  $$|__/      \_______/|__/ |__/ |__/      |__/  |__/ \_______/ \_______/ \_______/|__/      
                                /$$  \ $$                                                                                         
                               |  $$$$$$/                                                                                         
                                \______/                                                                                          
```

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/telethon-1.34+-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/version-2.0.0-orange?style=flat-square)

**Инструмент для работы с Telegram через userbot**

[Установка](#установка) · [Настройка](#настройка) · [Функции](#функции) · [Контакты](#контакты)

</div>

---

## Что это

TelegramRadar — консольный userbot для мониторинга групп, управления участниками, скрапинга сообщений и автоматизации рутинных задач в Telegram. Всё через терминал, без лишних GUI и браузерных вкладок.

Написан на `telethon` + `rich`, работает на любой машине где есть Python.

---

## Функции

| # | Модуль | Описание |
|---|--------|----------|
| 01 | Мониторинг группы | Live-лог входящих сообщений с именами и ID |
| 02 | Статистика группы | Участники, активность, топ писателей |
| 03 | Экспорт данных | Выгрузка в txt / csv / pdf |
| 04 | Добавить участника/бота | Инвайт по username или ID |
| 05 | Управление правами | Выдача и снятие прав в группе |
| 06 | Блокировка участника | Бан/кик с подтверждением |
| 07 | Настройки | Конфигурация сессии и параметров |
| 08 | Личные чаты | Навигация по личке |
| 09 | Скрапинг сообщений | Сбор сообщений из чата с фильтрами |
| 10 | Чат с нейросетью | Mistral AI прямо в терминале |
| 11 | Отправить сообщение | Отправка в любой чат/канал |
| 12 | Отчёт мониторингов | Сводка по всем запускам |
| 13 | Управление каналом | Редактирование, посты, статистика |
| 14 | Выгрузка сообщений | Экспорт из Избранного |
| 15 | Выгрузка медиа | Скачивание медиа из Избранного |

---

## Установка

```bash
git clone https://github.com/mark-smitov/TelegramRadar
cd TelegramRadar
pip install -r requirements.txt
```

Python 3.10 и выше. На Windows работает, но лучше запускать через Windows Terminal.

---

## Настройка

Получить `API_ID` и `API_HASH` можно на [my.telegram.org](https://my.telegram.org) → API development tools.

Создать файл `.env` в корне проекта:

```env
API_ID=ваш_api_id
API_HASH=ваш_api_hash
SESSION_NAME=telegram_radar

# опционально — для модуля чата с ИИ
MISTRAL_API_KEY=ваш_ключ
MISTRAL_BASE_URL=https://api.mistral.ai/v1
```

Запуск:

```bash
python main.py
```

При первом запуске спросит номер телефона и код из Telegram. После этого сессия сохраняется в файл `telegram_radar.session` рядом со скриптом — повторная авторизация не нужна.

---

## Структура

```
TelegramRadar/
├── main.py                 — точка входа, меню, авторизация
├── .env                    — ключи (не коммитить)
├── requirements.txt
├── modules/
│   ├── _ui.py              — общие утилиты интерфейса
│   ├── monitoring_group.py
│   ├── static_group.py
│   ├── export.py
│   ├── add_member.py
│   ├── rights_management.py
│   ├── ban_member.py
│   ├── settings.py
│   ├── personal_chats.py
│   ├── scrapping.py
│   ├── chat_ai.py
│   ├── send.py
│   ├── reports_all.py
│   ├── management_channel.py
│   ├── export_message_from_favourites.py
│   └── export_media_from_favourites.py
└── progress_bar/
    └── spiner.py
```

---

## Важно

Инструмент использует userbot — то есть работает от имени обычного аккаунта, не бота. Telegram может заблокировать аккаунт за агрессивный скрапинг или массовые действия. Используйте на тестовом аккаунте или с умом.

`.env` и `.session` файлы содержат чувствительные данные — не загружайте их в публичные репозитории.

---

## Контакты

Канал — [t.me/adaptBlackSerch](https://t.me/adaptBlackSerch)  
Разработчик — [@vksmitov](https://t.me/vksmitov)  
GitHub — [github.com/mark-smitov](https://github.com/mark-smitov)
