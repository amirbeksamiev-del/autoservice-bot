# 🚗 AutoService Motor Bot

Telegram-бот для записи клиентов в автосервис. Позволяет выбрать услугу, дату, время и способ оплаты, а также уведомляет администратора о новых записях.

## ✨ Возможности

- 📝 Онлайн-запись на услуги (масло, шины, диагностика и др.)
- 📅 Выбор даты и удобного времени
- 💰 Выбор способа оплаты (картой / наличными)
- 📖 История записей пользователя
- 🔔 Уведомления администратору при новой записи

## 🚀 Установка и запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/your-username/autoservice-bot.git
cd autoservice-bot
```

### 2. Создай виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Настрой переменные окружения

```bash
cp .env.example .env
```

Открой файл `.env` и заполни:

```
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_user_id
```

> Получить токен можно у [@BotFather](https://t.me/BotFather)  
> Узнать свой ID можно у [@userinfobot](https://t.me/userinfobot)

### 5. Запусти бота

```bash
python bot.py
```

## 📁 Структура проекта

```
autoservice-bot/
├── bot.py           # Основной файл бота
├── requirements.txt # Зависимости
├── .env.example     # Пример файла с переменными окружения
├── .env             # Твои секреты (НЕ коммитить!)
├── .gitignore       # Исключения для Git
└── README.md        # Документация
```

## ⚠️ Важно

Файл `.env` с реальным токеном **никогда не должен попасть на GitHub**.  
Он уже добавлен в `.gitignore` — не удаляй эту строку!

## 🛠 Стек

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21
- python-dotenv
