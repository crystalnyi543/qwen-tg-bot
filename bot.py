import os
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from ai_client import QwenClient
from parser import WebParser
from database import Database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Инициализация ──────────────────────────────────────────────
TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
qwen     = QwenClient()
parser   = WebParser()
db       = Database()

SYSTEM_PROMPT = """Ты умный AI-ассистент с базой знаний до 2026 года.
Ты можешь:
- Отвечать на любые вопросы
- Парсить сайты по запросу пользователя (команда /parse <url>)
- Помнить контекст разговора

Отвечай на языке пользователя. Будь полезным, точным и лаконичным.
Если парсишь сайт — кратко суммируй содержимое."""


# ── Команды ────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.clear_history(user.id)
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я умный AI-ассистент на базе **Qwen**.\n\n"
        "🧠 Знаю всё до 2026 года\n"
        "🌐 Могу парсить сайты: `/parse https://example.com`\n"
        "🗑 Сброс памяти: `/clear`\n"
        "ℹ️ Помощь: `/help`\n\n"
        "Просто напиши мне что-нибудь!",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Команды бота:*\n\n"
        "`/start` — Начать / сбросить диалог\n"
        "`/clear` — Очистить историю чата\n"
        "`/parse <url>` — Спарсить сайт и задать вопрос\n"
        "`/help` — Это сообщение\n\n"
        "💬 Или просто пиши — бот помнит контекст разговора!",
        parse_mode="Markdown"
    )


async def clear_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db.clear_history(update.effective_user.id)
    await update.message.reply_text("🗑 История очищена. Начнём заново!")


async def parse_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "⚠️ Укажи URL: `/parse https://example.com`",
            parse_mode="Markdown"
        )
        return

    url = args[0]
    question = " ".join(args[1:]) if len(args) > 1 else "Кратко опиши содержимое этого сайта"

    msg = await update.message.reply_text(f"🌐 Парсю `{url}`...", parse_mode="Markdown")

    content = await parser.fetch(url)
    if content.startswith("❌"):
        await msg.edit_text(content)
        return

    await msg.edit_text("🤔 Анализирую содержимое...")

    user_id = update.effective_user.id
    history = db.get_history(user_id)

    prompt = f"Содержимое сайта {url}:\n\n{content[:3000]}\n\n---\nВопрос: {question}"
    reply = await qwen.chat(prompt, history, SYSTEM_PROMPT)

    db.add_message(user_id, "user", f"[Парсинг {url}] {question}")
    db.add_message(user_id, "assistant", reply)

    await msg.edit_text(f"🌐 *{url}*\n\n{reply}", parse_mode="Markdown")


async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    typing = asyncio.create_task(
        ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    )

    history = db.get_history(user_id)
    reply = await qwen.chat(text, history, SYSTEM_PROMPT)

    db.add_message(user_id, "user", text)
    db.add_message(user_id, "assistant", reply)

    typing.cancel()
    await update.message.reply_text(reply)


# ── Запуск ─────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("parse", parse_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("🤖 Бот запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
