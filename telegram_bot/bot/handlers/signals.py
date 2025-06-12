from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from ..utils.user_manager import user_manager
from ..config import config
from datetime import datetime
import pytz
import re

router = Router()

def parse_mt5_signal(message_text: str) -> dict:
    """Parse MT5 signal message into structured data"""
    try:
        # Extract direction and pair
        direction_match = re.search(r'(📈|📉)\s+<b>(LONG|SHORT)\s+SIGNAL\s+-\s+(\w+)</b>', message_text)
        if not direction_match:
            return None
            
        direction = "BUY" if direction_match.group(1) == "📈" else "SELL"
        pair = direction_match.group(3)
        
        # Extract entry price
        entry_match = re.search(r'@\s+([\d.]+)', message_text)
        entry = entry_match.group(1) if entry_match else "N/A"
        
        # Extract R:R ratio
        rr_match = re.search(r'1:([\d.]+)\s+R:R', message_text)
        rr_ratio = float(rr_match.group(1)) if rr_match else 2.0
        
        # Calculate SL and TP based on R:R ratio
        # This is a simplified calculation - you might want to adjust based on your strategy
        entry_price = float(entry)
        if direction == "BUY":
            sl = entry_price * 0.99  # 1% below entry
            tp = entry_price + (entry_price - sl) * rr_ratio
        else:
            sl = entry_price * 1.01  # 1% above entry
            tp = entry_price - (sl - entry_price) * rr_ratio
            
        return {
            "pair": pair,
            "direction": direction,
            "entry": entry,
            "sl": f"{sl:.5f}",
            "tp": f"{tp:.5f}",
            "rr_ratio": rr_ratio,
            "source": "MT5",
            "timestamp": datetime.now(pytz.UTC)
        }
    except Exception as e:
        print(f"Error parsing MT5 signal: {e}")
        return None

async def format_signal_message(signal_data: dict) -> str:
    """Format signal message with rich formatting"""
    direction_emoji = "🚀" if signal_data["direction"].upper() == "BUY" else "📉"
    source_emoji = "🤖" if signal_data.get("source") == "MT5" else "📊"
    
    return (
        f"{source_emoji} New Trade Signal {source_emoji}\n"
        f"───────────────\n"
        f"Pair: {signal_data['pair']}\n"
        f"Direction: {signal_data['direction'].upper()} {direction_emoji}\n"
        f"Entry: {signal_data['entry']}\n"
        f"SL: {signal_data['sl']} ❌\n"
        f"TP: {signal_data['tp']} ✅\n"
        f"R:R Ratio: 1:{signal_data.get('rr_ratio', 2.0):.1f}\n"
        f"───────────────\n"
        f"Time: {signal_data['timestamp'].strftime('%H:%M UTC')}"
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

@router.message()
async def handle_mt5_signal(message: Message):
    """Handle incoming MT5 signals"""
    if message.text and (message.text.startswith("📈") or message.text.startswith("📉")):
        signal_data = parse_mt5_signal(message.text)
        if signal_data:
            await broadcast_signal(message.bot, signal_data)
            # Store the signal for /lastsignal command
            config.last_signal = signal_data

@router.message(Command("lastsignal"))
async def cmd_last_signal(message: Message):
    """Handle /lastsignal command"""
    if hasattr(config, 'last_signal') and config.last_signal:
        signal_message = await format_signal_message(config.last_signal)
        await message.answer(signal_message)
    else:
        await message.answer(
            "📊 Last Signal\n"
            "───────────────\n"
            "No recent signals available"
        ) 