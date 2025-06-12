from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """Create the main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Trading Section
    builder.row(
        InlineKeyboardButton(text="📊 Trading Dashboard", callback_data="trading_dashboard"),
        InlineKeyboardButton(text="🎯 Active Signals", callback_data="active_signals")
    )
    
    # Analysis Section
    builder.row(
        InlineKeyboardButton(text="📈 Market Analysis", callback_data="market_analysis"),
        InlineKeyboardButton(text="🔍 Pair Scanner", callback_data="pair_scanner")
    )
    
    # Settings Section
    builder.row(
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton(text="📱 Notifications", callback_data="notifications")
    )
    
    # Advanced Features
    builder.row(
        InlineKeyboardButton(text="🤖 AI Assistant", callback_data="ai_assistant"),
        InlineKeyboardButton(text="📊 Performance Stats", callback_data="performance_stats")
    )
    
    return builder.as_markup()

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

def get_risk_mode_menu() -> InlineKeyboardMarkup:
    """Create the risk mode selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="🚀 Aggressive (2% Risk)", callback_data="risk_aggressive"))
    builder.row(InlineKeyboardButton(text="⚖️ Balanced (1% Risk)", callback_data="risk_balanced"))
    builder.row(InlineKeyboardButton(text="🛡️ Conservative (0.5% Risk)", callback_data="risk_conservative"))
    builder.row(InlineKeyboardButton(text="« Back to Settings", callback_data="settings"))
    
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