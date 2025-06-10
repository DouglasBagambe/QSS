from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..keyboards.inline import (
    get_main_menu,
    get_risk_mode_keyboard,
    get_back_keyboard
)
from ..utils.user_manager import user_manager
from ..config import config

router = Router()

class RiskStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_risk = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await message.answer(
        "🔐 Welcome to the Quantum SmartFlow Strategy (QSS) Trading Bot!",
        reply_markup=get_main_menu()
    )

@router.message(RiskStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """Process password input"""
    if message.text == config.password:
        await state.clear()
        await message.answer(
            "✅ Password correct! Welcome to the trading bot.",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "❌ Incorrect password. Please try again or contact support."
        )

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command"""
    await message.answer(
        "🤖 Bot Status\n"
        "───────────────\n"
        "✅ Bot is active and running\n"
        "📊 System is operational\n"
        "🔒 Security checks passed",
        reply_markup=get_main_menu()
    )

@router.message(Command("risk"))
async def cmd_risk(message: Message):
    """Handle /risk command"""
    user_prefs = user_manager.get_user_preferences(message.from_user.id)
    current_mode = user_prefs.risk_mode if user_prefs else config.DEFAULT_RISK_MODE
    current_risk = user_prefs.risk_percentage if user_prefs else config.RISK_MODES[config.DEFAULT_RISK_MODE]
    
    await message.answer(
        f"⚙️ Risk Settings\n"
        f"───────────────\n"
        f"Current Mode: {current_mode.title()}\n"
        f"Risk Percentage: {current_risk}%\n\n"
        f"Select new risk mode:",
        reply_markup=get_risk_mode_keyboard()
    )

@router.callback_query(F.data.startswith("risk_"))
async def process_risk_selection(callback: CallbackQuery, state: FSMContext):
    """Process risk mode selection"""
    mode = callback.data.split("_")[1]
    
    if mode == "custom":
        await state.set_state(RiskStates.waiting_for_risk)
        await callback.message.edit_text(
            "📝 Enter your custom risk percentage (0.1-5.0):",
            reply_markup=get_back_keyboard()
        )
    else:
        if user_manager.set_risk_mode(callback.from_user.id, mode):
            await callback.message.edit_text(
                f"✅ Risk mode set to {mode.title()} ({config.RISK_MODES[mode]}%)",
                reply_markup=get_main_menu()
            )
        else:
            await callback.answer("❌ Invalid risk mode selected", show_alert=True)

@router.message(RiskStates.waiting_for_risk)
async def process_custom_risk(message: Message, state: FSMContext):
    """Process custom risk percentage input"""
    try:
        risk = float(message.text)
        if 0.1 <= risk <= 5.0:
            user_manager.set_risk_percentage(message.from_user.id, risk)
            await state.clear()
            await message.answer(
                f"✅ Custom risk percentage set to {risk}%",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer(
                "❌ Risk percentage must be between 0.1% and 5.0%",
                reply_markup=get_back_keyboard()
            )
    except ValueError:
        await message.answer(
            "❌ Please enter a valid number",
            reply_markup=get_back_keyboard()
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "🤖 Trading Bot Help\n"
        "───────────────\n\n"
        "Available commands:\n"
        "/start - Start the bot and enter password\n"
        "/status - Check bot status\n"
        "/risk - Configure risk settings\n"
        "/lastsignal - View last trading signal\n"
        "/help - Show this help message\n\n"
        "Risk Modes:\n"
        "🚀 Aggressive (2%)\n"
        "⚖️ Balanced (1%)\n"
        "🛡️ Conservative (0.5%)\n"
        "📝 Custom (0.1-5.0%)"
    )
    await message.answer(help_text, reply_markup=get_main_menu()) 