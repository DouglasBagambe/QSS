//+------------------------------------------------------------------+
//|                                             QSS_SignalSender.mqh |
//|                        Copyright 2025, Quantum SmartFlow Systems |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantum SmartFlow Systems"
#property link      "https://yoursite.com"

#include "config.mqh"

//+------------------------------------------------------------------+
//| Send signal to Telegram                                          |
//+------------------------------------------------------------------+
bool SendTelegramSignal(const SignalInfo& signal)
{
   if(!EnableTelegramAlerts)
   {
      Print("Telegram alerts disabled");
      return false;
   }
   
   if(StringLen(TelegramBotToken) == 0 || StringLen(TelegramChatID) == 0)
   {
      Print("Telegram bot token or chat ID not configured");
      return false;
   }
   
   // Check cooldown period
   if(TimeCurrent() - g_lastSignalTime < SignalCooldownSeconds)
   {
      Print("Signal cooldown active - skipping Telegram message");
      return false;
   }
   
   string message = FormatTelegramMessage(signal);
   
   // Prepare URL and headers
   string url = "https://api.telegram.org/bot" + TelegramBotToken + "/sendMessage";
   string headers = "Content-Type: application/json\r\n";
   
   // Prepare JSON payload
   string json_data = "{";
   json_data += "\"chat_id\":\"" + TelegramChatID + "\",";
   json_data += "\"text\":\"" + message + "\",";
   json_data += "\"parse_mode\":\"HTML\"";
   json_data += "}";
   
   // Convert string to char array
   char post_data[];
   StringToCharArray(json_data, post_data, 0, StringLen(json_data));
   
   char result[];
   string result_headers;
   
   Print("Sending Telegram message: ", message);
   
   // Make HTTP POST request
   int res = WebRequest(
      "POST",
      url,
      headers,
      TelegramTimeout,
      post_data,
      result,
      result_headers
   );
   
   if(res == 200)
   {
      string response = CharArrayToString(result);
      Print("Telegram message sent successfully: ", response);
      g_lastSignalTime = TimeCurrent();
      return true;
   }
   else
   {
      Print("Failed to send Telegram message. HTTP Code: ", res);
      Print("Response: ", CharArrayToString(result));
      Print("Headers: ", result_headers);
      return false;
   }
}

//+------------------------------------------------------------------+
//| Format signal message for Telegram                               |
//+------------------------------------------------------------------+
string FormatTelegramMessage(const SignalInfo& signal)
{
   string direction_emoji = (signal.bias == BIAS_BULLISH) ? "📈" : "📉";
   string signal_type = (signal.bias == BIAS_BULLISH) ? "LONG" : "SHORT";
   
   // Get market structure
   string market_structure = GetMarketStructure();
   
   // Get technical indicators
   string indicators = GetTechnicalIndicators();
   
   // Get recent price action
   string price_action = GetRecentPriceAction();
   
   // Get volume profile
   string volume_profile = GetVolumeProfile();
   
   // Get support/resistance levels
   string key_levels = GetKeyLevels();
   
   string message = "";
   message += direction_emoji + " <b>" + signal_type + " SIGNAL - " + signal.symbol + "</b>\\n\\n";
   
   // Signal Details
   message += "🎯 <b>Signal Details:</b>\\n";
   message += "🔹 <b>Bias:</b> " + BiasToString(signal.bias) + " (" + TimeframeToString(HTF_Bias_Period) + ")\\n";
   message += "🔸 <b>Zone:</b> " + signal.zone_description + " @ " + DoubleToString(signal.entry_price, _Digits) + "\\n";
   message += "🎯 <b>Target:</b> 1:" + DoubleToString(signal.risk_reward, 1) + " R:R\\n";
   message += "⏰ <b>Time:</b> " + TimeToString(signal.signal_time, TIME_DATE|TIME_MINUTES) + "\\n\\n";
   
   // Market Structure
   message += "📊 <b>Market Structure:</b>\\n";
   message += market_structure + "\\n\\n";
   
   // Technical Indicators
   message += "📈 <b>Technical Indicators:</b>\\n";
   message += indicators + "\\n\\n";
   
   // Price Action
   message += "📉 <b>Recent Price Action:</b>\\n";
   message += price_action + "\\n\\n";
   
   // Volume Profile
   message += "📊 <b>Volume Profile:</b>\\n";
   message += volume_profile + "\\n\\n";
   
   // Key Levels
   message += "🎯 <b>Key Levels:</b>\\n";
   message += key_levels + "\\n\\n";
   
   message += "#QuantumSmartFlow #ICT #SMC";
   
   return message;
}

//+------------------------------------------------------------------+
//| Get market structure analysis                                    |
//+------------------------------------------------------------------+
string GetMarketStructure()
{
   string structure = "";
   
   // Get recent swing highs and lows
   double highs[], lows[];
   ArrayResize(highs, 20);
   ArrayResize(lows, 20);
   
   int copied = CopyHigh(_Symbol, HTF_Bias_Period, 1, 20, highs);
   CopyLow(_Symbol, HTF_Bias_Period, 1, 20, lows);
   
   if(copied < 10) return "Insufficient data";
   
   // Analyze trend structure
   bool higher_highs = true;
   bool higher_lows = true;
   bool lower_highs = true;
   bool lower_lows = true;
   
   for(int i = 1; i < 5; i++)
   {
      if(highs[i] <= highs[i-1]) higher_highs = false;
      if(lows[i] <= lows[i-1]) higher_lows = false;
      if(highs[i] >= highs[i-1]) lower_highs = false;
      if(lows[i] >= lows[i-1]) lower_lows = false;
   }
   
   if(higher_highs && higher_lows)
      structure += "• Strong Uptrend\\n";
   else if(lower_highs && lower_lows)
      structure += "• Strong Downtrend\\n";
   else if(higher_highs)
      structure += "• Higher Highs\\n";
   else if(higher_lows)
      structure += "• Higher Lows\\n";
   else if(lower_highs)
      structure += "• Lower Highs\\n";
   else if(lower_lows)
      structure += "• Lower Lows\\n";
   else
      structure += "• Range Bound\\n";
   
   // Add structure break info
   if(DetectCHOCH())
      structure += "• CHOCH Detected\\n";
   if(DetectBOS())
      structure += "• BOS Detected\\n";
   
   return structure;
}

//+------------------------------------------------------------------+
//| Get technical indicators data                                    |
//+------------------------------------------------------------------+
string GetTechnicalIndicators()
{
   string indicators = "";
   
   // RSI
   int rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   double rsi[];
   if(CopyBuffer(rsi_handle, 0, 0, 1, rsi) > 0)
   {
      indicators += "• RSI: " + DoubleToString(rsi[0], 1);
      if(rsi[0] > 70) indicators += " (Overbought)\\n";
      else if(rsi[0] < 30) indicators += " (Oversold)\\n";
      else indicators += "\\n";
   }
   
   // MACD
   int macd_handle = iMACD(_Symbol, PERIOD_CURRENT, 12, 26, 9, PRICE_CLOSE);
   double macd_main[], macd_signal[];
   if(CopyBuffer(macd_handle, 0, 0, 2, macd_main) > 0 && 
      CopyBuffer(macd_handle, 1, 0, 2, macd_signal) > 0)
   {
      indicators += "• MACD: " + DoubleToString(macd_main[0], 5);
      if(macd_main[0] > macd_signal[0]) indicators += " (Bullish)\\n";
      else indicators += " (Bearish)\\n";
   }
   
   // Bollinger Bands
   int bb_handle = iBands(_Symbol, PERIOD_CURRENT, 20, 0, 2, PRICE_CLOSE);
   double bb_upper[], bb_lower[], bb_middle[];
   if(CopyBuffer(bb_handle, 1, 0, 1, bb_upper) > 0 && 
      CopyBuffer(bb_handle, 2, 0, 1, bb_lower) > 0 &&
      CopyBuffer(bb_handle, 0, 0, 1, bb_middle) > 0)
   {
      double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      indicators += "• BB Position: ";
      if(current_price > bb_upper[0]) indicators += "Above Upper\\n";
      else if(current_price < bb_lower[0]) indicators += "Below Lower\\n";
      else indicators += "Inside Bands\\n";
      
      // Add BB width
      double bb_width = (bb_upper[0] - bb_lower[0]) / bb_middle[0] * 100;
      indicators += "• BB Width: " + DoubleToString(bb_width, 2) + "%\\n";
   }
   
   // Stochastic
   int stoch_handle = iStochastic(_Symbol, PERIOD_CURRENT, 5, 3, 3, MODE_SMA, STO_LOWHIGH);
   double stoch_main[], stoch_signal[];
   if(CopyBuffer(stoch_handle, 0, 0, 1, stoch_main) > 0 && 
      CopyBuffer(stoch_handle, 1, 0, 1, stoch_signal) > 0)
   {
      indicators += "• Stochastic: " + DoubleToString(stoch_main[0], 1);
      if(stoch_main[0] > 80) indicators += " (Overbought)\\n";
      else if(stoch_main[0] < 20) indicators += " (Oversold)\\n";
      else indicators += "\\n";
   }
   
   // ADX
   int adx_handle = iADX(_Symbol, PERIOD_CURRENT, 14);
   double adx_main[], adx_plus[], adx_minus[];
   if(CopyBuffer(adx_handle, 0, 0, 1, adx_main) > 0 && 
      CopyBuffer(adx_handle, 1, 0, 1, adx_plus) > 0 &&
      CopyBuffer(adx_handle, 2, 0, 1, adx_minus) > 0)
   {
      indicators += "• ADX: " + DoubleToString(adx_main[0], 1);
      if(adx_main[0] > 25) indicators += " (Strong Trend)\\n";
      else indicators += " (Weak Trend)\\n";
      
      if(adx_plus[0] > adx_minus[0])
         indicators += "• Trend Direction: Bullish\\n";
      else
         indicators += "• Trend Direction: Bearish\\n";
   }
   
   // Ichimoku Cloud
   int ichimoku_handle = iIchimoku(_Symbol, PERIOD_CURRENT, 9, 26, 52);
   double tenkan[], kijun[], senkou_a[], senkou_b[];
   if(CopyBuffer(ichimoku_handle, 0, 0, 1, tenkan) > 0 && 
      CopyBuffer(ichimoku_handle, 1, 0, 1, kijun) > 0 &&
      CopyBuffer(ichimoku_handle, 2, 0, 1, senkou_a) > 0 &&
      CopyBuffer(ichimoku_handle, 3, 0, 1, senkou_b) > 0)
   {
      double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      indicators += "• Ichimoku Position: ";
      if(current_price > senkou_a[0] && current_price > senkou_b[0])
         indicators += "Above Cloud (Bullish)\\n";
      else if(current_price < senkou_a[0] && current_price < senkou_b[0])
         indicators += "Below Cloud (Bearish)\\n";
      else
         indicators += "Inside Cloud (Neutral)\\n";
   }
   
   // Moving Averages
   int ma20_handle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
   int ma50_handle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_SMA, PRICE_CLOSE);
   int ma200_handle = iMA(_Symbol, PERIOD_CURRENT, 200, 0, MODE_SMA, PRICE_CLOSE);
   
   double ma20[], ma50[], ma200[];
   if(CopyBuffer(ma20_handle, 0, 0, 1, ma20) > 0 && 
      CopyBuffer(ma50_handle, 0, 0, 1, ma50) > 0 &&
      CopyBuffer(ma200_handle, 0, 0, 1, ma200) > 0)
   {
      double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      indicators += "• MA Alignment: ";
      if(current_price > ma20[0] && ma20[0] > ma50[0] && ma50[0] > ma200[0])
         indicators += "Bullish\\n";
      else if(current_price < ma20[0] && ma20[0] < ma50[0] && ma50[0] < ma200[0])
         indicators += "Bearish\\n";
      else
         indicators += "Mixed\\n";
   }
   
   return indicators;
}

//+------------------------------------------------------------------+
//| Get recent price action analysis                                 |
//+------------------------------------------------------------------+
string GetRecentPriceAction()
{
   string price_action = "";
   
   double opens[], highs[], lows[], closes[];
   ArrayResize(opens, 5);
   ArrayResize(highs, 5);
   ArrayResize(lows, 5);
   ArrayResize(closes, 5);
   
   int copied = CopyOpen(_Symbol, PERIOD_CURRENT, 1, 5, opens);
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 5, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 5, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 5, closes);
   
   if(copied < 5) return "Insufficient data";
   
   // Analyze candle patterns
   for(int i = 0; i < 5; i++)
   {
      double body_size = MathAbs(closes[i] - opens[i]);
      double upper_wick = highs[i] - MathMax(opens[i], closes[i]);
      double lower_wick = MathMin(opens[i], closes[i]) - lows[i];
      double total_range = highs[i] - lows[i];
      
      if(body_size > 0)
      {
         // Doji
         if(body_size < total_range * 0.1)
         {
            price_action += "• Doji\\n";
         }
         // Hammer
         else if(lower_wick > body_size * 2 && upper_wick < body_size * 0.5)
         {
            price_action += "• Hammer\\n";
         }
         // Shooting Star
         else if(upper_wick > body_size * 2 && lower_wick < body_size * 0.5)
         {
            price_action += "• Shooting Star\\n";
         }
         // Engulfing Pattern
         else if(i > 0)
         {
            if(closes[i] > opens[i] && closes[i-1] < opens[i-1] && 
               closes[i] > opens[i-1] && opens[i] < closes[i-1])
            {
               price_action += "• Bullish Engulfing\\n";
            }
            else if(closes[i] < opens[i] && closes[i-1] > opens[i-1] && 
                    closes[i] < opens[i-1] && opens[i] > closes[i-1])
            {
               price_action += "• Bearish Engulfing\\n";
            }
         }
         // Morning/Evening Star
         else if(i > 1)
         {
            if(closes[i] > opens[i] && closes[i-1] < opens[i-1] && 
               closes[i-2] < opens[i-2] && body_size > total_range * 0.6)
            {
               price_action += "• Morning Star\\n";
            }
            else if(closes[i] < opens[i] && closes[i-1] > opens[i-1] && 
                    closes[i-2] > opens[i-2] && body_size > total_range * 0.6)
            {
               price_action += "• Evening Star\\n";
            }
         }
         // Strong Candle
         else if(body_size > total_range * 0.7)
         {
            price_action += "• Strong " + (closes[i] > opens[i] ? "Bullish" : "Bearish") + " Candle\\n";
         }
      }
   }
   
   // Add trend analysis
   double ma20_handle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
   double ma50_handle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_SMA, PRICE_CLOSE);
   double ma20[], ma50[];
   
   if(CopyBuffer(ma20_handle, 0, 0, 1, ma20) > 0 && 
      CopyBuffer(ma50_handle, 0, 0, 1, ma50) > 0)
   {
      if(ma20[0] > ma50[0])
         price_action += "• Uptrend (MA20 > MA50)\\n";
      else
         price_action += "• Downtrend (MA20 < MA50)\\n";
   }
   
   return price_action;
}

//+------------------------------------------------------------------+
//| Get volume profile analysis                                      |
//+------------------------------------------------------------------+
string GetVolumeProfile()
{
   string volume_profile = "";
   
   long volumes[];
   ArrayResize(volumes, 20);
   
   if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 20, volumes) > 0)
   {
      double avg_volume = 0;
      for(int i = 0; i < 20; i++)
         avg_volume += volumes[i];
      avg_volume /= 20;
      
      volume_profile += "• Average Volume: " + DoubleToString(avg_volume, 0) + "\\n";
      
      if(volumes[0] > avg_volume * 1.5)
         volume_profile += "• High Volume Bar\\n";
      else if(volumes[0] < avg_volume * 0.5)
         volume_profile += "• Low Volume Bar\\n";
   }
   
   return volume_profile;
}

//+------------------------------------------------------------------+
//| Get key support and resistance levels                            |
//+------------------------------------------------------------------+
string GetKeyLevels()
{
   string key_levels = "";
   
   // Get recent swing highs and lows
   double highs[], lows[];
   ArrayResize(highs, 50);
   ArrayResize(lows, 50);
   
   int copied = CopyHigh(_Symbol, PERIOD_CURRENT, 1, 50, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 50, lows);
   
   if(copied < 10) return "Insufficient data";
   
   // Find significant levels
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double min_distance = 20 * point; // Minimum distance between levels
   
   // Resistance levels
   for(int i = 0; i < copied; i++)
   {
      if(highs[i] > current_price)
      {
         bool is_unique = true;
         for(int j = 0; j < i; j++)
         {
            if(MathAbs(highs[i] - highs[j]) < min_distance)
            {
               is_unique = false;
               break;
            }
         }
         if(is_unique)
            key_levels += "• R: " + DoubleToString(highs[i], _Digits) + "\\n";
      }
   }
   
   // Support levels
   for(int i = 0; i < copied; i++)
   {
      if(lows[i] < current_price)
      {
         bool is_unique = true;
         for(int j = 0; j < i; j++)
         {
            if(MathAbs(lows[i] - lows[j]) < min_distance)
            {
               is_unique = false;
               break;
            }
         }
         if(is_unique)
            key_levels += "• S: " + DoubleToString(lows[i], _Digits) + "\\n";
      }
   }
   
   return key_levels;
}

//+------------------------------------------------------------------+
//| Send test message to verify Telegram connection                  |
//+------------------------------------------------------------------+
bool SendTelegramTest()
{
   SignalInfo test_signal;
   test_signal.signal_time = TimeCurrent();
   test_signal.symbol = _Symbol;
   test_signal.bias = BIAS_BULLISH;
   test_signal.zone_description = "TEST - System Online";
   test_signal.entry_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   test_signal.risk_reward = 2.0;
   
   return SendTelegramSignal(test_signal);
}

//+------------------------------------------------------------------+
//| Log signal details for debugging                                 |
//+------------------------------------------------------------------+
void LogSignalDetails(const SignalInfo& signal)
{
   Print("=== SIGNAL GENERATED ===");
   Print("Time: ", TimeToString(signal.signal_time, TIME_DATE|TIME_SECONDS));
   Print("Symbol: ", signal.symbol);
   Print("Bias: ", BiasToString(signal.bias));
   Print("Zone: ", signal.zone_description);
   Print("Entry: ", DoubleToString(signal.entry_price, _Digits));
   Print("Stop Loss: ", DoubleToString(signal.stop_loss, _Digits));
   Print("Take Profit: ", DoubleToString(signal.take_profit, _Digits));
   Print("Risk:Reward: 1:", DoubleToString(signal.risk_reward, 1));
   Print("========================");
}

//+------------------------------------------------------------------+
//| Send market update notification                                  |
//+------------------------------------------------------------------+
bool SendMarketUpdate(string update_text)
{
   if(!EnableTelegramAlerts) return false;
   
   string url = "https://api.telegram.org/bot" + TelegramBotToken + "/sendMessage";
   string headers = "Content-Type: application/json\r\n";
   
   string message = "🔄 <b>Market Update - " + _Symbol + "</b>\\n";
   message += update_text + "\\n";
   message += "⏰ " + TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES) + "\\n";
   message += "#MarketUpdate #QuantumSmartFlow";
   
   string json_data = "{";
   json_data += "\"chat_id\":\"" + TelegramChatID + "\",";
   json_data += "\"text\":\"" + message + "\",";
   json_data += "\"parse_mode\":\"HTML\"";
   json_data += "}";
   
   char post_data[];
   StringToCharArray(json_data, post_data, 0, StringLen(json_data));
   
   char result[];
   string result_headers;
   
   int res = WebRequest("POST", url, headers, TelegramTimeout, post_data, result, result_headers);
   
   return (res == 200);
}

//+------------------------------------------------------------------+
//| Get advanced pattern recognition                                 |
//+------------------------------------------------------------------+
string GetAdvancedPatterns()
{
   string patterns = "";
   
   // Get price data
   double opens[], highs[], lows[], closes[];
   ArrayResize(opens, 100);
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyOpen(_Symbol, PERIOD_CURRENT, 1, 100, opens);
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Elliott Wave Analysis
   patterns += "🌊 <b>Elliott Wave Analysis</b>\\n";
   int wave_count = CountElliottWaves(highs, lows);
   if(wave_count > 0)
   {
      patterns += "• Wave Count: " + IntegerToString(wave_count) + "\\n";
      patterns += "• Wave Position: " + GetWavePosition() + "\\n";
      patterns += "• Wave Structure: " + GetWaveStructure() + "\\n";
   }
   
   // Harmonic Patterns
   patterns += "🎯 <b>Harmonic Patterns</b>\\n";
   string harmonic = DetectHarmonicPattern(highs, lows);
   if(StringLen(harmonic) > 0)
   {
      patterns += "• " + harmonic + "\\n";
   }
   
   // Divergence Analysis
   patterns += "📊 <b>Divergence Analysis</b>\\n";
   string divergences = DetectDivergences();
   if(StringLen(divergences) > 0)
   {
      patterns += divergences;
   }
   
   // Volume Profile
   patterns += "📈 <b>Volume Profile</b>\\n";
   string volume_profile = AnalyzeVolumeProfile();
   if(StringLen(volume_profile) > 0)
   {
      patterns += volume_profile;
   }
   
   // Market Structure
   patterns += "🏗️ <b>Market Structure</b>\\n";
   string structure = AnalyzeMarketStructure();
   if(StringLen(structure) > 0)
   {
      patterns += structure;
   }
   
   // Advanced Patterns
   patterns += "🎨 <b>Advanced Patterns</b>\\n";
   string advanced = DetectAdvancedPatterns();
   if(StringLen(advanced) > 0)
   {
      patterns += advanced;
   }
   
   // Order Flow Analysis
   patterns += "📊 <b>Order Flow Analysis</b>\\n";
   string order_flow = AnalyzeOrderFlow();
   if(StringLen(order_flow) > 0)
   {
      patterns += order_flow;
   }
   
   // Market Profile
   patterns += "📈 <b>Market Profile</b>\\n";
   string market_profile = AnalyzeMarketProfile();
   if(StringLen(market_profile) > 0)
   {
      patterns += market_profile;
   }
   
   return patterns;
}

//+------------------------------------------------------------------+
//| Count Elliott Waves                                              |
//+------------------------------------------------------------------+
int CountElliottWaves(const double &highs[], const double &lows[])
{
   int wave_count = 0;
   bool in_impulse = false;
   double last_high = 0, last_low = 0;
   
   for(int i = 2; i < ArraySize(highs) - 2; i++)
   {
      // Wave 1
      if(!in_impulse && highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
         highs[i] > highs[i+1] && highs[i] > highs[i+2])
      {
         wave_count++;
         in_impulse = true;
         last_high = highs[i];
         continue;
      }
      
      // Wave 2
      if(in_impulse && lows[i] < lows[i-1] && lows[i] < lows[i-2] &&
         lows[i] < lows[i+1] && lows[i] < lows[i+2] && lows[i] > last_low)
      {
         wave_count++;
         last_low = lows[i];
         continue;
      }
      
      // Wave 3
      if(in_impulse && highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
         highs[i] > highs[i+1] && highs[i] > highs[i+2] && highs[i] > last_high)
      {
         wave_count++;
         last_high = highs[i];
         continue;
      }
      
      // Wave 4
      if(in_impulse && lows[i] < lows[i-1] && lows[i] < lows[i-2] &&
         lows[i] < lows[i+1] && lows[i] < lows[i+2] && lows[i] > last_low)
      {
         wave_count++;
         last_low = lows[i];
         continue;
      }
      
      // Wave 5
      if(in_impulse && highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
         highs[i] > highs[i+1] && highs[i] > highs[i+2] && highs[i] > last_high)
      {
         wave_count++;
         in_impulse = false;
         continue;
      }
   }
   
   return wave_count;
}

//+------------------------------------------------------------------+
//| Get current wave position                                        |
//+------------------------------------------------------------------+
string GetWavePosition()
{
   double ma20_handle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
   double ma50_handle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_SMA, PRICE_CLOSE);
   double ma200_handle = iMA(_Symbol, PERIOD_CURRENT, 200, 0, MODE_SMA, PRICE_CLOSE);
   
   double ma20[], ma50[], ma200[];
   if(CopyBuffer(ma20_handle, 0, 0, 1, ma20) > 0 && 
      CopyBuffer(ma50_handle, 0, 0, 1, ma50) > 0 &&
      CopyBuffer(ma200_handle, 0, 0, 1, ma200) > 0)
   {
      if(ma20[0] > ma50[0] && ma50[0] > ma200[0])
         return "Impulse Wave (1-3-5)";
      else if(ma20[0] < ma50[0] && ma50[0] < ma200[0])
         return "Corrective Wave (A-B-C)";
   }
   return "Unknown";
}

//+------------------------------------------------------------------+
//| Get wave structure                                               |
//+------------------------------------------------------------------+
string GetWaveStructure()
{
   string structure = "";
   
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   
   // Analyze wave structure
   bool is_impulse = true;
   bool is_corrective = true;
   
   for(int i = 2; i < ArraySize(highs) - 2; i++)
   {
      // Check for impulse characteristics
      if(highs[i] <= highs[i-1] || highs[i] <= highs[i-2] ||
         highs[i] <= highs[i+1] || highs[i] <= highs[i+2])
      {
         is_impulse = false;
      }
      
      // Check for corrective characteristics
      if(lows[i] >= lows[i-1] || lows[i] >= lows[i-2] ||
         lows[i] >= lows[i+1] || lows[i] >= lows[i+2])
      {
         is_corrective = false;
      }
   }
   
   if(is_impulse)
      structure = "Impulse Wave (1-2-3-4-5)";
   else if(is_corrective)
      structure = "Corrective Wave (A-B-C)";
   else
      structure = "Complex Structure";
   
   return structure;
}

//+------------------------------------------------------------------+
//| Detect harmonic patterns                                         |
//+------------------------------------------------------------------+
string DetectHarmonicPattern(const double &highs[], const double &lows[])
{
   string pattern = "";
   
   // Gartley Pattern
   if(IsGartleyPattern(highs, lows))
      pattern = "Gartley Pattern Detected";
   
   // Butterfly Pattern
   else if(IsButterflyPattern(highs, lows))
      pattern = "Butterfly Pattern Detected";
   
   // Bat Pattern
   else if(IsBatPattern(highs, lows))
      pattern = "Bat Pattern Detected";
   
   // Crab Pattern
   else if(IsCrabPattern(highs, lows))
      pattern = "Crab Pattern Detected";
   
   return pattern;
}

//+------------------------------------------------------------------+
//| Detect divergences                                               |
//+------------------------------------------------------------------+
string DetectDivergences()
{
   string divergences = "";
   
   // RSI Divergence
   int rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   double rsi[];
   if(CopyBuffer(rsi_handle, 0, 0, 20, rsi) > 0)
   {
      // Bullish Divergence
      if(IsBullishDivergence(rsi))
         divergences += "• Bullish RSI Divergence\\n";
      
      // Bearish Divergence
      if(IsBearishDivergence(rsi))
         divergences += "• Bearish RSI Divergence\\n";
   }
   
   // MACD Divergence
   int macd_handle = iMACD(_Symbol, PERIOD_CURRENT, 12, 26, 9, PRICE_CLOSE);
   double macd_main[];
   if(CopyBuffer(macd_handle, 0, 0, 20, macd_main) > 0)
   {
      // Bullish Divergence
      if(IsBullishDivergence(macd_main))
         divergences += "• Bullish MACD Divergence\\n";
      
      // Bearish Divergence
      if(IsBearishDivergence(macd_main))
         divergences += "• Bearish MACD Divergence\\n";
   }
   
   return divergences;
}

//+------------------------------------------------------------------+
//| Analyze volume profile                                           |
//+------------------------------------------------------------------+
string AnalyzeVolumeProfile()
{
   string profile = "";
   
   // Get volume data
   long volumes[];
   ArrayResize(volumes, 20);
   CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 20, volumes);
   
   // Calculate average volume
   long avg_volume = 0;
   for(int i = 0; i < ArraySize(volumes); i++)
      avg_volume += volumes[i];
   avg_volume /= ArraySize(volumes);
   
   // Analyze recent volume
   if(volumes[0] > avg_volume * 1.5)
      profile += "• High Volume (Above Average)\\n";
   else if(volumes[0] < avg_volume * 0.5)
      profile += "• Low Volume (Below Average)\\n";
   
   // Volume trend
   bool increasing = true;
   bool decreasing = true;
   for(int i = 1; i < ArraySize(volumes); i++)
   {
      if(volumes[i] <= volumes[i-1]) increasing = false;
      if(volumes[i] >= volumes[i-1]) decreasing = false;
   }
   
   if(increasing)
      profile += "• Increasing Volume Trend\\n";
   else if(decreasing)
      profile += "• Decreasing Volume Trend\\n";
   
   return profile;
}

//+------------------------------------------------------------------+
//| Analyze market structure                                         |
//+------------------------------------------------------------------+
string AnalyzeMarketStructure()
{
   string structure = "";
   
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 50);
   ArrayResize(lows, 50);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 50, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 50, lows);
   
   // Higher Highs and Higher Lows
   bool higher_highs = true;
   bool higher_lows = true;
   for(int i = 1; i < ArraySize(highs); i++)
   {
      if(highs[i] <= highs[i-1]) higher_highs = false;
      if(lows[i] <= lows[i-1]) higher_lows = false;
   }
   
   if(higher_highs && higher_lows)
      structure += "• Higher Highs and Higher Lows (Uptrend)\\n";
   
   // Lower Highs and Lower Lows
   bool lower_highs = true;
   bool lower_lows = true;
   for(int i = 1; i < ArraySize(highs); i++)
   {
      if(highs[i] >= highs[i-1]) lower_highs = false;
      if(lows[i] >= lows[i-1]) lower_lows = false;
   }
   
   if(lower_highs && lower_lows)
      structure += "• Lower Highs and Lower Lows (Downtrend)\\n";
   
   // Range
   double highest_high = highs[ArrayMaximum(highs, 0, ArraySize(highs))];
   double lowest_low = lows[ArrayMinimum(lows, 0, ArraySize(lows))];
   double range = highest_high - lowest_low;
   double avg_range = range / ArraySize(highs);
   
   if(avg_range < _Point * 10)
      structure += "• Tight Range (Consolidation)\\n";
   else if(avg_range > _Point * 50)
      structure += "• Wide Range (Volatile)\\n";
   
   return structure;
}

//+------------------------------------------------------------------+
//| Detect advanced patterns                                         |
//+------------------------------------------------------------------+
string DetectAdvancedPatterns()
{
   string patterns = "";
   
   // Get price data
   double opens[], highs[], lows[], closes[];
   ArrayResize(opens, 100);
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyOpen(_Symbol, PERIOD_CURRENT, 1, 100, opens);
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Double Top/Bottom
   if(IsDoubleTop(highs, lows))
      patterns += "• Double Top\\n";
   else if(IsDoubleBottom(highs, lows))
      patterns += "• Double Bottom\\n";
   
   // Triple Top/Bottom
   if(IsTripleTop(highs, lows))
      patterns += "• Triple Top\\n";
   else if(IsTripleBottom(highs, lows))
      patterns += "• Triple Bottom\\n";
   
   // Head and Shoulders
   if(IsHeadAndShoulders(highs, lows))
      patterns += "• Head and Shoulders\\n";
   else if(IsInverseHeadAndShoulders(highs, lows))
      patterns += "• Inverse Head and Shoulders\\n";
   
   // Triangle Patterns
   if(IsAscendingTriangle(highs, lows))
      patterns += "• Ascending Triangle\\n";
   else if(IsDescendingTriangle(highs, lows))
      patterns += "• Descending Triangle\\n";
   else if(IsSymmetricalTriangle(highs, lows))
      patterns += "• Symmetrical Triangle\\n";
   
   // Wedge Patterns
   if(IsRisingWedge(highs, lows))
      patterns += "• Rising Wedge\\n";
   else if(IsFallingWedge(highs, lows))
      patterns += "• Falling Wedge\\n";
   
   // Flag Patterns
   if(IsBullFlag(highs, lows))
      patterns += "• Bull Flag\\n";
   else if(IsBearFlag(highs, lows))
      patterns += "• Bear Flag\\n";
   
   // Pennant Patterns
   if(IsBullPennant(highs, lows))
      patterns += "• Bull Pennant\\n";
   else if(IsBearPennant(highs, lows))
      patterns += "• Bear Pennant\\n";
   
   return patterns;
}

//+------------------------------------------------------------------+
//| Analyze order flow                                               |
//+------------------------------------------------------------------+
string AnalyzeOrderFlow()
{
   string analysis = "";
   
   // Get volume data
   long volumes[];
   ArrayResize(volumes, 20);
   CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 20, volumes);
   
   // Get price data
   double opens[], highs[], lows[], closes[];
   ArrayResize(opens, 20);
   ArrayResize(highs, 20);
   ArrayResize(lows, 20);
   ArrayResize(closes, 20);
   
   CopyOpen(_Symbol, PERIOD_CURRENT, 1, 20, opens);
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 20, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 20, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 20, closes);
   
   // Analyze volume distribution
   long buy_volume = 0;
   long sell_volume = 0;
   
   for(int i = 0; i < ArraySize(volumes); i++)
   {
      if(closes[i] > opens[i])
         buy_volume += volumes[i];
      else
         sell_volume += volumes[i];
   }
   
   // Calculate volume ratio
   double volume_ratio = (double)buy_volume / (double)sell_volume;
   
   if(volume_ratio > 1.5)
      analysis += "• Strong Buying Pressure\\n";
   else if(volume_ratio < 0.67)
      analysis += "• Strong Selling Pressure\\n";
   else
      analysis += "• Balanced Volume\\n";
   
   // Analyze price-volume relationship
   bool price_volume_confirmation = true;
   for(int i = 1; i < ArraySize(volumes); i++)
   {
      if(closes[i] > closes[i-1] && volumes[i] < volumes[i-1])
         price_volume_confirmation = false;
      if(closes[i] < closes[i-1] && volumes[i] < volumes[i-1])
         price_volume_confirmation = false;
   }
   
   if(price_volume_confirmation)
      analysis += "• Price-Volume Confirmation\\n";
   else
      analysis += "• Price-Volume Divergence\\n";
   
   return analysis;
}

//+------------------------------------------------------------------+
//| Analyze market profile                                           |
//+------------------------------------------------------------------+
string AnalyzeMarketProfile()
{
   string profile = "";
   
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 50);
   ArrayResize(lows, 50);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 50, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 50, lows);
   
   // Calculate value area
   double highest_high = highs[ArrayMaximum(highs, 0, ArraySize(highs))];
   double lowest_low = lows[ArrayMinimum(lows, 0, ArraySize(lows))];
   double range = highest_high - lowest_low;
   
   double value_area_high = highest_high - range * 0.25;
   double value_area_low = lowest_low + range * 0.25;
   
   // Get current price
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   if(current_price > value_area_high)
      profile += "• Above Value Area (Overvalued)\\n";
   else if(current_price < value_area_low)
      profile += "• Below Value Area (Undervalued)\\n";
   else
      profile += "• Inside Value Area (Fair Value)\\n";
   
   // Analyze price distribution
   int above_value = 0;
   int below_value = 0;
   
   for(int i = 0; i < ArraySize(highs); i++)
   {
      if(highs[i] > value_area_high)
         above_value++;
      if(lows[i] < value_area_low)
         below_value++;
   }
   
   if(above_value > below_value)
      profile += "• Bullish Price Distribution\\n";
   else if(below_value > above_value)
      profile += "• Bearish Price Distribution\\n";
   else
      profile += "• Neutral Price Distribution\\n";
   
   return profile;
}

//+------------------------------------------------------------------+
//| Fix type conversion warnings                                      |
//+------------------------------------------------------------------+
void SendMarketUpdate()
{
   // ... existing code ...
   
   // Fix type conversion warnings
   double volume_value = (double)volume[0];
   double tick_volume_value = (double)tick_volume[0];
   double spread_value = (double)spread[0];
   
   // ... rest of the code ...
}

//+------------------------------------------------------------------+
//| Pattern recognition functions                                     |
//+------------------------------------------------------------------+
bool IsGartleyPattern(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double xab = MathAbs(highs[start_idx-1] - lows[start_idx-2]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   double abc = MathAbs(lows[start_idx-1] - highs[start_idx]) / MathAbs(highs[start_idx-1] - lows[start_idx-2]);
   double bcd = MathAbs(highs[start_idx] - lows[start_idx+1]) / MathAbs(lows[start_idx-1] - highs[start_idx]);
   double xad = MathAbs(highs[start_idx-1] - lows[start_idx+1]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   
   return (xab >= 0.618 && xab <= 0.786) &&
          (abc >= 0.382 && abc <= 0.886) &&
          (bcd >= 1.272 && bcd <= 1.618) &&
          (xad >= 0.786 && xad <= 0.886);
}

bool IsButterflyPattern(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double xab = MathAbs(highs[start_idx-1] - lows[start_idx-2]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   double abc = MathAbs(lows[start_idx-1] - highs[start_idx]) / MathAbs(highs[start_idx-1] - lows[start_idx-2]);
   double bcd = MathAbs(highs[start_idx] - lows[start_idx+1]) / MathAbs(lows[start_idx-1] - highs[start_idx]);
   double xad = MathAbs(highs[start_idx-1] - lows[start_idx+1]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   
   return (xab >= 0.786 && xab <= 0.886) &&
          (abc >= 0.382 && abc <= 0.886) &&
          (bcd >= 1.618 && bcd <= 2.618) &&
          (xad >= 1.27 && xad <= 1.618);
}

bool IsDoubleTop(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 2) return false;
   
   double first_high = highs[start_idx-2];
   double second_high = highs[start_idx];
   double neckline = lows[start_idx-1];
   
   return MathAbs(first_high - second_high) / first_high < 0.01 &&
          second_high > neckline;
}

bool IsDoubleBottom(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 2) return false;
   
   double first_low = lows[start_idx-2];
   double second_low = lows[start_idx];
   double neckline = highs[start_idx-1];
   
   return MathAbs(first_low - second_low) / first_low < 0.01 &&
          second_low < neckline;
}

bool IsTripleTop(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double first_high = highs[start_idx-4];
   double second_high = highs[start_idx-2];
   double third_high = highs[start_idx];
   double neckline = lows[start_idx-1];
   
   return MathAbs(first_high - second_high) / first_high < 0.01 &&
          MathAbs(second_high - third_high) / second_high < 0.01 &&
          third_high > neckline;
}

bool IsTripleBottom(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double first_low = lows[start_idx-4];
   double second_low = lows[start_idx-2];
   double third_low = lows[start_idx];
   double neckline = highs[start_idx-1];
   
   return MathAbs(first_low - second_low) / first_low < 0.01 &&
          MathAbs(second_low - third_low) / second_low < 0.01 &&
          third_low < neckline;
}

bool IsHeadAndShoulders(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double left_shoulder = highs[start_idx-4];
   double head = highs[start_idx-2];
   double right_shoulder = highs[start_idx];
   double neckline = lows[start_idx-1];
   
   return head > left_shoulder && head > right_shoulder &&
          MathAbs(left_shoulder - right_shoulder) / left_shoulder < 0.01 &&
          head > neckline;
}

bool IsInverseHeadAndShoulders(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double left_shoulder = lows[start_idx-4];
   double head = lows[start_idx-2];
   double right_shoulder = lows[start_idx];
   double neckline = highs[start_idx-1];
   
   return head < left_shoulder && head < right_shoulder &&
          MathAbs(left_shoulder - right_shoulder) / left_shoulder < 0.01 &&
          head < neckline;
}

bool IsAscendingTriangle(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double resistance = highs[start_idx-4];
   double slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return MathAbs(highs[start_idx] - resistance) / resistance < 0.01 &&
          slope > 0;
}

bool IsDescendingTriangle(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double support = lows[start_idx-4];
   double slope = (highs[start_idx] - highs[start_idx-4]) / (start_idx - (start_idx-4));
   
   return MathAbs(lows[start_idx] - support) / support < 0.01 &&
          slope < 0;
}

bool IsRisingWedge(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double upper_slope = (highs[start_idx] - highs[start_idx-4]) / (start_idx - (start_idx-4));
   double lower_slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return upper_slope > 0 && lower_slope > 0 && upper_slope < lower_slope;
}

bool IsFallingWedge(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double upper_slope = (highs[start_idx] - highs[start_idx-4]) / (start_idx - (start_idx-4));
   double lower_slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return upper_slope < 0 && lower_slope < 0 && upper_slope > lower_slope;
}

bool IsBullFlag(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double pole_high = highs[start_idx-4];
   double pole_low = lows[start_idx-4];
   double flag_high = highs[start_idx];
   double flag_low = lows[start_idx];
   
   return pole_high > pole_low &&
          flag_high < pole_high &&
          flag_low > pole_low;
}

bool IsBearFlag(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double pole_high = highs[start_idx-4];
   double pole_low = lows[start_idx-4];
   double flag_high = highs[start_idx];
   double flag_low = lows[start_idx];
   
   return pole_high < pole_low &&
          flag_high > pole_high &&
          flag_low < pole_low;
}

bool IsBullPennant(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double pole_high = highs[start_idx-4];
   double pole_low = lows[start_idx-4];
   double pennant_high = highs[start_idx];
   double pennant_low = lows[start_idx];
   
   return pole_high > pole_low &&
          pennant_high < pole_high &&
          pennant_low > pole_low &&
          (pennant_high - pennant_low) < (pole_high - pole_low);
}

bool IsBearPennant(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double pole_high = highs[start_idx-4];
   double pole_low = lows[start_idx-4];
   double pennant_high = highs[start_idx];
   double pennant_low = lows[start_idx];
   
   return pole_high < pole_low &&
          pennant_high > pole_high &&
          pennant_low < pole_low &&
          (pennant_high - pennant_low) < (pole_high - pole_low);
}

bool IsBullishDivergence(const double &price[], const double &indicator[], int start_idx)
{
   if(start_idx < 2) return false;
   
   double price_low1 = price[start_idx-2];
   double price_low2 = price[start_idx];
   double ind_low1 = indicator[start_idx-2];
   double ind_low2 = indicator[start_idx];
   
   return price_low2 < price_low1 && ind_low2 > ind_low1;
}

bool IsBearishDivergence(const double &price[], const double &indicator[], int start_idx)
{
   if(start_idx < 2) return false;
   
   double price_high1 = price[start_idx-2];
   double price_high2 = price[start_idx];
   double ind_high1 = indicator[start_idx-2];
   double ind_high2 = indicator[start_idx];
   
   return price_high2 > price_high1 && ind_high2 < ind_high1;
}

bool IsBatPattern(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double xab = MathAbs(highs[start_idx-1] - lows[start_idx-2]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   double abc = MathAbs(lows[start_idx-1] - highs[start_idx]) / MathAbs(highs[start_idx-1] - lows[start_idx-2]);
   double bcd = MathAbs(highs[start_idx] - lows[start_idx+1]) / MathAbs(lows[start_idx-1] - highs[start_idx]);
   double xad = MathAbs(highs[start_idx-1] - lows[start_idx+1]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   
   return (xab >= 0.382 && xab <= 0.5) &&
          (abc >= 0.382 && abc <= 0.886) &&
          (bcd >= 1.618 && bcd <= 2.618) &&
          (xad >= 0.886 && xad <= 0.886);
}

bool IsSymmetricalTriangle(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double upper_slope = (highs[start_idx] - highs[start_idx-4]) / (start_idx - (start_idx-4));
   double lower_slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return MathAbs(upper_slope) < 0.1 && MathAbs(lower_slope) < 0.1 &&
          upper_slope < 0 && lower_slope > 0;
}

bool IsCrabPattern(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double xab = MathAbs(highs[start_idx-1] - lows[start_idx-2]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   double abc = MathAbs(lows[start_idx-1] - highs[start_idx]) / MathAbs(highs[start_idx-1] - lows[start_idx-2]);
   double bcd = MathAbs(highs[start_idx] - lows[start_idx+1]) / MathAbs(lows[start_idx-1] - highs[start_idx]);
   double xad = MathAbs(highs[start_idx-1] - lows[start_idx+1]) / MathAbs(highs[start_idx-2] - lows[start_idx-3]);
   
   return (xab >= 0.382 && xab <= 0.618) &&
          (abc >= 0.382 && abc <= 0.886) &&
          (bcd >= 2.618 && bcd <= 3.618) &&
          (xad >= 1.618 && xad <= 1.618);
}

//+------------------------------------------------------------------+
//| Fix function calls                                               |
//+------------------------------------------------------------------+
void CheckPatterns()
{
   double highs[], lows[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   
   // Check harmonic patterns
   if(IsGartleyPattern(highs, lows, 0))
      SendSignal("Gartley Pattern Detected");
   else if(IsButterflyPattern(highs, lows, 0))
      SendSignal("Butterfly Pattern Detected");
   else if(IsBatPattern(highs, lows, 0))
      SendSignal("Bat Pattern Detected");
   else if(IsCrabPattern(highs, lows, 0))
      SendSignal("Crab Pattern Detected");
   
   // Check chart patterns
   if(IsDoubleTop(highs, lows, 0))
      SendSignal("Double Top Detected");
   else if(IsDoubleBottom(highs, lows, 0))
      SendSignal("Double Bottom Detected");
   else if(IsTripleTop(highs, lows, 0))
      SendSignal("Triple Top Detected");
   else if(IsTripleBottom(highs, lows, 0))
      SendSignal("Triple Bottom Detected");
   else if(IsHeadAndShoulders(highs, lows, 0))
      SendSignal("Head and Shoulders Detected");
   else if(IsInverseHeadAndShoulders(highs, lows, 0))
      SendSignal("Inverse Head and Shoulders Detected");
   else if(IsAscendingTriangle(highs, lows, 0))
      SendSignal("Ascending Triangle Detected");
   else if(IsDescendingTriangle(highs, lows, 0))
      SendSignal("Descending Triangle Detected");
   else if(IsSymmetricalTriangle(highs, lows, 0))
      SendSignal("Symmetrical Triangle Detected");
   else if(IsRisingWedge(highs, lows, 0))
      SendSignal("Rising Wedge Detected");
   else if(IsFallingWedge(highs, lows, 0))
      SendSignal("Falling Wedge Detected");
   else if(IsBullFlag(highs, lows, 0))
      SendSignal("Bull Flag Detected");
   else if(IsBearFlag(highs, lows, 0))
      SendSignal("Bear Flag Detected");
   else if(IsBullPennant(highs, lows, 0))
      SendSignal("Bull Pennant Detected");
   else if(IsBearPennant(highs, lows, 0))
      SendSignal("Bear Pennant Detected");
   
   // Check divergences
   double closes[], rsi[];
   ArrayResize(closes, 100);
   ArrayResize(rsi, 100);
   
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate RSI
   for(int i = 0; i < ArraySize(rsi); i++)
   {
      double gain = 0, loss = 0;
      for(int j = i; j < i + 14 && j < ArraySize(closes); j++)
      {
         if(closes[j] > closes[j-1])
            gain += closes[j] - closes[j-1];
         else
            loss += closes[j-1] - closes[j];
      }
      rsi[i] = 100 - (100 / (1 + gain/loss));
   }
   
   if(IsBullishDivergence(closes, rsi, 0))
      SendSignal("Bullish Divergence Detected");
   else if(IsBearishDivergence(closes, rsi, 0))
      SendSignal("Bearish Divergence Detected");
} 