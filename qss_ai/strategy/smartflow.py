import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from ..config.settings import (
    OB_LOOKBACK_PERIODS,
    FVG_THRESHOLD,
    LIQUIDITY_CLUSTER_SIZE
)
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice

class QuantumSmartFlowStrategy:
    def __init__(self):
        # ICT Parameters
        self.order_block_lookback = 20
        self.fvg_threshold = 0.0002
        self.liquidity_cluster_size = 3
        self.displacement_threshold = 0.001
        self.optimal_entry_retracement = (0.618, 0.786)  # Fibonacci levels
        
        # Technical Indicators
        self.ema_periods = [8, 21, 50, 200]
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.bb_period = 20
        self.bb_std = 2
        self.vwap_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.stoch_k = 14
        self.stoch_d = 3
        self.stoch_smooth = 3

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        """
        # EMAs
        for period in self.ema_periods:
            df[f'ema_{period}'] = EMAIndicator(close=df['close'], window=period).ema_indicator()
        
        # RSI
        rsi = RSIIndicator(close=df['close'], window=self.rsi_period)
        df['rsi'] = rsi.rsi()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=self.bb_period, window_dev=self.bb_std)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        
        # VWAP
        df['vwap'] = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume'],
            window=self.vwap_period
        ).volume_weighted_average_price()
        
        # MACD
        macd = MACD(
            close=df['close'],
            window_fast=self.macd_fast,
            window_slow=self.macd_slow,
            window_sign=self.macd_signal
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Stochastic
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.stoch_k,
            smooth_window=self.stoch_smooth
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal(window=self.stoch_d)
        
        return df

    def _check_trend_strength(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Check trend strength using multiple indicators
        """
        # EMA Alignment
        ema_aligned_up = all(df['ema_8'].iloc[-1] > df[f'ema_{period}'].iloc[-1] 
                           for period in [21, 50, 200])
        ema_aligned_down = all(df['ema_8'].iloc[-1] < df[f'ema_{period}'].iloc[-1] 
                             for period in [21, 50, 200])
        
        # MACD
        macd_bullish = df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]
        macd_bearish = df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]
        
        # RSI
        rsi_bullish = df['rsi'].iloc[-1] > 50
        rsi_bearish = df['rsi'].iloc[-1] < 50
        
        # Bollinger Bands
        bb_bullish = df['close'].iloc[-1] > df['bb_middle'].iloc[-1]
        bb_bearish = df['close'].iloc[-1] < df['bb_middle'].iloc[-1]
        
        # Calculate trend strength
        bullish_signals = sum([ema_aligned_up, macd_bullish, rsi_bullish, bb_bullish])
        bearish_signals = sum([ema_aligned_down, macd_bearish, rsi_bearish, bb_bearish])
        
        if bullish_signals > bearish_signals:
            return 'bullish', bullish_signals / 4
        elif bearish_signals > bullish_signals:
            return 'bearish', bearish_signals / 4
        else:
            return 'neutral', 0.5

    def _check_momentum(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Check momentum using multiple indicators
        """
        # RSI
        rsi = df['rsi'].iloc[-1]
        rsi_momentum = 0
        if rsi > self.rsi_overbought:
            rsi_momentum = -1
        elif rsi < self.rsi_oversold:
            rsi_momentum = 1
        
        # Stochastic
        stoch_k = df['stoch_k'].iloc[-1]
        stoch_d = df['stoch_d'].iloc[-1]
        stoch_momentum = 0
        if stoch_k > 80 and stoch_d > 80:
            stoch_momentum = -1
        elif stoch_k < 20 and stoch_d < 20:
            stoch_momentum = 1
        
        # MACD
        macd_momentum = 0
        if df['macd_diff'].iloc[-1] > 0 and df['macd_diff'].iloc[-2] < 0:
            macd_momentum = 1
        elif df['macd_diff'].iloc[-1] < 0 and df['macd_diff'].iloc[-2] > 0:
            macd_momentum = -1
        
        # Calculate overall momentum
        momentum_score = (rsi_momentum + stoch_momentum + macd_momentum) / 3
        
        if momentum_score > 0:
            return 'bullish', abs(momentum_score)
        elif momentum_score < 0:
            return 'bearish', abs(momentum_score)
        else:
            return 'neutral', 0

    def _check_volatility(self, df: pd.DataFrame) -> float:
        """
        Check market volatility
        """
        # Bollinger Band Width
        bb_width = (df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1]) / df['bb_middle'].iloc[-1]
        
        # ATR (Average True Range)
        tr = pd.DataFrame()
        tr['h-l'] = df['high'] - df['low']
        tr['h-pc'] = abs(df['high'] - df['close'].shift(1))
        tr['l-pc'] = abs(df['low'] - df['close'].shift(1))
        tr['tr'] = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        atr = tr['tr'].rolling(window=14).mean().iloc[-1]
        
        # Normalize volatility score
        volatility_score = (bb_width + atr/df['close'].iloc[-1]) / 2
        return min(volatility_score * 10, 1.0)  # Scale to 0-1

    def _check_volume_profile(self, df: pd.DataFrame) -> Dict:
        """
        Analyze volume profile
        """
        # Calculate POC (Point of Control)
        price_range = pd.qcut(df['close'], q=10)
        volume_profile = df.groupby(price_range)['volume'].sum()
        poc_price = volume_profile.idxmax().left
        
        # Calculate Value Area
        total_volume = volume_profile.sum()
        value_area_volume = 0
        value_area_prices = []
        
        for price, volume in volume_profile.sort_values(ascending=False).items():
            value_area_volume += volume
            value_area_prices.append(price.left)
            if value_area_volume >= 0.7 * total_volume:
                break
        
        return {
            'poc': poc_price,
            'value_area_high': max(value_area_prices),
            'value_area_low': min(value_area_prices)
        }

    def _check_optimal_entry(self, df: pd.DataFrame, setup_type: str) -> bool:
        """
        Check if current price is at optimal entry level
        """
        if setup_type == 'bullish':
            # Check if price is in discount zone (below 50% retracement)
            recent_high = df['high'].rolling(window=20).max().iloc[-1]
            recent_low = df['low'].rolling(window=20).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate retracement levels
            range_high = recent_high
            range_low = recent_low
            range_size = range_high - range_low
            
            # Check if price is in optimal entry zone (61.8% - 78.6% retracement)
            optimal_zone_low = range_high - range_size * self.optimal_entry_retracement[1]
            optimal_zone_high = range_high - range_size * self.optimal_entry_retracement[0]
            
            return optimal_zone_low <= current_price <= optimal_zone_high
            
        elif setup_type == 'bearish':
            # Check if price is in premium zone (above 50% retracement)
            recent_high = df['high'].rolling(window=20).max().iloc[-1]
            recent_low = df['low'].rolling(window=20).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate retracement levels
            range_high = recent_high
            range_low = recent_low
            range_size = range_high - range_low
            
            # Check if price is in optimal entry zone (61.8% - 78.6% retracement)
            optimal_zone_low = range_low + range_size * self.optimal_entry_retracement[0]
            optimal_zone_high = range_low + range_size * self.optimal_entry_retracement[1]
            
            return optimal_zone_low <= current_price <= optimal_zone_high
            
        return False

    def detect_order_blocks(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect bullish and bearish order blocks based on candle patterns
        """
        bullish_obs = []
        bearish_obs = []
        
        for i in range(2, len(df) - 1):
            # Bullish Order Block
            if (df['close'].iloc[i] < df['open'].iloc[i] and  # Current candle is bearish
                df['close'].iloc[i+1] > df['open'].iloc[i+1] and  # Next candle is bullish
                df['low'].iloc[i+1] > df['high'].iloc[i]):  # Next candle breaks above
                
                bullish_obs.append({
                    'start': df.index[i],
                    'end': df.index[i+1],
                    'high': df['high'].iloc[i],
                    'low': df['low'].iloc[i],
                    'strength': (df['high'].iloc[i] - df['low'].iloc[i]) / df['low'].iloc[i]
                })
            
            # Bearish Order Block
            if (df['close'].iloc[i] > df['open'].iloc[i] and  # Current candle is bullish
                df['close'].iloc[i+1] < df['open'].iloc[i+1] and  # Next candle is bearish
                df['high'].iloc[i+1] < df['low'].iloc[i]):  # Next candle breaks below
                
                bearish_obs.append({
                    'start': df.index[i],
                    'end': df.index[i+1],
                    'high': df['high'].iloc[i],
                    'low': df['low'].iloc[i],
                    'strength': (df['high'].iloc[i] - df['low'].iloc[i]) / df['low'].iloc[i]
                })
        
        return {
            'bullish': bullish_obs[-3:] if bullish_obs else [],  # Keep last 3
            'bearish': bearish_obs[-3:] if bearish_obs else []   # Keep last 3
        }

    def detect_fair_value_gaps(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect fair value gaps (FVGs) in the market
        """
        bullish_fvgs = []
        bearish_fvgs = []
        
        for i in range(1, len(df) - 1):
            # Bullish FVG
            if (df['low'].iloc[i+1] > df['high'].iloc[i-1] and
                (df['low'].iloc[i+1] - df['high'].iloc[i-1]) / df['high'].iloc[i-1] > self.fvg_threshold):
                
                bullish_fvgs.append({
                    'start': df.index[i-1],
                    'end': df.index[i+1],
                    'top': df['low'].iloc[i+1],
                    'bottom': df['high'].iloc[i-1],
                    'size': (df['low'].iloc[i+1] - df['high'].iloc[i-1]) / df['high'].iloc[i-1]
                })
            
            # Bearish FVG
            if (df['high'].iloc[i+1] < df['low'].iloc[i-1] and
                (df['low'].iloc[i-1] - df['high'].iloc[i+1]) / df['low'].iloc[i-1] > self.fvg_threshold):
                
                bearish_fvgs.append({
                    'start': df.index[i-1],
                    'end': df.index[i+1],
                    'top': df['low'].iloc[i-1],
                    'bottom': df['high'].iloc[i+1],
                    'size': (df['low'].iloc[i-1] - df['high'].iloc[i+1]) / df['low'].iloc[i-1]
                })
        
        return {
            'bullish': bullish_fvgs[-3:] if bullish_fvgs else [],  # Keep last 3
            'bearish': bearish_fvgs[-3:] if bearish_fvgs else []   # Keep last 3
        }

    def detect_liquidity_zones(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect liquidity zones based on equal highs and lows
        """
        bullish_zones = []
        bearish_zones = []
        
        for i in range(self.liquidity_cluster_size, len(df)):
            # Check for bullish liquidity (equal lows)
            if all(abs(df['low'].iloc[i-j] - df['low'].iloc[i]) < self.fvg_threshold 
                  for j in range(self.liquidity_cluster_size)):
                bullish_zones.append({
                    'start': df.index[i-self.liquidity_cluster_size],
                    'end': df.index[i],
                    'price': df['low'].iloc[i],
                    'strength': self.liquidity_cluster_size
                })
            
            # Check for bearish liquidity (equal highs)
            if all(abs(df['high'].iloc[i-j] - df['high'].iloc[i]) < self.fvg_threshold 
                  for j in range(self.liquidity_cluster_size)):
                bearish_zones.append({
                    'start': df.index[i-self.liquidity_cluster_size],
                    'end': df.index[i],
                    'price': df['high'].iloc[i],
                    'strength': self.liquidity_cluster_size
                })
        
        return {
            'bullish': bullish_zones[-3:] if bullish_zones else [],  # Keep last 3
            'bearish': bearish_zones[-3:] if bearish_zones else []   # Keep last 3
        }

    def detect_market_structure(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect market structure including swing highs/lows and BOS/CHOCH
        """
        swing_highs = []
        swing_lows = []
        bos_points = []
        choch_points = []
        
        # Detect swing highs and lows
        for i in range(2, len(df) - 2):
            # Swing High
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and
                df['high'].iloc[i] > df['high'].iloc[i+2]):
                swing_highs.append({
                    'time': df.index[i],
                    'price': df['high'].iloc[i],
                    'strength': (df['high'].iloc[i] - df['low'].iloc[i]) / df['low'].iloc[i]
                })
            
            # Swing Low
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and
                df['low'].iloc[i] < df['low'].iloc[i+2]):
                swing_lows.append({
                    'time': df.index[i],
                    'price': df['low'].iloc[i],
                    'strength': (df['high'].iloc[i] - df['low'].iloc[i]) / df['low'].iloc[i]
                })
        
        # Detect BOS and CHOCH
        for i in range(1, len(swing_highs) - 1):
            # Bullish BOS
            if (swing_highs[i]['price'] > swing_highs[i-1]['price'] and
                swing_lows[i]['price'] > swing_lows[i-1]['price']):
                bos_points.append({
                    'time': swing_highs[i]['time'],
                    'type': 'bullish',
                    'price': swing_highs[i]['price']
                })
            
            # Bearish BOS
            if (swing_highs[i]['price'] < swing_highs[i-1]['price'] and
                swing_lows[i]['price'] < swing_lows[i-1]['price']):
                bos_points.append({
                    'time': swing_lows[i]['time'],
                    'type': 'bearish',
                    'price': swing_lows[i]['price']
                })
        
        return {
            'swing_highs': swing_highs[-5:] if swing_highs else [],  # Keep last 5
            'swing_lows': swing_lows[-5:] if swing_lows else [],     # Keep last 5
            'bos': bos_points[-3:] if bos_points else [],            # Keep last 3
            'choch': choch_points[-3:] if choch_points else []       # Keep last 3
        }

    def _check_bullish_setup(self, df: pd.DataFrame, components: Dict) -> Optional[Dict]:
        """
        Check for bullish trading setup
        """
        current_price = df['close'].iloc[-1]
        
        # Check for bullish order block
        bullish_ob = next((ob for ob in components['order_blocks']['bullish'] 
                          if ob['low'] < current_price < ob['high']), None)
        
        # Check for bullish FVG
        bullish_fvg = next((fvg for fvg in components['fair_value_gaps']['bullish']
                           if fvg['bottom'] < current_price < fvg['top']), None)
        
        # Check for bullish liquidity zone
        bullish_liq = next((liq for liq in components['liquidity_zones']['bullish']
                           if abs(liq['price'] - current_price) < self.fvg_threshold), None)
        
        # Check for bullish market structure
        bullish_bos = next((bos for bos in components['market_structure']['bos']
                           if bos['type'] == 'bullish' and bos['time'] > df.index[-10]), None)
        
        # Calculate setup strength
        setup_strength = 0
        if bullish_ob: setup_strength += 1
        if bullish_fvg: setup_strength += 1
        if bullish_liq: setup_strength += 1
        if bullish_bos: setup_strength += 1
        
        # Return signal if setup is strong enough
        if setup_strength >= 2:
            return {
                'type': 'bullish',
                'entry': current_price,
                'stop_loss': min(bullish_ob['low'] if bullish_ob else current_price * 0.99,
                               bullish_fvg['bottom'] if bullish_fvg else current_price * 0.99),
                'take_profit': current_price + (current_price - min(bullish_ob['low'] if bullish_ob else current_price * 0.99,
                                                                  bullish_fvg['bottom'] if bullish_fvg else current_price * 0.99)) * 2,
                'confidence': setup_strength / 4,
                'components': {
                    'order_block': bullish_ob,
                    'fair_value_gap': bullish_fvg,
                    'liquidity_zone': bullish_liq,
                    'market_structure': bullish_bos
                }
            }
        
        return None

    def _check_bearish_setup(self, df: pd.DataFrame, components: Dict) -> Optional[Dict]:
        """
        Check for bearish trading setup
        """
        current_price = df['close'].iloc[-1]
        
        # Check for bearish order block
        bearish_ob = next((ob for ob in components['order_blocks']['bearish']
                          if ob['low'] < current_price < ob['high']), None)
        
        # Check for bearish FVG
        bearish_fvg = next((fvg for fvg in components['fair_value_gaps']['bearish']
                           if fvg['bottom'] < current_price < fvg['top']), None)
        
        # Check for bearish liquidity zone
        bearish_liq = next((liq for liq in components['liquidity_zones']['bearish']
                           if abs(liq['price'] - current_price) < self.fvg_threshold), None)
        
        # Check for bearish market structure
        bearish_bos = next((bos for bos in components['market_structure']['bos']
                           if bos['type'] == 'bearish' and bos['time'] > df.index[-10]), None)
        
        # Calculate setup strength
        setup_strength = 0
        if bearish_ob: setup_strength += 1
        if bearish_fvg: setup_strength += 1
        if bearish_liq: setup_strength += 1
        if bearish_bos: setup_strength += 1
        
        # Return signal if setup is strong enough
        if setup_strength >= 2:
            return {
                'type': 'bearish',
                'entry': current_price,
                'stop_loss': max(bearish_ob['high'] if bearish_ob else current_price * 1.01,
                               bearish_fvg['top'] if bearish_fvg else current_price * 1.01),
                'take_profit': current_price - (max(bearish_ob['high'] if bearish_ob else current_price * 1.01,
                                                  bearish_fvg['top'] if bearish_fvg else current_price * 1.01) - current_price) * 2,
                'confidence': setup_strength / 4,
                'components': {
                    'order_block': bearish_ob,
                    'fair_value_gap': bearish_fvg,
                    'liquidity_zone': bearish_liq,
                    'market_structure': bearish_bos
                }
            }
        
        return None

    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze market data and return trading signal if conditions are met
        """
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Get all components
        components = {
            'order_blocks': self.detect_order_blocks(df),
            'fair_value_gaps': self.detect_fair_value_gaps(df),
            'liquidity_zones': self.detect_liquidity_zones(df),
            'market_structure': self.detect_market_structure(df)
        }
        
        # Check trend strength
        trend, trend_strength = self._check_trend_strength(df)
        
        # Check momentum
        momentum, momentum_strength = self._check_momentum(df)
        
        # Check volatility
        volatility = self._check_volatility(df)
        
        # Check volume profile
        volume_profile = self._check_volume_profile(df)
        
        # Check for bullish setup
        if trend == 'bullish' and momentum == 'bullish':
            if self._check_optimal_entry(df, 'bullish'):
                bullish_signal = self._check_bullish_setup(df, components)
                if bullish_signal:
                    # Enhance signal with additional analysis
                    bullish_signal.update({
                        'trend_strength': trend_strength,
                        'momentum_strength': momentum_strength,
                        'volatility': volatility,
                        'volume_profile': volume_profile,
                        'indicators': {
                            'rsi': df['rsi'].iloc[-1],
                            'macd': df['macd'].iloc[-1],
                            'stoch_k': df['stoch_k'].iloc[-1],
                            'stoch_d': df['stoch_d'].iloc[-1],
                            'bb_position': (df['close'].iloc[-1] - df['bb_lower'].iloc[-1]) / 
                                         (df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1])
                        }
                    })
                    return bullish_signal
        
        # Check for bearish setup
        if trend == 'bearish' and momentum == 'bearish':
            if self._check_optimal_entry(df, 'bearish'):
                bearish_signal = self._check_bearish_setup(df, components)
                if bearish_signal:
                    # Enhance signal with additional analysis
                    bearish_signal.update({
                        'trend_strength': trend_strength,
                        'momentum_strength': momentum_strength,
                        'volatility': volatility,
                        'volume_profile': volume_profile,
                        'indicators': {
                            'rsi': df['rsi'].iloc[-1],
                            'macd': df['macd'].iloc[-1],
                            'stoch_k': df['stoch_k'].iloc[-1],
                            'stoch_d': df['stoch_d'].iloc[-1],
                            'bb_position': (df['close'].iloc[-1] - df['bb_lower'].iloc[-1]) / 
                                         (df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1])
                        }
                    })
                    return bearish_signal
        
        return None 