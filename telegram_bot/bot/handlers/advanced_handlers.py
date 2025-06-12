from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime, timedelta
import pytz
from ..keyboards.main_menu import (
    get_main_menu, get_trading_dashboard, get_settings_menu,
    get_risk_mode_menu, get_pair_selection_menu, get_analysis_menu
)
from ..config import Config
from ..utils.market_analysis import analyze_market, get_market_overview
from ..utils.risk_calculator import calculate_position_size, calculate_risk
from ..utils.performance_tracker import get_performance_stats
from ..utils.ai_assistant import get_ai_insights

router = Router()

@router.callback_query(F.data == "trading_dashboard")
async def show_trading_dashboard(callback: CallbackQuery):
    """Show the trading dashboard with market overview and portfolio"""
    await callback.message.edit_text(
        "📊 *Trading Dashboard*\n\n"
        "Select an option to view detailed information:",
        reply_markup=get_trading_dashboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "market_overview")
async def show_market_overview(callback: CallbackQuery):
    """Show market overview with current market conditions"""
    overview = await get_market_overview()
    await callback.message.edit_text(
        f"🌍 *Market Overview*\n\n"
        f"*Current Market Conditions:*\n"
        f"{overview['conditions']}\n\n"
        f"*Active Sessions:*\n"
        f"{overview['sessions']}\n\n"
        f"*Market Volatility:*\n"
        f"{overview['volatility']}\n\n"
        f"*Key Events:*\n"
        f"{overview['events']}",
        reply_markup=get_trading_dashboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "risk_calculator")
async def show_risk_calculator(callback: CallbackQuery):
    """Show risk calculator interface"""
    await callback.message.edit_text(
        "💰 *Risk Calculator*\n\n"
        "Please enter your account balance:",
        reply_markup=get_trading_dashboard(),
        parse_mode="Markdown"
    )

@router.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def calculate_risk_from_balance(message: Message):
    """Calculate risk based on account balance"""
    try:
        balance = float(message.text)
        risk_amount = calculate_risk(balance)
        position_size = calculate_position_size(balance)
        
        await message.answer(
            f"💰 *Risk Analysis*\n\n"
            f"*Account Balance:* ${balance:,.2f}\n"
            f"*Recommended Risk:* ${risk_amount:,.2f}\n"
            f"*Position Size:* ${position_size:,.2f}\n\n"
            f"*Risk Management Tips:*\n"
            f"• Never risk more than 2% per trade\n"
            f"• Use stop losses on every trade\n"
            f"• Consider market volatility",
            reply_markup=get_trading_dashboard(),
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("Please enter a valid number.")

@router.callback_query(F.data == "performance_stats")
async def show_performance_stats(callback: CallbackQuery):
    """Show trading performance statistics"""
    stats = await get_performance_stats()
    await callback.message.edit_text(
        f"📊 *Performance Statistics*\n\n"
        f"*Overall Performance:*\n"
        f"Win Rate: {stats['win_rate']}%\n"
        f"Total Trades: {stats['total_trades']}\n"
        f"Profit Factor: {stats['profit_factor']}\n\n"
        f"*Monthly Performance:*\n"
        f"Current Month: {stats['current_month']}\n"
        f"Last Month: {stats['last_month']}\n\n"
        f"*Best Performing Pairs:*\n"
        f"{stats['best_pairs']}\n\n"
        f"*Risk Metrics:*\n"
        f"Average Risk: {stats['avg_risk']}%\n"
        f"Max Drawdown: {stats['max_drawdown']}%",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "ai_assistant")
async def show_ai_assistant(callback: CallbackQuery):
    """Show AI assistant interface"""
    insights = await get_ai_insights()
    await callback.message.edit_text(
        f"🤖 *AI Trading Assistant*\n\n"
        f"*Market Insights:*\n"
        f"{insights['market_analysis']}\n\n"
        f"*Trading Opportunities:*\n"
        f"{insights['opportunities']}\n\n"
        f"*Risk Assessment:*\n"
        f"{insights['risk_assessment']}\n\n"
        f"*Recommendations:*\n"
        f"{insights['recommendations']}",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "analysis_technical")
async def show_technical_analysis(callback: CallbackQuery):
    """Show technical analysis for selected pairs"""
    analysis = await analyze_market()
    await callback.message.edit_text(
        f"📊 *Technical Analysis*\n\n"
        f"*Market Structure:*\n"
        f"{analysis['structure']}\n\n"
        f"*Key Levels:*\n"
        f"{analysis['levels']}\n\n"
        f"*Indicators:*\n"
        f"{analysis['indicators']}\n\n"
        f"*Patterns:*\n"
        f"{analysis['patterns']}",
        reply_markup=get_analysis_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    """Show settings menu"""
    await callback.message.edit_text(
        "⚙️ *Settings*\n\n"
        "Configure your trading preferences:",
        reply_markup=get_settings_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "risk_mode")
async def show_risk_mode(callback: CallbackQuery):
    """Show risk mode selection"""
    await callback.message.edit_text(
        "🎯 *Risk Mode Selection*\n\n"
        "Choose your preferred risk level:",
        reply_markup=get_risk_mode_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("risk_"))
async def set_risk_mode(callback: CallbackQuery):
    """Set risk mode based on selection"""
    risk_mode = callback.data.split("_")[1]
    risk_percentages = {
        "aggressive": 2.0,
        "balanced": 1.0,
        "conservative": 0.5
    }
    
    risk_percentage = risk_percentages.get(risk_mode, 1.0)
    await callback.message.edit_text(
        f"✅ *Risk Mode Updated*\n\n"
        f"Your risk level has been set to {risk_percentage}% per trade.\n\n"
        f"*Risk Management Guidelines:*\n"
        f"• Maximum risk per trade: {risk_percentage}%\n"
        f"• Use appropriate stop losses\n"
        f"• Monitor market conditions",
        reply_markup=get_settings_menu(),
        parse_mode="Markdown"
    ) 