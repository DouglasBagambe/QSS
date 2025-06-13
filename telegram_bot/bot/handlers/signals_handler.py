from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.keyboards.main_menu import get_pair_selection_keyboard, get_timeframe_keyboard
from bot.utils.data_manager import DataManager
from bot.utils.market_analysis import analyze_market

router = Router()
data_manager = DataManager()

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

@router.callback_query(F.data.startswith("select_pair_"))
async def select_pair(callback: CallbackQuery):
    """Handle pair selection"""
    pair = callback.data.replace("select_pair_", "")
    message = f"Selected pair: {pair}\n\n"
    message += "Please select a timeframe:"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_timeframe_keyboard()
    )

@router.callback_query(F.data.startswith("select_timeframe_"))
async def select_timeframe(callback: CallbackQuery):
    """Handle timeframe selection"""
    timeframe = callback.data.replace("select_timeframe_", "")
    
    # Get market data
    market_data = data_manager.get_market_data(callback.message.text.split(": ")[1])
    if not market_data:
        await callback.message.edit_text(
            "❌ No data available for this pair. Please try another pair.",
            reply_markup=get_pair_selection_keyboard()
        )
        return
    
    # Format message with real data
    message = f"📊 Market Analysis for {market_data.pair} ({timeframe})\n\n"
    
    # Market Structure
    message += "🎯 Market Structure:\n"
    message += f"• Trend: {market_data.structure.trend}\n"
    message += f"• Strength: {market_data.structure.strength:.2f}\n"
    message += "• Support Levels: " + ", ".join(f"{level:.5f}" for level in market_data.structure.support_levels) + "\n"
    message += "• Resistance Levels: " + ", ".join(f"{level:.5f}" for level in market_data.structure.resistance_levels) + "\n\n"
    
    # Technical Indicators
    message += "📈 Technical Indicators:\n"
    message += f"• RSI: {market_data.indicators.rsi:.2f}\n"
    message += f"• MACD: {market_data.indicators.macd['histogram']:.5f}\n"
    message += f"• BB Upper: {market_data.indicators.bollinger_bands['upper'][-1]:.5f}\n"
    message += f"• BB Lower: {market_data.indicators.bollinger_bands['lower'][-1]:.5f}\n\n"
    
    # Active Signals
    active_signals = [s for s in market_data.active_signals if s.status == "ACTIVE"]
    if active_signals:
        message += "🚨 Active Signals:\n"
        for signal in active_signals:
            message += f"• {signal.direction} at {signal.entry_price:.5f}\n"
            message += f"  SL: {signal.stop_loss:.5f} | TP: {signal.take_profit:.5f}\n"
            message += f"  R:R = {signal.risk_reward:.2f} | Confidence: {signal.confidence:.2f}\n"
            if signal.pips_moved:
                message += f"  Pips Moved: {signal.pips_moved:.1f}\n"
            message += "\n"
    else:
        message += "ℹ️ No active signals at the moment\n\n"
    
    # Recent News
    if market_data.recent_news:
        message += "📰 Recent News:\n"
        for news in market_data.recent_news[:3]:  # Show last 3 news items
            message += f"• {news.title} ({news.impact})\n"
        message += "\n"
    
    # Predictions
    if market_data.predictions:
        message += "🔮 AI Predictions:\n"
        for pred in market_data.predictions[:2]:  # Show last 2 predictions
            message += f"• {pred.prediction} (Confidence: {pred.confidence:.2f})\n"
            message += f"  Target: {pred.target_price:.5f} | SL: {pred.stop_loss:.5f}\n"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_pair_selection_keyboard()
    ) 