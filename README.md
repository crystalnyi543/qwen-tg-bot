# 🤖 Qwen Telegram Bot

Умный AI-ассистент в Telegram с парсингом сайтов на базе **Qwen** (Alibaba).

---

## ⚡ Быстрый старт

### 1. Клонируй репозиторий
```bash
git clone https://github.com/YOUR_USERNAME/qwen-tg-bot.git
cd qwen-tg-bot
```

### 2. Установи зависимости
```bash
pip install -r requirements.txt
```

### 3. Настрой токены
```bash
cp .env.example .env
# Открой .env и заполни токены
```

### 4. Запусти бота
```bash
python bot.py
```

---

## 🔑 Как получить токены

### Telegram Bot Token
1. Напиши [@BotFather](https://t.me/BotFather) в Telegram
2. Команда `/newbot`
3. Придумай имя и username бота
4. Скопируй токен → вставь в `.env` как `TELEGRAM_BOT_TOKEN`

### DashScope API Key (Qwen)
1. Зарегистрируйся на [dashscope.aliyuncs.com](https://dashscope.aliyuncs.com)
2. Раздел **API Keys** → создай ключ
3. Скопируй → вставь в `.env` как `DASHSCOPE_API_KEY`

> 💡 Новым пользователям DashScope даёт бесплатные токены для тестирования.

---

## 📋 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск / сброс диалога |
| `/help` | Список команд |
| `/clear` | Очистить историю чата |
| `/parse <url>` | Спарсить сайт |
| `/parse <url> <вопрос>` | Спарсить и задать вопрос |

### Примеры
```
/parse https://habr.com/ru/articles/123456/
/parse https://news.ycombinator.com О чём главные новости?
```

---

## 🌐 Как привязать GitHub

### Создать новый аккаунт GitHub
1. Зайди на [github.com/signup](https://github.com/signup)
2. Введи email, пароль, username
3. Подтверди email

### Привязать SSH-ключ
```bash
# Генерация ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Копируй публичный ключ
cat ~/.ssh/id_ed25519.pub
```
4. GitHub → **Settings → SSH and GPG keys → New SSH key**
5. Вставь ключ

### Загрузить проект на GitHub
```bash
git init
git add .
git commit -m "Initial commit: Qwen Telegram Bot"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/qwen-tg-bot.git
git push -u origin main
```

---

## 📁 Структура проекта
```
qwen-tg-bot/
├── bot.py          # Основной файл бота
├── ai_client.py    # Клиент Qwen API
├── parser.py       # Парсер сайтов
├── database.py     # SQLite история диалогов
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Деплой на сервер (опционально)

### systemd сервис
```bash
sudo nano /etc/systemd/system/qwen-bot.service
```
```ini
[Unit]
Description=Qwen Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/qwen-tg-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
EnvironmentFile=/path/to/qwen-tg-bot/.env

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable qwen-bot
sudo systemctl start qwen-bot
```
