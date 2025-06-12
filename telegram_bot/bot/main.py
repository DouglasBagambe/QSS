import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Config
from bot.handlers import (
    start_handler,
    help_handler,
    settings_handler,
    signals_handler,
    advanced_handlers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    try:
        # Initialize bot and dispatcher
        config = Config()
        bot = Bot(token=config.bot_token)
        dp = Dispatcher()
        
        # Register handlers
        dp.message.register(start_handler, Command(commands=["start"]))
        dp.message.register(help_handler, Command(commands=["help"]))
        dp.message.register(settings_handler, Command(commands=["settings"]))
        dp.message.register(signals_handler, Command(commands=["signals"]))
        
        # Register advanced handlers
        dp.include_router(advanced_handlers.router)
        
        # Start polling
        logger.info("Starting bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 