//+------------------------------------------------------------------+
//|                                                QSS_Indicator.mq5 |
//|                        Copyright 2025, Quantum SmartFlow Systems |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantum SmartFlow Systems"
#property link      "https://yoursite.com"
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots   0

#include "config.mqh"
#include "QSS_SignalSender.mqh"

//--- Global Variables
int g_htf_handle;
int g_ltf_handle;
datetime g_lastAnalysisTime = 0;
bool g_initialized = false;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("Initializing Quantum SmartFlow Indicator v" + EXPERT_VERSION);
   
   // Validate inputs
   if(!ValidateInputs())
   {
      Print("Invalid input parameters");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Initialize arrays
   ArrayResize(g_orderBlocks, 0);
   ArrayResize(g_fvgZones, 0);
   
   // Set indicator properties
   IndicatorSetString(INDICATOR_SHORTNAME, EXPERT_NAME + " v" + EXPERT_VERSION);
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);
   
   // Add URL to allowed list for WebRequest
   if(EnableTelegramAlerts && StringLen(TelegramBotToken) > 0)
   {
      string telegram_url = "https://api.telegram.org";
      if(!TerminalInfoInteger(TERMINAL_DLLS_ALLOWED))
      {
         Print("Warning: DLL imports not allowed. Telegram functionality may be limited.");
      }
   }
   
   g_initialized = true;
   Print("Quantum SmartFlow initialized successfully");
   
   // Send test message if enabled
   if(EnableTelegramAlerts && StringLen(TelegramBotToken) > 0 && StringLen(TelegramChatID) > 0)
   {
      Print("Testing Telegram connection...");
      if(SendTelegramTest())
      {
         Print("Telegram connection successful!");
      }
      else
      {
         Print("Telegram connection failed. Check bot token and chat ID.");
      }
   }
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                      |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("Deinitializing Quantum SmartFlow Indicator");
   
   // Clean up visual objects
   if(DrawVisuals)
   {
      CleanupObjects(PREFIX_OB);
      CleanupObjects(PREFIX_FVG);
      CleanupObjects(PREFIX_CHOCH);
      CleanupObjects(PREFIX_BOS);
      CleanupObjects(PREFIX_SIGNAL);
      CleanupObjects(PREFIX_EQUI);
   }
   
   // Clear arrays
   ArrayFree(g_orderBlocks);
   ArrayFree(g_fvgZones);
   
   Print("Quantum SmartFlow cleanup completed");
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   if(!g_initialized || rates_total < 100) return 0;
   
   // Only analyze on new bar
   if(!IsNewBar()) return rates_total;
   
   // Main analysis
   PerformMarketAnalysis();
   
   return rates_total;
}

//+------------------------------------------------------------------+
//| Validate input parameters                                        |
//+------------------------------------------------------------------+
bool ValidateInputs()
{
   if(MinDisplacementPips <= 0)
   {
      Print("Invalid MinDisplacementPips: ", MinDisplacementPips);
      return false;
   }
   
   if(FVG_MinSizePips <= 0)
   {
      Print("Invalid FVG_MinSizePips: ", FVG_MinSizePips);
      return false;
   }
   
   if(OrderBlock_LookbackBars <= 0)
   {
      Print("Invalid OrderBlock_LookbackBars: ", OrderBlock_LookbackBars);
      return false;
   }
   
   if(EnableTelegramAlerts)
   {
      if(StringLen(TelegramBotToken) == 0)
      {
         Print("Telegram alerts enabled but bot token is empty");
         return false;
      }
      
      if(StringLen(TelegramChatID) == 0)
      {
         Print("Telegram alerts enabled but chat ID is empty");
         return false;
      }
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Main market analysis function                                    |
//+------------------------------------------------------------------+
void PerformMarketAnalysis()
{
   // Step 1: Determine HTF bias
   ENUM_SIGNAL_BIAS htf_bias = DetermineHTFBias();
   
   // Step 2: Detect market structure shifts
   bool choch_detected = DetectCHOCH();
   bool bos_detected = DetectBOS();
   
   // Step 3: Identify key zones
   DetectOrderBlocks();
   DetectFairValueGaps();
   
   // Step 4: Check for confluences and generate signals
   CheckForSignalConfluence(htf_bias, choch_detected, bos_detected);
   
   // Step 5: Update visual elements
   if(DrawVisuals)
   {
      UpdateVisualElements();
   }
}

//+------------------------------------------------------------------+
//| Determine Higher Timeframe Bias                                  |
//+------------------------------------------------------------------+
ENUM_SIGNAL_BIAS DetermineHTFBias()
{
   // Get recent swing highs and lows on HTF
   double recent_highs[];
   double recent_lows[];
   datetime recent_times[];
   
   ArrayResize(recent_highs, 10);
   ArrayResize(recent_lows, 10);
   ArrayResize(recent_times, 10);
   
   // Copy recent data from HTF
   int copied = CopyHigh(_Symbol, HTF_Bias_Period, 1, 10, recent_highs);
   CopyLow(_Symbol, HTF_Bias_Period, 1, 10, recent_lows);
   CopyTime(_Symbol, HTF_Bias_Period, 1, 10, recent_times);
   
   if(copied < 5) return BIAS_NEUTRAL;
   
   // Analyze trend structure
   bool higher_highs = true;
   bool higher_lows = true;
   bool lower_highs = true;
   bool lower_lows = true;
   
   for(int i = 1; i < 5; i++)
   {
      if(recent_highs[i] <= recent_highs[i-1]) higher_highs = false;
      if(recent_lows[i] <= recent_lows[i-1]) higher_lows = false;
      if(recent_highs[i] >= recent_highs[i-1]) lower_highs = false;
      if(recent_lows[i] >= recent_lows[i-1]) lower_lows = false;
   }
   
   if(higher_highs && higher_lows) return BIAS_BULLISH;
   if(lower_highs && lower_lows) return BIAS_BEARISH;
   
   return BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| Detect Change of Character (CHOCH)                              |
//+------------------------------------------------------------------+
bool DetectCHOCH()
{
   double highs[], lows[];
   ArrayResize(highs, 20);
   ArrayResize(lows, 20);
   
   int copied = CopyHigh(_Symbol, LTF_Entry_Period, 1, 20, highs);
   CopyLow(_Symbol, LTF_Entry_Period, 1, 20, lows);
   
   if(copied < 10) return false;
   
   // Look for structure break pattern
   for(int i = 5; i < 15; i++)
   {
      // Check for bullish CHOCH (break above previous high after downtrend)
      if(highs[i] > highs[i-1] && highs[i-1] < highs[i-2] && highs[i-2] < highs[i-3])
      {
         DrawCHOCHMarker(iTime(_Symbol, LTF_Entry_Period, copied - i), highs[i], true);
         return true;
      }
      
      // Check for bearish CHOCH (break below previous low after uptrend)  
      if(lows[i] < lows[i-1] && lows[i-1] > lows[i-2] && lows[i-2] > lows[i-3])
      {
         DrawCHOCHMarker(iTime(_Symbol, LTF_Entry_Period, copied - i), lows[i], false);
         return true;
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Detect Break of Structure (BOS)                                 |
//+------------------------------------------------------------------+
bool DetectBOS()
{
   double highs[], lows[], closes[];
   ArrayResize(highs, 15);
   ArrayResize(lows, 15);
   ArrayResize(closes, 15);
   
   int copied = CopyHigh(_Symbol, LTF_Entry_Period, 1, 15, highs);
   CopyLow(_Symbol, LTF_Entry_Period, 1, 15, lows);
   CopyClose(_Symbol, LTF_Entry_Period, 1, 15, closes);
   
   if(copied < 10) return false;
   
   // Look for significant breaks with displacement
   for(int i = 3; i < 10; i++)
   {
      double displacement_size = MathAbs(closes[i] - closes[i-1]);
      double min_displacement = PipsToPrice(MinDisplacementPips);
      
      if(displacement_size >= min_displacement)
      {
         // Bullish BOS
         if(closes[i] > highs[i-1])
         {
            DrawBOSMarker(iTime(_Symbol, LTF_Entry_Period, copied - i), highs[i], true);
            return true;
         }
         
         // Bearish BOS
         if(closes[i] < lows[i-1])
         {
            DrawBOSMarker(iTime(_Symbol, LTF_Entry_Period, copied - i), lows[i], false);
            return true;
         }
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Detect Order Blocks                                             |
//+------------------------------------------------------------------+
void DetectOrderBlocks()
{
   double opens[], highs[], lows[], closes[];
   datetime times[];
   
   int bars_to_analyze = MathMin(OrderBlock_LookbackBars, 100);
   
   ArrayResize(opens, bars_to_analyze);
   ArrayResize(highs, bars_to_analyze);
   ArrayResize(lows, bars_to_analyze);
   ArrayResize(closes, bars_to_analyze);
   ArrayResize(times, bars_to_analyze);
   
   int copied = CopyOpen(_Symbol, LTF_Entry_Period, 1, bars_to_analyze, opens);
   CopyHigh(_Symbol, LTF_Entry_Period, 1, bars_to_analyze, highs);
   CopyLow(_Symbol, LTF_Entry_Period, 1, bars_to_analyze, lows);
   CopyClose(_Symbol, LTF_Entry_Period, 1, bars_to_analyze, closes);
   CopyTime(_Symbol, LTF_Entry_Period, 1, bars_to_analyze, times);
   
   if(copied < 10) return;
   
   // Clear old order blocks
   ArrayResize(g_orderBlocks, 0);
   
   // Look for order block patterns
   for(int i = 5; i < copied - 5; i++)
   {
      double body_size = MathAbs(closes[i] - opens[i]);
      double min_body = PipsToPrice(MinDisplacementPips);
      
      // Check for significant move after this candle
      bool strong_move_up = false;
      bool strong_move_down = false;
      
      for(int j = i + 1; j < MathMin(i + 5, copied); j++)
      {
         if(lows[j] - highs[i] > PipsToPrice(MinDisplacementPips))
            strong_move_up = true;
         if(highs[i] - highs[j] > PipsToPrice(MinDisplacementPips))
            strong_move_down = true;
      }
      
      // Bearish Order Block (last bullish candle before drop)
      if(closes[i] > opens[i] && body_size >= min_body && strong_move_down)
      {
         ZoneInfo ob;
         ob.type = ZONE_ORDER_BLOCK;
         ob.time_start = times[i];
         ob.time_end = times[i] + PeriodSeconds(LTF_Entry_Period) * 10;
         ob.price_high = highs[i];
         ob.price_low = opens[i];
         ob.is_bullish = false;
         ob.is_tested = false;
         ob.description = "Bearish OB";
         
         ArrayResize(g_orderBlocks, ArraySize(g_orderBlocks) + 1);
         g_orderBlocks[ArraySize(g_orderBlocks) - 1] = ob;
      }
      
      // Bullish Order Block (last bearish candle before rally)
      if(closes[i] < opens[i] && body_size >= min_body && strong_move_up)
      {
         ZoneInfo ob;
         ob.type = ZONE_ORDER_BLOCK;
         ob.time_start = times[i];
         ob.time_end = times[i] + PeriodSeconds(LTF_Entry_Period) * 10;
         ob.price_high = opens[i];
         ob.price_low = lows[i];
         ob.is_bullish = true;
         ob.is_tested = false;
         ob.description = "Bullish OB";
         
         ArrayResize(g_orderBlocks, ArraySize(g_orderBlocks) + 1);
         g_orderBlocks[ArraySize(g_orderBlocks) - 1] = ob;
      }
   }
}

//+------------------------------------------------------------------+
//| Detect Fair Value Gaps                                          |
//+------------------------------------------------------------------+
void DetectFairValueGaps()
{
   double highs[], lows[];
   datetime times[];
   
   ArrayResize(highs, 50);
   ArrayResize(lows, 50);
   ArrayResize(times, 50);
   
   int copied = CopyHigh(_Symbol, LTF_Entry_Period, 1, 50, highs);
   CopyLow(_Symbol, LTF_Entry_Period, 1, 50, lows);
   CopyTime(_Symbol, LTF_Entry_Period, 1, 50, times);
   
   if(copied < 10) return;
   
   // Clear old FVGs
   ArrayResize(g_fvgZones, 0);
   
   // Look for FVG patterns (3 candle pattern)
   for(int i = 1; i < copied - 1; i++)
   {
      // Bullish FVG: Low[i+1] > High[i-1]
      if(lows[i+1] > highs[i-1])
      {
         double gap_size = lows[i+1] - highs[i-1];
         
         if(gap_size >= PipsToPrice(FVG_MinSizePips))
         {
            ZoneInfo fvg;
            fvg.type = ZONE_FVG;
            fvg.time_start = times[i-1];
            fvg.time_end = times[i+1];
            fvg.price_high = lows[i+1];
            fvg.price_low = highs[i-1];
            fvg.is_bullish = true;
            fvg.is_tested = false;
            fvg.description = "Bullish FVG";
            
            ArrayResize(g_fvgZones, ArraySize(g_fvgZones) + 1);
            g_fvgZones[ArraySize(g_fvgZones) - 1] = fvg;
         }
      }
      
      // Bearish FVG: High[i+1] < Low[i-1]
      if(highs[i+1] < lows[i-1])
      {
         double gap_size = lows[i-1] - highs[i+1];
         
         if(gap_size >= PipsToPrice(FVG_MinSizePips))
         {
            ZoneInfo fvg;
            fvg.type = ZONE_FVG;
            fvg.time_start = times[i-1];
            fvg.time_end = times[i+1];
            fvg.price_high = lows[i-1];
            fvg.price_low = highs[i+1];
            fvg.is_bullish = false;
            fvg.is_tested = false;
            fvg.description = "Bearish FVG";
            
            ArrayResize(g_fvgZones, ArraySize(g_fvgZones) + 1);
            g_fvgZones[ArraySize(g_fvgZones) - 1] = fvg;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Check for signal confluence and generate signals                 |
//+------------------------------------------------------------------+
void CheckForSignalConfluence(ENUM_SIGNAL_BIAS htf_bias, bool choch_detected, bool bos_detected)
{
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   // Check order blocks
   for(int i = 0; i < ArraySize(g_orderBlocks); i++)
   {
      if(!g_orderBlocks[i].is_tested && 
         current_price >= g_orderBlocks[i].price_low && 
         current_price <= g_orderBlocks[i].price_high)
      {
         // Check if bias aligns with order block
         if((htf_bias == BIAS_BULLISH && g_orderBlocks[i].is_bullish) ||
            (htf_bias == BIAS_BEARISH && !g_orderBlocks[i].is_bullish))
         {
            if(choch_detected || bos_detected)
            {
               GenerateSignal(g_orderBlocks[i]);
               g_orderBlocks[i].is_tested = true;
            }
         }
      }
   }
   
   // Check FVGs
   for(int i = 0; i < ArraySize(g_fvgZones); i++)
   {
      if(!g_fvgZones[i].is_tested && 
         current_price >= g_fvgZones[i].price_low && 
         current_price <= g_fvgZones[i].price_high)
      {
         // Check if bias aligns with FVG
         if((htf_bias == BIAS_BULLISH && g_fvgZones[i].is_bullish) ||
            (htf_bias == BIAS_BEARISH && !g_fvgZones[i].is_bullish))
         {
            if(choch_detected || bos_detected)
            {
               GenerateSignal(g_fvgZones[i]);
               g_fvgZones[i].is_tested = true;
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Generate trading signal                                          |
//+------------------------------------------------------------------+
void GenerateSignal(const ZoneInfo& zone)
{
   SignalInfo signal;
   signal.signal_time = TimeCurrent();
   signal.symbol = _Symbol;
   signal.bias = zone.is_bullish ? BIAS_BULLISH : BIAS_BEARISH;
   signal.zone_description = zone.description;
   signal.entry_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   // Calculate stop loss and take profit using ATR
   int atr_handle = iATR(_Symbol, LTF_Entry_Period, 14);
   double atr[];
   double stop_distance = 0.0;
   if(CopyBuffer(atr_handle, 0, 0, 1, atr) > 0)
   {
      stop_distance = atr[0] * 1.5;
   }
   else
   {
      stop_distance = 20 * SymbolInfoDouble(_Symbol, SYMBOL_POINT); // fallback
   }
   
   if(zone.is_bullish)
   {
      signal.stop_loss = signal.entry_price - stop_distance;
      signal.take_profit = signal.entry_price + (stop_distance * DefaultRiskReward);
   }
   else
   {
      signal.stop_loss = signal.entry_price + stop_distance;
      signal.take_profit = signal.entry_price - (stop_distance * DefaultRiskReward);
   }
   
   signal.risk_reward = DefaultRiskReward;
   signal.telegram_sent = false;
   
   // Log signal details
   LogSignalDetails(signal);
   
   // Send to Telegram if enabled
   if(EnableTelegramAlerts)
   {
      signal.telegram_sent = SendTelegramSignal(signal);
   }
   
   // Store last signal
   g_lastSignal = signal;
}

//+------------------------------------------------------------------+
//| Update visual elements on chart                                  |
//+------------------------------------------------------------------+
void UpdateVisualElements()
{
   // Draw order blocks
   for(int i = 0; i < ArraySize(g_orderBlocks); i++)
   {
      string obj_name = PREFIX_OB + IntegerToString(i);
      color zone_color = g_orderBlocks[i].is_bullish ? BullishOB_Color : BearishOB_Color;
      
      DrawZone(obj_name, 
               g_orderBlocks[i].time_start,
               g_orderBlocks[i].time_end,
               g_orderBlocks[i].price_high,
               g_orderBlocks[i].price_low,
               zone_color);
   }
   
   // Draw FVGs
   for(int i = 0; i < ArraySize(g_fvgZones); i++)
   {
      string obj_name = PREFIX_FVG + IntegerToString(i);
      color zone_color = g_fvgZones[i].is_bullish ? FVG_Bull_Color : FVG_Bear_Color;
      
      DrawZone(obj_name,
               g_fvgZones[i].time_start,
               g_fvgZones[i].time_end,
               g_fvgZones[i].price_high,
               g_fvgZones[i].price_low,
               zone_color);
   }
   
   // Draw equilibrium line
   double high = iHigh(_Symbol, PERIOD_CURRENT, iHighest(_Symbol, PERIOD_CURRENT, MODE_HIGH, 20, 0));
   double low = iLow(_Symbol, PERIOD_CURRENT, iLowest(_Symbol, PERIOD_CURRENT, MODE_LOW, 20, 0));
   double equilibrium = low + (high - low) * (EquilibriumLevel / 100.0);
   
   string obj_name = PREFIX_EQUI + "Current";
   DrawEquilibriumLine(obj_name, equilibrium);
}

//+------------------------------------------------------------------+
//| Draw zone on chart                                               |
//+------------------------------------------------------------------+
void DrawZone(string name, datetime time1, datetime time2, double price1, double price2, color clr)
{
   ObjectCreate(0, name, OBJ_RECTANGLE, 0, time1, price1, time2, price2);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, name, OBJPROP_FILL, true);
   ObjectSetInteger(0, name, OBJPROP_BACK, true);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
   ObjectSetInteger(0, name, OBJPROP_ZORDER, 0);
}

//+------------------------------------------------------------------+
//| Draw CHOCH marker                                                |
//+------------------------------------------------------------------+
void DrawCHOCHMarker(datetime time, double price, bool is_bullish)
{
   string obj_name = PREFIX_CHOCH + TimeToString(time);
   
   ObjectCreate(0, obj_name, OBJ_ARROW, 0, time, price);
   ObjectSetInteger(0, obj_name, OBJPROP_ARROWCODE, is_bullish ? 241 : 242);
   ObjectSetInteger(0, obj_name, OBJPROP_COLOR, CHOCH_Color);
   ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, 2);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, obj_name, OBJPROP_HIDDEN, true);
   ObjectSetInteger(0, obj_name, OBJPROP_ZORDER, 0);
}

//+------------------------------------------------------------------+
//| Draw BOS marker                                                  |
//+------------------------------------------------------------------+
void DrawBOSMarker(datetime time, double price, bool is_bullish)
{
   string obj_name = PREFIX_BOS + TimeToString(time);
   
   ObjectCreate(0, obj_name, OBJ_ARROW, 0, time, price);
   ObjectSetInteger(0, obj_name, OBJPROP_ARROWCODE, is_bullish ? 241 : 242);
   ObjectSetInteger(0, obj_name, OBJPROP_COLOR, BOS_Color);
   ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, 2);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, obj_name, OBJPROP_HIDDEN, true);
   ObjectSetInteger(0, obj_name, OBJPROP_ZORDER, 0);
}

//+------------------------------------------------------------------+
//| Draw equilibrium line                                            |
//+------------------------------------------------------------------+
void DrawEquilibriumLine(string name, double price)
{
   ObjectCreate(0, name, OBJ_HLINE, 0, 0, price);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clrGray);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DASH);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
   ObjectSetInteger(0, name, OBJPROP_ZORDER, 0);
} 