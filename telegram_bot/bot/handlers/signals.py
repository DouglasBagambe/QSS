from aiogram import Router, Bot
from aiogram.types import Message
from ..utils.user_manager import user_manager
from ..config import config
from datetime import datetime
import pytz

router = Router()

async def format_signal_message(signal_data: dict) -> str:
    """Format signal message with rich formatting"""
    direction_emoji = "🚀" if signal_data["direction"].lower() == "buy" else "📉"
    
    return (
        f"📈 New Trade Signal 📈\n"
        f"───────────────\n"
        f"Pair: {signal_data['pair']}\n"
        f"Direction: {signal_data['direction'].upper()} {direction_emoji}\n"
        f"Entry: {signal_data['entry']}\n"
        f"SL: {signal_data['sl']} ❌\n"
        f"TP: {signal_data['tp']} ✅\n"
        f"───────────────\n"
        f"Time: {datetime.now(pytz.UTC).strftime('%H:%M UTC')}"
    )

async def broadcast_signal(bot: Bot, signal_data: dict):
    """Broadcast signal to all authorized users"""
    message = await format_signal_message(signal_data)
    
    for user_id in user_manager.users:
        if user_manager.is_authorized(user_id):
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Error sending signal to user {user_id}: {e}")

@router.message(Command("lastsignal"))
async def cmd_last_signal(message: Message):
    """Handle /lastsignal command"""
    # TODO: Implement last signal storage and retrieval
    await message.answer(
        "📊 Last Signal\n"
        "───────────────\n"
        "No recent signals available",
        reply_markup=get_main_menu()
    ) 