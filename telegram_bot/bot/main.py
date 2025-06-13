import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.token import validate_token
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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

async def health_check(request: web.Request) -> web.Response:
    """Health check endpoint for Railway"""
    return web.Response(text="OK", status=200)

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

async def main() -> None:
    """Main function to start the bot"""
    try:
        # Initialize bot and dispatcher
        bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher()
        
        # Register handlers and middleware
        register_handlers(dp)
        register_advanced_handlers(dp)
        register_webhook_handlers(dp)
        register_middleware(dp)
        
        # Register startup and shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Create web application
        app = web.Application()
        app.router.add_get("/health", health_check)
        
        # Setup webhook handler
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_handler.register(app, path="/webhook")
        
        # Start web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8000")))
        await site.start()
        
        logger.info("Web server started!")
        
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!") 