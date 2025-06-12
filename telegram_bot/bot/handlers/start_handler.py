from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    """Handle the /start command"""
    welcome_message = (
        "🤖 Welcome to Quantum Smart Flow Strategy Bot!\n\n"
        "I'm your AI-powered trading assistant, designed to help you make "
        "smarter trading decisions using advanced market analysis and risk management.\n\n"
        "Here's what I can do:\n"
        "• Provide real-time market analysis\n"
        "• Calculate optimal position sizes\n"
        "• Track your trading performance\n"
        "• Offer AI-powered trading insights\n"
        "• Manage your risk settings\n\n"
        "Select an option from the menu below to get started!"
    )
    
    await message.answer(
        welcome_message,
        reply_markup=get_main_menu()
    ) 