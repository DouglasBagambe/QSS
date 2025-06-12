from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.main_menu import get_pair_selection_keyboard
from bot.utils.market_analysis import analyze_market

router = Router()

@router.message(Command(commands=["signals"]))
async def signals_handler(message: Message):
    """Handle the /signals command"""
    signals_message = (
        "🎯 Trading Signals\n\n"
        "Select a currency pair to view signals:\n\n"
        "Available Pairs:\n"
        "• EUR/USD - Euro/US Dollar\n"
        "• GBP/USD - British Pound/US Dollar\n"
        "• USD/JPY - US Dollar/Japanese Yen\n"
        "• USD/CHF - US Dollar/Swiss Franc\n"
        "• AUD/USD - Australian Dollar/US Dollar\n"
        "• USD/CAD - US Dollar/Canadian Dollar\n\n"
        "Choose a pair to analyze:"
    )
    
    await message.answer(
        signals_message,
        reply_markup=get_pair_selection_keyboard()
    ) 