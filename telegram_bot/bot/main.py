import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from bot.config import Config
from bot.handlers.start_handler import router as start_router
from bot.handlers.help_handler import router as help_router
from bot.handlers.settings_handler import router as settings_router
from bot.handlers.signals_handler import router as signals_router
from bot.handlers.advanced_handlers import router as advanced_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    try:
        # Initialize bot and dispatcher
        bot = Bot(token=Config.bot_token)
        dp = Dispatcher()
        
        # Register routers
        dp.include_router(start_router)
        dp.include_router(help_router)
        dp.include_router(settings_router)
        dp.include_router(signals_router)
        dp.include_router(advanced_router)
        
        # Start polling
        logger.info("Starting bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 