from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command(commands=["help"]))
async def help_handler(message: Message):
    """Handle the /help command"""
    help_message = (
        "📚 Quantum Smart Flow Strategy Bot Help\n\n"
        "Available Commands:\n"
        "/start - Start the bot and show main menu\n"
        "/help - Show this help message\n"
        "/settings - Configure bot settings\n"
        "/signals - View active trading signals\n\n"
        "Main Features:\n"
        "1. Trading Dashboard\n"
        "   • Real-time market overview\n"
        "   • Performance statistics\n"
        "   • Active trades monitoring\n\n"
        "2. Market Analysis\n"
        "   • Technical analysis\n"
        "   • Market structure\n"
        "   • Key levels and patterns\n\n"
        "3. Risk Management\n"
        "   • Position size calculator\n"
        "   • Risk mode settings\n"
        "   • Stop loss calculator\n\n"
        "4. AI Assistant\n"
        "   • Trading insights\n"
        "   • Market predictions\n"
        "   • Risk assessment\n\n"
        "Need more help? Contact support at @support"
    )
    
    await message.answer(
        help_message,
        reply_markup=get_main_menu()
    ) 