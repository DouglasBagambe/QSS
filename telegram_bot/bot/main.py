import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.token import validate_token
from aiogram.client.default import DefaultBotProperties
import os

from .config import config
from .handlers import (
    register_handlers,
    register_advanced_handlers,
    register_webhook_handlers
)
from .middlewares.auth import register_middleware
from .utils.logger import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Global variables for cleanup
bot = None
dp = None

async def on_startup(bot: Bot) -> None:
    """Actions to perform on bot startup"""
    logger.info("Starting bot...")
    
    # Validate bot token
    if not validate_token(config.bot_token):
        logger.error("Invalid bot token!")
        return
    
    # Set bot commands
    await bot.set_my_commands([
        {"command": "start", "description": "Start the bot"},
        {"command": "help", "description": "Show help message"},
        {"command": "settings", "description": "Configure bot settings"},
        {"command": "dashboard", "description": "Show trading dashboard"},
        {"command": "market", "description": "Show market overview"},
        {"command": "risk", "description": "Show risk calculator"},
        {"command": "stats", "description": "Show performance stats"},
        {"command": "ai", "description": "Open AI assistant"},
        {"command": "analysis", "description": "Show technical analysis"},
        {"command": "signals", "description": "Show trading signals"}
    ])
    
    logger.info("Bot started successfully!")

async def on_shutdown(bot: Bot) -> None:
    """Actions to perform on bot shutdown"""
    logger.info("Shutting down bot...")
    await bot.session.close()

def handle_exit(signum, frame):
    """Handle exit signals"""
    logger.info("Received exit signal, shutting down...")
    if bot and dp:
        asyncio.create_task(dp.stop_polling())
        asyncio.create_task(bot.session.close())
    sys.exit(0)

async def main() -> None:
    """Main function to start the bot"""
    global bot, dp
    
    try:
        # Initialize bot and dispatcher
        bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Register handlers and middleware
        register_handlers(dp)
        register_advanced_handlers(dp)
        register_webhook_handlers(dp)
        register_middleware(dp)
        
        # Register startup and shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        if bot:
            await bot.session.close()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 