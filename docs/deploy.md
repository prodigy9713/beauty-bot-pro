# Deploy

## Безопасный принцип

- .env создается только локально или прямо на VPS;
- .env не загружается в GitHub;
- в репозиторий попадает только .env.example без настоящих секретов;
- токен бота, пароль VPS и другие чувствительные данные не отправляются в чат, коммиты и README.

## Что должно быть в репозитории

- код проекта;
- .env.example;
- .gitignore;
- инструкция по деплою.

## Что не должно попадать в GitHub

- .env;
- реальный BOT_TOKEN;
- пароль от VPS;
- база с рабочими данными, если она используется в проде.

## Подготовка сервера

Сервер: Ubuntu 24.04

1. Подключитесь к серверу по SSH.
2. Обновите пакеты:

```bash
sudo apt update && sudo apt upgrade -y
```

3. Установите Python, venv и git:

```bash
sudo apt install -y python3 python3-venv python3-pip git
```

4. Создайте папку проекта:

```bash
sudo mkdir -p /opt/beauty_bot
sudo chown -R $USER:$USER /opt/beauty_bot
```

## Загрузка проекта

Если проект будет храниться в GitHub:

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> /opt/beauty_bot
cd /opt/beauty_bot
```

Если проект пока без GitHub, загрузите папку вручную по SFTP или через VS Code Remote SSH.

## Настройка окружения

1. Перейдите в папку проекта:

```bash
cd /opt/beauty_bot
```

2. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Установите зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Создание .env на сервере

Скопируйте шаблон:

```bash
cp .env.example .env
```

Откройте файл и впишите реальные значения только на сервере:

```bash
nano .env
```

Пример структуры:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=123456789
DATABASE_PATH=/opt/beauty_bot/beauty_bot.db
PROJECT_NAME=BeautyBot Pro
```

Важно: не вставляйте реальные секреты в README, GitHub issues, чат и скриншоты.

## Первый запуск

Запустите бота вручную и проверьте, что он стартует без ошибок:

```bash
source .venv/bin/activate
python main.py
```

Если бот запустился, остановите его сочетанием Ctrl+C и переходите к автозапуску.

## Автозапуск через systemd

Создайте сервис:

```bash
sudo nano /etc/systemd/system/beautybot.service
```

Вставьте:

```ini
[Unit]
Description=BeautyBot Pro
After=network.target

[Service]
User=root
WorkingDirectory=/opt/beauty_bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/beauty_bot/.venv/bin/python /opt/beauty_bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable beautybot
sudo systemctl start beautybot
sudo systemctl status beautybot
```

## Полезные команды

Логи сервиса:

```bash
sudo journalctl -u beautybot -f
```

Перезапуск после обновления кода:

```bash
sudo systemctl restart beautybot
```

## Проверка после деплоя

- открывается ли /start;
- открывается ли /admin;
- создаются ли слоты;
- проходит ли запись клиента;
- приходят ли уведомления админу.
