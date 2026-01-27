import os
import logging
import asyncio
import asyncpg
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TG_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_VERSION = "1.1.1"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_db():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST)
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS memer_users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                joined_at TIMESTAMP DEFAULT NOW()
            );
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS memer_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        logger.info("Database tables checked/created.")
    finally:
        await conn.close()

async def get_db_pool():
    return await asyncpg.create_pool(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST)

async def fetch_meme():
    subreddits = ["ProgrammerHumor", "wholesomememes", "ITHumor"]
    
    async with aiohttp.ClientSession() as session:
        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/top.json?limit=25&t=day"
            try:
                async with session.get(url, headers={'User-agent': 'memer_bot 1.0'}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        posts = data['data']['children']
                        
                        for post in posts:
                            p = post['data']
                            if (p['ups'] > 500 and 
                                p['url'].endswith(('.jpg', '.png', '.gif')) and 
                                not p['over_18']):
                                
                                logger.info(f"Found meme in r/{sub}: {p['title']}")
                                return p['url'], p['title']
            except Exception as e:
                logger.error(f"Error fetching from r/{sub}: {e}")
                
    logger.warning("No memes found in any subreddit today.")
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pool = context.bot_data['db_pool']
    
    await pool.execute('''
        INSERT INTO memer_users (user_id, username, first_name, is_active)
        VALUES ($1, $2, $3, TRUE)
        ON CONFLICT (user_id) DO UPDATE 
        SET is_active = TRUE, username = $2, first_name = $3
    ''', user.id, user.username, user.first_name)
    
    logger.info(f"User {user.id} ({user.username}) started the bot.")
    await update.message.reply_text(f"Привет, {user.first_name}! Я буду присылать отборные мемы каждые 30 минут!")
    
    if ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 Новый подписчик у Мемера: {user.first_name} (@{user.username})")
        except Exception as e:
            logger.error(f"Could not send admin notification: {e}")

async def send_meme_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting scheduled meme job...")
    meme_url, meme_title = await fetch_meme()
    
    if not meme_url:
        return

    pool = context.bot_data['db_pool']
    users = await pool.fetch("SELECT user_id FROM memer_users WHERE is_active = TRUE")
    
    for record in users:
        user_id = record['user_id']
        try:
            await context.bot.send_photo(chat_id=user_id, photo=meme_url, caption=meme_title)
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            if "Forbidden" in str(e):
                await pool.execute("UPDATE memer_users SET is_active = FALSE WHERE user_id = $1", user_id)

async def check_version_update(context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    row = await pool.fetchrow("SELECT value FROM memer_state WHERE key = 'version'")
    db_version = row['value'] if row else "0.0.0"

    if db_version != BOT_VERSION:
        logger.info(f"New version detected: {BOT_VERSION} (was {db_version})")
        users = await pool.fetch("SELECT user_id FROM memer_users WHERE is_active = TRUE")
        
        msg = f"♻️ **Бот обновлен до v{BOT_VERSION}!**\nТеперь я умею фильтровать мемы еще лучше."
        for u in users:
            try:
                await context.bot.send_message(u['user_id'], msg, parse_mode="Markdown")
            except:
                pass
        
        await pool.execute('''
            INSERT INTO memer_state (key, value) VALUES ('version', $1) 
            ON CONFLICT (key) DO UPDATE SET value = $1
        ''', BOT_VERSION)

async def post_init(application: Application):
    await init_db()
    application.bot_data['db_pool'] = await get_db_pool()
    application.job_queue.run_once(check_version_update, 10) 
    application.job_queue.run_repeating(send_meme_job, interval=3600, first=60)

def main():
    if not TOKEN:
        logger.fatal("No TG_TOKEN provided!")
        return
        
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("Memer Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()