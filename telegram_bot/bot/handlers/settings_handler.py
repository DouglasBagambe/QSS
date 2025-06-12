from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.main_menu import get_settings_keyboard

router = Router()

@router.message(Command(commands=["settings"]))
async def settings_handler(message: Message):
    """Handle the /settings command"""
    settings_message = (
        "⚙️ Settings\n\n"
        "Configure your bot preferences:\n\n"
        "1. Risk Mode\n"
        "   • Conservative (1% risk)\n"
        "   • Moderate (2% risk)\n"
        "   • Aggressive (3% risk)\n\n"
        "2. Notifications\n"
        "   • Signal alerts\n"
        "   • Market updates\n"
        "   • Performance reports\n\n"
        "3. Trading Hours\n"
        "   • Session preferences\n"
        "   • Time zone settings\n\n"
        "4. Default Timeframe\n"
        "   • Chart timeframe\n"
        "   • Analysis period\n\n"
        "5. Language\n"
        "   • Interface language\n"
        "   • Market terminology\n\n"
        "Select an option to configure:"
    )
    
    await message.answer(
        settings_message,
        reply_markup=get_settings_keyboard()
    ) 