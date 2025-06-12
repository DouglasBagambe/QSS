from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """Get the main menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Trading Dashboard", callback_data="show_trading_dashboard"),
                InlineKeyboardButton(text="📈 Market Overview", callback_data="show_market_overview")
            ],
            [
                InlineKeyboardButton(text="💰 Risk Calculator", callback_data="show_risk_calculator"),
                InlineKeyboardButton(text="📊 Performance Stats", callback_data="show_performance_stats")
            ],
            [
                InlineKeyboardButton(text="🤖 AI Assistant", callback_data="show_ai_assistant"),
                InlineKeyboardButton(text="📊 Technical Analysis", callback_data="show_technical_analysis")
            ],
            [
                InlineKeyboardButton(text="⚙️ Settings", callback_data="show_settings"),
                InlineKeyboardButton(text="🎯 Risk Mode", callback_data="show_risk_mode")
            ]
        ]
    )
    return keyboard

def get_risk_mode_keyboard() -> InlineKeyboardMarkup:
    """Get the risk mode selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Conservative", callback_data="set_risk_mode_conservative"),
                InlineKeyboardButton(text="Moderate", callback_data="set_risk_mode_moderate")
            ],
            [
                InlineKeyboardButton(text="Aggressive", callback_data="set_risk_mode_aggressive")
            ],
            [
                InlineKeyboardButton(text="« Back to Main Menu", callback_data="show_main_menu")
            ]
        ]
    )
    return keyboard

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get the settings menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Risk Mode", callback_data="show_risk_mode"),
                InlineKeyboardButton(text="Notifications", callback_data="show_notifications")
            ],
            [
                InlineKeyboardButton(text="Trading Hours", callback_data="show_trading_hours"),
                InlineKeyboardButton(text="Timeframe", callback_data="show_timeframe")
            ],
            [
                InlineKeyboardButton(text="Language", callback_data="show_language"),
                InlineKeyboardButton(text="Backup", callback_data="show_backup")
            ],
            [
                InlineKeyboardButton(text="« Back to Main Menu", callback_data="show_main_menu")
            ]
        ]
    )
    return keyboard

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
                InlineKeyboardButton(text="« Back to Main Menu", callback_data="show_main_menu")
            ]
        ]
    )
    return keyboard

def get_timeframe_keyboard() -> InlineKeyboardMarkup:
    """Get the timeframe selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="M1", callback_data="select_timeframe_M1"),
                InlineKeyboardButton(text="M5", callback_data="select_timeframe_M5"),
                InlineKeyboardButton(text="M15", callback_data="select_timeframe_M15")
            ],
            [
                InlineKeyboardButton(text="M30", callback_data="select_timeframe_M30"),
                InlineKeyboardButton(text="H1", callback_data="select_timeframe_H1"),
                InlineKeyboardButton(text="H4", callback_data="select_timeframe_H4")
            ],
            [
                InlineKeyboardButton(text="D1", callback_data="select_timeframe_D1"),
                InlineKeyboardButton(text="W1", callback_data="select_timeframe_W1"),
                InlineKeyboardButton(text="MN", callback_data="select_timeframe_MN")
            ],
            [
                InlineKeyboardButton(text="« Back to Settings", callback_data="show_settings")
            ]
        ]
    )
    return keyboard

def get_trading_dashboard() -> InlineKeyboardMarkup:
    """Create the trading dashboard keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Market Overview
    builder.row(
        InlineKeyboardButton(text="🌍 Market Overview", callback_data="market_overview"),
        InlineKeyboardButton(text="📊 Portfolio", callback_data="portfolio")
    )
    
    # Trading Tools
    builder.row(
        InlineKeyboardButton(text="🎯 Signal Generator", callback_data="signal_generator"),
        InlineKeyboardButton(text="📈 Technical Analysis", callback_data="technical_analysis")
    )
    
    # Risk Management
    builder.row(
        InlineKeyboardButton(text="💰 Risk Calculator", callback_data="risk_calculator"),
        InlineKeyboardButton(text="🛡️ Position Sizer", callback_data="position_sizer")
    )
    
    # Back Button
    builder.row(InlineKeyboardButton(text="« Back to Main Menu", callback_data="main_menu"))
    
    return builder.as_markup()

def get_settings_menu() -> InlineKeyboardMarkup:
    """Create the settings menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Trading Settings
    builder.row(
        InlineKeyboardButton(text="🎯 Risk Mode", callback_data="risk_mode"),
        InlineKeyboardButton(text="📊 Trading Pairs", callback_data="trading_pairs")
    )
    
    # Notification Settings
    builder.row(
        InlineKeyboardButton(text="🔔 Signal Alerts", callback_data="signal_alerts"),
        InlineKeyboardButton(text="📱 Alert Methods", callback_data="alert_methods")
    )
    
    # AI Settings
    builder.row(
        InlineKeyboardButton(text="🤖 AI Preferences", callback_data="ai_preferences"),
        InlineKeyboardButton(text="📈 Analysis Settings", callback_data="analysis_settings")
    )
    
    # Back Button
    builder.row(InlineKeyboardButton(text="« Back to Main Menu", callback_data="main_menu"))
    
    return builder.as_markup()

def get_pair_selection_menu() -> InlineKeyboardMarkup:
    """Create the trading pair selection menu"""
    builder = InlineKeyboardBuilder()
    
    # Major Pairs
    builder.row(
        InlineKeyboardButton(text="EUR/USD", callback_data="pair_EURUSD"),
        InlineKeyboardButton(text="GBP/USD", callback_data="pair_GBPUSD")
    )
    builder.row(
        InlineKeyboardButton(text="USD/JPY", callback_data="pair_USDJPY"),
        InlineKeyboardButton(text="AUD/USD", callback_data="pair_AUDUSD")
    )
    
    # Additional Pairs
    builder.row(
        InlineKeyboardButton(text="USD/CAD", callback_data="pair_USDCAD"),
        InlineKeyboardButton(text="NZD/USD", callback_data="pair_NZDUSD")
    )
    builder.row(
        InlineKeyboardButton(text="USD/CHF", callback_data="pair_USDCHF"),
        InlineKeyboardButton(text="EUR/GBP", callback_data="pair_EURGBP")
    )
    
    # Back Button
    builder.row(InlineKeyboardButton(text="« Back to Settings", callback_data="settings"))
    
    return builder.as_markup()

def get_analysis_menu() -> InlineKeyboardMarkup:
    """Create the market analysis menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Analysis Types
    builder.row(
        InlineKeyboardButton(text="📊 Technical Analysis", callback_data="analysis_technical"),
        InlineKeyboardButton(text="📈 Price Action", callback_data="analysis_price_action")
    )
    
    # AI Analysis
    builder.row(
        InlineKeyboardButton(text="🤖 AI Predictions", callback_data="analysis_ai"),
        InlineKeyboardButton(text="🎯 Signal Quality", callback_data="analysis_quality")
    )
    
    # Timeframes
    builder.row(
        InlineKeyboardButton(text="⏱️ Timeframe Analysis", callback_data="analysis_timeframes"),
        InlineKeyboardButton(text="📅 Market Schedule", callback_data="analysis_schedule")
    )
    
    # Back Button
    builder.row(InlineKeyboardButton(text="« Back to Main Menu", callback_data="main_menu"))
    
    return builder.as_markup() 