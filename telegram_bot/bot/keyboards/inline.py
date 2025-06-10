from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Status", callback_data="status"),
                InlineKeyboardButton(text="⚙️ Risk Settings", callback_data="risk")
            ],
            [
                InlineKeyboardButton(text="📬 Last Signal", callback_data="lastsignal"),
                InlineKeyboardButton(text="❓ Help", callback_data="help")
            ]
        ]
    )

def get_risk_mode_keyboard() -> InlineKeyboardMarkup:
    """Get risk mode selection keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Aggressive (2%)", callback_data="risk_aggressive"),
                InlineKeyboardButton(text="⚖️ Balanced (1%)", callback_data="risk_balanced")
            ],
            [
                InlineKeyboardButton(text="🛡️ Conservative (0.5%)", callback_data="risk_conservative"),
                InlineKeyboardButton(text="📝 Custom", callback_data="risk_custom")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")
            ]
        ]
    )

def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{action}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
            ]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get back button keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")
            ]
        ]
    ) 