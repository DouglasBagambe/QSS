from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime
import pytz
from bot.utils.market_analysis import get_market_overview, analyze_market
from bot.utils.risk_calculator import RiskCalculator
from bot.utils.performance_tracker import PerformanceTracker
from bot.utils.ai_assistant import get_ai_insights
from bot.keyboards.main_menu import (
    get_main_menu,
    get_risk_mode_keyboard,
    get_settings_keyboard,
    get_pair_selection_keyboard,
    get_timeframe_keyboard
)
from ..config import Config

router = Router()
risk_calculator = RiskCalculator()
performance_tracker = PerformanceTracker()

@router.callback_query(F.data == "show_trading_dashboard")
async def show_trading_dashboard(callback: CallbackQuery):
    """Show the trading dashboard"""
    market_overview = await get_market_overview()
    performance_stats = performance_tracker.get_performance_stats()
    
    message = "📊 Trading Dashboard\n\n"
    message += f"Market Conditions:\n"
    message += f"• {market_overview['conditions']}\n"
    message += f"• Active Sessions: {market_overview['sessions']}\n"
    message += f"• {market_overview['volatility']}\n\n"
    
    message += f"Performance Stats:\n"
    message += f"• Total Trades: {performance_stats['total_trades']}\n"
    message += f"• Win Rate: {performance_stats['win_rate']:.1%}\n"
    message += f"• Profit Factor: {performance_stats['profit_factor']:.2f}\n"
    message += f"• Total Profit: ${performance_stats['total_profit']:.2f}\n"
    
    await callback.message.edit_text(message)

@router.callback_query(F.data == "show_market_overview")
async def show_market_overview(callback: CallbackQuery):
    """Show current market conditions"""
    market_analysis = await analyze_market()
    
    message = "📈 Market Overview\n\n"
    message += f"Market Structure:\n"
    message += f"• {market_analysis['structure']}\n\n"
    
    message += f"Key Levels:\n"
    message += f"{market_analysis['levels']}\n\n"
    
    message += f"Technical Indicators:\n"
    message += f"{market_analysis['indicators']}\n\n"
    
    message += f"Chart Patterns:\n"
    message += f"{market_analysis['patterns']}"
    
    await callback.message.edit_text(message)

@router.callback_query(F.data == "show_risk_calculator")
async def show_risk_calculator(callback: CallbackQuery):
    """Show risk calculator prompt"""
    message = "💰 Risk Calculator\n\n"
    message += "Please enter your account balance to calculate position sizes."
    
    await callback.message.edit_text(message)

@router.message(lambda message: message.text.isdigit())
async def calculate_risk_from_balance(message: Message):
    """Calculate risk based on account balance"""
    balance = float(message.text)
    risk_calculation = risk_calculator.calculate_position_size(balance)
    
    response = "💰 Risk Calculation Results\n\n"
    response += f"Account Balance: ${balance:,.2f}\n"
    response += f"Risk Mode: {risk_calculation['risk_mode'].title()}\n\n"
    
    response += "Position Sizes:\n"
    for lot_type, size in risk_calculation['position_sizes'].items():
        response += f"• {lot_type.title()}: {size:.2f} lots\n"
    
    response += f"\nMax Open Trades: {risk_calculation['max_open_trades']}\n"
    response += f"Stop Loss: {risk_calculation['stop_loss_pips']} pips\n"
    response += f"Max Daily Risk: ${risk_calculation['max_daily_risk']:,.2f}"
    
    await message.reply(response)

@router.callback_query(F.data == "show_performance_stats")
async def show_performance_stats(callback: CallbackQuery):
    """Show performance statistics"""
    stats = performance_tracker.get_performance_stats()
    
    message = "📊 Performance Statistics\n\n"
    message += f"Trading Activity:\n"
    message += f"• Total Trades: {stats['total_trades']}\n"
    message += f"• Winning Trades: {stats['winning_trades']}\n"
    message += f"• Losing Trades: {stats['losing_trades']}\n"
    message += f"• Win Rate: {stats['win_rate']:.1%}\n\n"
    
    message += f"Profitability:\n"
    message += f"• Average Profit: ${stats['average_profit']:.2f}\n"
    message += f"• Average Loss: ${stats['average_loss']:.2f}\n"
    message += f"• Profit Factor: {stats['profit_factor']:.2f}\n"
    message += f"• Total Profit: ${stats['total_profit']:.2f}\n\n"
    
    message += f"Risk Metrics:\n"
    message += f"• Max Drawdown: ${stats['max_drawdown']:.2f}\n"
    message += f"• Sharpe Ratio: {stats['sharpe_ratio']:.2f}"
    
    await callback.message.edit_text(message)

@router.callback_query(F.data == "show_ai_assistant")
async def show_ai_assistant(callback: CallbackQuery):
    """Show AI trading assistant insights"""
    insights = await get_ai_insights()
    
    message = "🤖 AI Trading Assistant\n\n"
    message += f"Market Conditions:\n"
    message += f"• Phase: {insights['market_conditions']['market_phase']}\n"
    message += f"• Sentiment: {insights['market_conditions']['sentiment']}\n"
    message += f"• Volatility: {insights['market_conditions']['volatility']}\n\n"
    
    message += f"Trading Opportunities:\n"
    for opp in insights['trading_opportunities']:
        message += f"• {opp['pair']} {opp['direction']}\n"
        message += f"  Entry: {opp['entry']}\n"
        message += f"  SL: {opp['stop_loss']}\n"
        message += f"  TP: {opp['take_profit']}\n"
        message += f"  Confidence: {opp['confidence']}\n\n"
    
    message += f"Risk Assessment:\n"
    message += f"• Overall Risk: {insights['risk_assessment']['overall_risk']}\n"
    message += f"• Risk Factors:\n"
    for factor in insights['risk_assessment']['risk_factors']:
        message += f"  - {factor}\n"
    
    await callback.message.edit_text(message)

@router.callback_query(F.data == "show_technical_analysis")
async def show_technical_analysis(callback: CallbackQuery):
    """Show technical analysis for selected pairs"""
    market_analysis = await analyze_market()
    
    message = "📊 Technical Analysis\n\n"
    message += f"Market Structure:\n"
    message += f"{market_analysis['structure']}\n\n"
    
    message += f"Key Levels:\n"
    message += f"{market_analysis['levels']}\n\n"
    
    message += f"Technical Indicators:\n"
    message += f"{market_analysis['indicators']}\n\n"
    
    message += f"Chart Patterns:\n"
    message += f"{market_analysis['patterns']}"
    
    await callback.message.edit_text(message)

@router.callback_query(F.data == "show_risk_mode")
async def show_risk_mode(callback: CallbackQuery):
    """Show risk mode selection"""
    message = "🎯 Risk Mode Selection\n\n"
    message += "Choose your preferred risk level:\n"
    message += "• Conservative - 1% risk per trade\n"
    message += "• Moderate - 2% risk per trade\n"
    message += "• Aggressive - 3% risk per trade"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_risk_mode_keyboard()
    )

@router.callback_query(F.data == "show_settings")
async def show_settings(callback: CallbackQuery):
    """Show settings menu"""
    message = "⚙️ Settings\n\n"
    message += "Select an option to configure:\n"
    message += "• Risk Mode\n"
    message += "• Notification Preferences\n"
    message += "• Trading Hours\n"
    message += "• Default Timeframe\n"
    message += "• Language"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_settings_keyboard()
    )

@router.callback_query(F.data == "show_main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu"""
    message = "🤖 Welcome to Quantum Smart Flow Strategy Bot\n\n"
    message += "Select an option from the menu below:"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_main_menu()
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
    message = f"Selected timeframe: {timeframe}\n\n"
    message += "Analyzing market conditions..."
    
    market_analysis = await analyze_market()
    
    message += f"\n\nMarket Structure:\n"
    message += f"{market_analysis['structure']}\n\n"
    message += f"Key Levels:\n"
    message += f"{market_analysis['levels']}\n\n"
    message += f"Technical Indicators:\n"
    message += f"{market_analysis['indicators']}\n\n"
    message += f"Chart Patterns:\n"
    message += f"{market_analysis['patterns']}"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data.startswith("set_risk_mode_"))
async def set_risk_mode(callback: CallbackQuery):
    """Set risk mode"""
    risk_mode = callback.data.replace("set_risk_mode_", "")
    guidelines = risk_calculator.get_risk_guidelines(risk_mode)
    
    message = f"🎯 {risk_mode.title()} Risk Mode Selected\n\n"
    message += f"{guidelines['description']}\n\n"
    message += "Guidelines:\n"
    for guideline in guidelines['guidelines']:
        message += f"• {guideline}\n"
    
    await callback.message.edit_text(message) 