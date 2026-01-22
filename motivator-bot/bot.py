import os
import logging
import datetime
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# В реальном проекте список ID пользователей хранят в БД (SQLite/Postgres).
# Для лабы храним в памяти (после перезапуска бота список очистится).
SUBSCRIBED_USERS = set()

# Ссылки на GIF (замени на свои любимые)
GIFS_GOOD = ["https://media.giphy.com/media/l0HTYUmU67pLWv1a8/giphy.gif", "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzN2ZGZ0bjhjNTVwNWkycmx3OW5sbDM4cG02ZzhpYjB4a3d4dTF4NiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/NEvPzZ8bd1V4Y/giphy.gif"]
GIFS_LAZY = ["https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTR5am9saXE0cjZjeTczeGViM3g5bnVhdHQzOTZrYXV3NXVoY3dmcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l378rrt5tAawaCQ9i/giphy.gif"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    SUBSCRIBED_USERS.add(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Я буду кошмарить тебя одним очень важным вопросом!")

# Задача по расписанию
async def daily_check(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='gym_yes'), InlineKeyboardButton("Нет", callback_data='gym_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for chat_id in SUBSCRIBED_USERS:
        try:
            await context.bot.send_message(chat_id=chat_id, text="Ходил в зал вчера??", reply_markup=reply_markup)
        except Exception as e:
            print(f"Не удалось отправить юзеру {chat_id}: {e}")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'gym_yes':
        await query.edit_message_text(text="Красавчик! 🔥")
        await context.bot.send_animation(chat_id=query.message.chat_id, animation=random.choice(GIFS_GOOD))
    
    elif data == 'gym_no':
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='today_yes')],
            [InlineKeyboardButton("Нет", callback_data='today_no')],
            [InlineKeyboardButton("И не планировал", callback_data='today_lazy')]
        ]
        await query.edit_message_text(text="А СЕГОДНЯ???", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'today_yes':
        await query.edit_message_text(text="Ну ладно, живи. Молодец! 👍")
        await context.bot.send_animation(chat_id=query.message.chat_id, animation=random.choice(GIFS_GOOD))

    elif data == 'today_no':
        await query.edit_message_text(text="Слабак.")
        await context.bot.send_animation(chat_id=query.message.chat_id, animation=random.choice(GIFS_LAZY))

    elif data == 'today_lazy':
        await query.edit_message_text(text="Отмазка слабака!")
        await context.bot.send_animation(chat_id=query.message.chat_id, animation=random.choice(GIFS_LAZY))

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TG_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Настройка времени (UTC)
    job_queue = app.job_queue
    # Для теста можно поставить run_repeating(daily_check, interval=60)
    # Для прода потом поставить run_daily(daily_check, time=datetime.time(hour=15, minute=0)) 
    job_queue.run_repeating(daily_check, interval=60)

    app.run_polling()
