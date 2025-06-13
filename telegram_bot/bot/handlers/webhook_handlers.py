from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..config import config

router = Router()

@router.message(Command("webhook"))
async def webhook_status(message: Message):
    """Handle webhook status check"""
    await message.answer(
        "🔗 Webhook Status\n"
        "───────────────\n"
        f"URL: {config.webhook_url}\n"
        "Status: Active\n"
        "Last Signal: " + (f"{config.last_signal['timestamp']}" if config.last_signal else "None")
    )

def register_webhook_handlers(dp):
    """Register webhook handlers with the dispatcher"""
    dp.include_router(router) 