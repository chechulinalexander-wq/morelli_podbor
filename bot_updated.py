import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from door_analyzer import DoorAnalyzer
from recommendation_engine import RecommendationEngine

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

door_analyzer = DoorAnalyzer()
recommendation_engine = RecommendationEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = 'Привет! Я помощник по подбору дверных ручек Morelli. Отправьте фото двери.'
    await update.message.reply_text(msg)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text('Вы прислали не фото двери')
        return

    print(f'[BOT] Received photo from user {update.effective_user.id}')
    await update.message.reply_text('Фото принято! Анализирую дверь...')

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_path = f'/tmp/door_{update.effective_user.id}_{photo.file_id}.jpg'
        await file.download_to_drive(file_path)
        print(f'[BOT] Downloaded photo to {file_path}')

        print('[BOT] Starting door analysis...')
        door_features = door_analyzer.analyze_door(file_path)
        print('[BOT] Door analysis complete')

        await update.message.reply_text('Подбираю подходящие ручки...')

        print('[BOT] Getting recommendations...')
        recommendations = recommendation_engine.recommend_handles(door_features, top_n=5)
        print(f'[BOT] Got {len(recommendations)} recommendations')

        await send_recommendations(update, recommendations, door_features)

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        print(f'[BOT] ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f'Ошибка при анализе: {str(e)}')

async def send_recommendations(update: Update, recommendations: list, door_features: dict):
    if not recommendations:
        await update.message.reply_text('Не удалось подобрать ручки.')
        return

    # Prepare explanation message
    door_desc = door_features.get('description', 'Ваша дверь')
    door_color = door_features.get('door_color', 'неизвестный')
    door_style = door_features.get('door_style', 'unknown')
    preferred_colors = ', '.join(door_features.get('preferred_finish_colors', []))
    preferred_rose = door_features.get('preferred_rose_shape', 'любая')

    style_ru = {
        'modern_minimal': 'современный минимализм',
        'classic': 'классический',
        'contemporary': 'современный',
        'rustic': 'рустик'
    }.get(door_style, door_style)

    explanation = f"""📊 Анализ вашей двери:
{door_desc}

🎨 Характеристики:
• Цвет: {door_color}
• Стиль: {style_ru}

🔍 Логика подбора:
Я использую гибридную систему рекомендаций (AI-powered):
• 70% — совпадение по метаданным (форма розетки, цвет покрытия, стиль)
• 30% — визуальное сходство через нейросеть (эмбеддинги)

💡 Для вашей двери рекомендую:
• Форма розетки: {preferred_rose}
• Цвет покрытия: {preferred_colors}
• Принцип контраста для гармоничного сочетания

Найдено {len(recommendations)} лучших вариантов:"""

    await update.message.reply_text(explanation)
    await asyncio.sleep(1)

    for i, handle in enumerate(recommendations, 1):
        name = handle['name'][:80]
        url = handle['url']
        score = handle.get('final_score', 0)

        message = f'{i}. {name}\n📈 Совпадение: {score:.1%}\nСсылка: {url}'

        try:
            if handle.get('image_path'):
                await update.message.reply_photo(photo=handle['image_path'], caption=message)
            else:
                await update.message.reply_text(message)
        except Exception as e:
            print(f'[BOT] Error: {e}')
            await update.message.reply_text(message)

        await asyncio.sleep(0.5)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        mime_type = update.message.document.mime_type
        if mime_type and mime_type.startswith('image/'):
            await handle_photo(update, context)
        else:
            await update.message.reply_text('Вы прислали не фото двери')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отправьте фотографию двери')

def main():
    print('Starting Morelli bot...')
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print('Bot is running...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
