# Telegram-бот для скачивания видео с различных сервисов
[@yandisk_bot](https://t.me/yandisk_bot)


## Функции

- **Скачивание видео из YouTube**

## Установка

Для запуска Telegram-бота вам потребуется Python 3.x и установленные зависимости. Следуйте шагам ниже:

### Клонирование репозитория:

```bash
git clone ...
cd ...
```

### Создание виртуального окружения (рекомендуется):

```bash
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
```

### Установка зависимостей:

```bash
pip install -r requirements.txt
```

### Настройка переменных окружения:

Создайте файл .env в корневой папке проекта скопировав .env.template и добавьте свой Telegram API токен:

```text
BOT_TOKEN = <Token by BotFather>
```

### Запуск бота:

```bash
python ./bot/main.py
```

### Запуск api:

```bash
python ./api/app.py
```

## Зависимости

Проект использует следующие библиотеки:

- aiogram — для взаимодействия с Telegram API
- flask — для построения api

### *Важно

Убедитесь что доступ в Youtube не ограничен в вашем регионе. В противном случае Api потребуется VPN.
