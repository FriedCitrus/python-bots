import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers import router
from app.database import db

# Load environment variables from .env file
load_dotenv()


async def main():
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set!")
    
    # Initialize database
    print("Initializing database...")
    await db.init_db()
    print("Database initialized!")
    
    # Initialize bot and dispatcher
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Include router
    dp.include_router(router)
    
    # Start polling
    print("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')

