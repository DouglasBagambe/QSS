from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..config.pairs import PAIR_CATEGORIES, PAIR_DISPLAY_NAMES

def get_pair_selection_keyboard() -> InlineKeyboardMarkup:
    """Get the trading pair selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="EUR/USD", callback_data="select_pair_EURUSD"),
                InlineKeyboardButton(text="GBP/USD", callback_data="select_pair_GBPUSD")
            ],
            [
                InlineKeyboardButton(text="USD/JPY", callback_data="select_pair_USDJPY"),
                InlineKeyboardButton(text="USD/CHF", callback_data="select_pair_USDCHF")
            ],
            [
                InlineKeyboardButton(text="AUD/USD", callback_data="select_pair_AUDUSD"),
                InlineKeyboardButton(text="USD/CAD", callback_data="select_pair_USDCAD")
            ],
            [
                InlineKeyboardButton(text="GBP/JPY", callback_data="select_pair_GBPJPY"),
                InlineKeyboardButton(text="EUR/JPY", callback_data="select_pair_EURJPY")
            ],
            [
                InlineKeyboardButton(text="XAU/USD", callback_data="select_pair_XAUUSD"),
                InlineKeyboardButton(text="XAG/USD", callback_data="select_pair_XAGUSD")
            ],
            [
                InlineKeyboardButton(text="NAS100", callback_data="select_pair_NAS100"),
                InlineKeyboardButton(text="US300", callback_data="select_pair_US300")
            ],
            [
                InlineKeyboardButton(text="« Back to Main Menu", callback_data="show_main_menu")
            ]
        ]
    )
    return keyboard

def get_pair_category_keyboard() -> InlineKeyboardMarkup:
    """Get the pair category selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Major Pairs", callback_data="category_major"),
                InlineKeyboardButton(text="Cross Pairs", callback_data="category_cross")
            ],
            [
                InlineKeyboardButton(text="Commodities", callback_data="category_commodities"),
                InlineKeyboardButton(text="Indices", callback_data="category_indices")
            ],
            [
                InlineKeyboardButton(text="« Back to Main Menu", callback_data="show_main_menu")
            ]
        ]
    )
    return keyboard

def get_pairs_by_category(category: str) -> InlineKeyboardMarkup:
    """Get keyboard for pairs in a specific category"""
    pairs = PAIR_CATEGORIES.get(category, [])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=PAIR_DISPLAY_NAMES[pair],
                    callback_data=f"select_pair_{pair}"
                )
            ] for pair in pairs
        ] + [
            [
                InlineKeyboardButton(text="« Back to Categories", callback_data="show_categories")
            ]
        ]
    )
    return keyboard 