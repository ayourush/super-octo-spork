import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

SUBSCRIBED_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBED_USERS.add(update.effective_chat.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Жди мемы каждые 30 минут!")

async def send_meme(context: ContextTypes.DEFAULT_TYPE):
    # Берем случайный мем. Пропускаем NSFW
    url = "https://meme-api.com/gimme" 
    try:
        response = requests.get(url).json()
        image_url = response.get('url')
        
        # Проверяем, что это картинка, а не гифка
        if image_url and (image_url.endswith('.jpg') or image_url.endswith('.png')):
            for chat_id in SUBSCRIBED_USERS:
                await context.bot.send_photo(chat_id=chat_id, photo=image_url, caption=response.get('title'))
    except Exception as e:
        print(f"Error fetching meme: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TG_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    
    job_queue = app.job_queue
    # 1800 секунд = 30 минут
    job_queue.run_repeating(send_meme, interval=1800, first=10)

    app.run_polling()
