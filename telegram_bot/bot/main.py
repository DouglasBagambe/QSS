import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from .config import Config
from .keyboards.main_menu import get_main_menu
from .handlers import (
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
    """Main function to run the bot"""
    try:
        # Initialize bot and dispatcher
        bot = Bot(token=Config.bot_token)
        dp = Dispatcher()
        
        # Register handlers
        dp.include_router(start_handler.router)
        dp.include_router(help_handler.router)
        dp.include_router(settings_handler.router)
        dp.include_router(signals_handler.router)
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