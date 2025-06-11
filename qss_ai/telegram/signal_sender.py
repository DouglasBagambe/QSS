import aiohttp
import json
from typing import Dict, Optional
from ..config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class SignalSender:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_signal(self, signal: Dict) -> bool:
        """
        Send trading signal to Telegram
        """
        try:
            message = self._format_signal_message(signal)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json={
                        'chat_id': self.chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error sending signal: {str(e)}")
            return False

    def _format_signal_message(self, signal: Dict) -> str:
        """
        Format trading signal message with detailed analysis
        """
        # Emoji mapping
        emojis = {
            'bullish': '🟢',
            'bearish': '🔴',
            'entry': '🎯',
            'stop_loss': '🛑',
            'take_profit': '💰',
            'confidence': '📊',
            'order_block': '📦',
            'fair_value_gap': '⚡',
            'liquidity_zone': '💧',
            'market_structure': '📈',
            'trend': '📈',
            'momentum': '💫',
            'volatility': '🌊',
            'volume': '📊',
            'risk': '⚠️',
            'reward': '🎁',
            'timeframe': '⏰',
            'session': '🌍'
        }

        # Format direction and setup
        direction = signal['type'].upper()
        direction_emoji = emojis['bullish'] if signal['type'] == 'bullish' else emojis['bearish']
        
        # Format price levels with pips
        entry = f"{emojis['entry']} Entry: {signal['entry']:.5f}"
        stop_loss = f"{emojis['stop_loss']} Stop Loss: {signal['stop_loss']:.5f}"
        take_profit = f"{emojis['take_profit']} Take Profit: {signal['take_profit']:.5f}"
        
        # Calculate and format risk metrics
        risk = abs(signal['entry'] - signal['stop_loss'])
        reward = abs(signal['take_profit'] - signal['entry'])
        rr_ratio = reward / risk if risk > 0 else 0
        
        # Format technical analysis
        ta_section = self._format_technical_analysis(signal.get('indicators', {}), emojis)
        
        # Format market structure
        structure_section = self._format_market_structure(signal.get('components', {}), emojis)
        
        # Format risk analysis
        risk_section = self._format_risk_analysis(signal, emojis)
        
        # Format session info
        session_info = self._format_session_info(signal.get('timeframe', ''), emojis)
        
        # Build the message
        message = f"""
<b>🚨 QSS Trading Signal 🚨</b>

<b>{direction_emoji} {direction} SETUP - {signal['symbol']} ({signal['timeframe']})</b>

<b>Price Levels:</b>
{entry}
{stop_loss}
{take_profit}

<b>Risk Analysis:</b>
{emojis['risk']} Risk: {risk:.5f} pips
{emojis['reward']} Reward: {reward:.5f} pips
📊 Risk-Reward Ratio: {rr_ratio:.2f}

<b>Technical Analysis:</b>
{ta_section}

<b>Market Structure:</b>
{structure_section}

<b>Risk Assessment:</b>
{risk_section}

<b>Trading Session:</b>
{session_info}

<b>Confidence Score: {signal['confidence']*100:.1f}%</b>

#QSS #Trading #Signal #{signal['symbol'].replace('/', '')} #{signal['timeframe']}
"""
        return message

    def _format_technical_analysis(self, indicators: Dict, emojis: Dict) -> str:
        """
        Format technical indicators analysis
        """
        if not indicators:
            return "No technical indicators available"
        
        analysis = []
        
        # RSI
        rsi = indicators.get('rsi', 0)
        rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
        analysis.append(f"📊 RSI ({rsi:.1f}): {rsi_status}")
        
        # MACD
        macd = indicators.get('macd', 0)
        macd_status = "Bullish" if macd > 0 else "Bearish"
        analysis.append(f"📈 MACD: {macd_status}")
        
        # Stochastic
        stoch_k = indicators.get('stoch_k', 0)
        stoch_d = indicators.get('stoch_d', 0)
        stoch_status = "Oversold" if stoch_k < 20 and stoch_d < 20 else "Overbought" if stoch_k > 80 and stoch_d > 80 else "Neutral"
        analysis.append(f"📊 Stochastic: {stoch_status}")
        
        # Bollinger Bands
        bb_position = indicators.get('bb_position', 0)
        bb_status = "Upper Band" if bb_position > 0.8 else "Lower Band" if bb_position < 0.2 else "Middle Band"
        analysis.append(f"📊 BB Position: {bb_status}")
        
        return '\n'.join(analysis)

    def _format_market_structure(self, components: Dict, emojis: Dict) -> str:
        """
        Format market structure analysis
        """
        if not components:
            return "No market structure components identified"
        
        structure = []
        
        # Order Block
        if ob := components.get('order_block'):
            structure.append(f"{emojis['order_block']} Order Block: {ob['strength']*100:.1f}% strength")
        
        # Fair Value Gap
        if fvg := components.get('fair_value_gap'):
            structure.append(f"{emojis['fair_value_gap']} Fair Value Gap: {fvg['size']*100:.1f}% size")
        
        # Liquidity Zone
        if liq := components.get('liquidity_zone'):
            structure.append(f"{emojis['liquidity_zone']} Liquidity Zone: {liq['strength']} candles")
        
        # Market Structure
        if ms := components.get('market_structure'):
            structure.append(f"{emojis['market_structure']} Market Structure: {ms['type'].upper()} BOS")
        
        return '\n'.join(structure)

    def _format_risk_analysis(self, signal: Dict, emojis: Dict) -> str:
        """
        Format risk analysis
        """
        risk_analysis = []
        
        # Trend Strength
        if 'trend_strength' in signal:
            risk_analysis.append(f"{emojis['trend']} Trend Strength: {signal['trend_strength']*100:.1f}%")
        
        # Momentum
        if 'momentum_strength' in signal:
            risk_analysis.append(f"{emojis['momentum']} Momentum: {signal['momentum_strength']*100:.1f}%")
        
        # Volatility
        if 'volatility' in signal:
            vol_status = "High" if signal['volatility'] > 0.7 else "Low" if signal['volatility'] < 0.3 else "Medium"
            risk_analysis.append(f"{emojis['volatility']} Volatility: {vol_status}")
        
        # Volume Profile
        if 'volume_profile' in signal:
            vp = signal['volume_profile']
            risk_analysis.append(f"{emojis['volume']} POC: {vp['poc']:.5f}")
        
        return '\n'.join(risk_analysis)

    def _format_session_info(self, timeframe: str, emojis: Dict) -> str:
        """
        Format trading session information
        """
        if not timeframe:
            return "No timeframe information available"
        
        return f"{emojis['timeframe']} Timeframe: {timeframe}\n{emojis['session']} Session: Current" 