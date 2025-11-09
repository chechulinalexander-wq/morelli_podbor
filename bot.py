import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start command is issued"""
    welcome_message = (
        "👋 Привет!\n"
        "Я — твой виртуальный помощник по подбору дверных ручек Morelli.\n\n"
        "Отправь мне фотографию двери, и я подберу модели ручек, которые идеально подойдут по стилю, форме и цвету.\n\n"
        "💡 Что я умею:\n"
        "• анализировать цвет и дизайн двери\n"
        "• предлагать подходящие варианты ручек\n"
        "• показывать фото и ссылки на товары с сайта\n\n"
        "Просто отправь фото двери — и через пару секунд получишь рекомендации!\n\n"
        "🖼️ <i>Совет:</i> фотографируй дверь при хорошем освещении, чтобы я точнее определил оттенок и стиль."
    )

    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    # Проверяем, что это действительно фото
    if update.message.photo:
        await update.message.reply_text("✅ Файл принят")
        # TODO: Add image processing logic here
    else:
        await update.message.reply_text("❌ Вы прислали не фото двери")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages (files sent as documents)"""
    # Проверяем MIME-type документа
    if update.message.document:
        mime_type = update.message.document.mime_type
        # Проверяем, является ли документ изображением
        if mime_type and mime_type.startswith('image/'):
            await update.message.reply_text("✅ Файл принят")
            # TODO: Add image processing logic here
        else:
            await update.message.reply_text("❌ Вы прислали не фото двери")
    else:
        await update.message.reply_text("❌ Вы прислали не фото двери")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(
        "Пожалуйста, отправьте фотографию двери, чтобы я мог подобрать подходящие ручки."
    )

def main():
    """Start the bot"""
    print("Starting Morelli bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
