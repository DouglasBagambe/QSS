//+------------------------------------------------------------------+
//|                                                QSS_Indicator.mq5 |
//|                        Copyright 2025, Quantum SmartFlow Systems |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantum SmartFlow Systems"
#property link      ""
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
datetime g_lastUpdateTime = 0;
int g_updateInterval = 300; // 5 minutes

//+------------------------------------------------------------------+
//| Prefix constants for object names                                 |
//+------------------------------------------------------------------+
#define PREFIX_EW "EW_"        // Elliott Wave
#define PREFIX_HARMONIC "HARM_" // Harmonic Patterns
#define PREFIX_DIV "DIV_"      // Divergences
#define PREFIX_MP "MP_"        // Market Profile
#define PREFIX_OF "OF_"        // Order Flow
#define PREFIX_PATTERN "PAT_"  // Chart Patterns
#define PREFIX_IND "IND_"      // Indicators
#define PREFIX_FIB "FIB_"      // Fibonacci
#define PREFIX_PIVOT "PIV_"    // Pivot Points
#define PREFIX_CLOUD "CLD_"    // Ichimoku Cloud
#define PREFIX_MS "MS_"        // Market Structure
#define PREFIX_VP "VP_"        // Volume Profile

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
   
   // Send periodic market updates
   if(TimeCurrent() - g_lastUpdateTime >= g_updateInterval)
   {
      SendMarketUpdate();
      g_lastUpdateTime = TimeCurrent();
   }
   
   // Draw advanced patterns
   if(DrawVisuals)
   {
      DrawElliottWaves();
      DrawHarmonicPatterns();
      DrawDivergences();
      DrawVolumeProfile();
      DrawMarketProfile();
      DrawOrderFlow();
      DrawAdvancedPatterns();
      DrawMarketStructure();
      DrawTechnicalIndicators();
      DrawFibonacciLevels();
      DrawPivotPoints();
      DrawIchimokuCloud();
      DrawBollingerBands();
      DrawRSI();
      DrawMACD();
      DrawStochastic();
      DrawADX();
      DrawATR();
      DrawOBV();
      DrawMFI();
   }
   
   return rates_total;
}

//+------------------------------------------------------------------+
//| Send market update to Telegram                                   |
//+------------------------------------------------------------------+
void SendMarketUpdate()
{
   if(!EnableTelegramAlerts) return;
   
   string update = "";
   
   // Market Structure
   ENUM_SIGNAL_BIAS htf_bias = DetermineHTFBias();
   bool choch_detected = DetectCHOCH();
   bool bos_detected = DetectBOS();
   
   update += "📊 <b>Market Structure Update</b>\\n";
   update += "• Bias: " + BiasToString(htf_bias) + "\\n";
   if(choch_detected) update += "• CHOCH Detected\\n";
   if(bos_detected) update += "• BOS Detected\\n";
   
   // Add market structure analysis
   update += "• Market Structure: ";
   if(IsInUptrend())
      update += "Uptrend\\n";
   else if(IsInDowntrend())
      update += "Downtrend\\n";
   else
      update += "Sideways\\n";
   
   // Add key levels
   double key_levels[];
   GetKeyLevels(key_levels);
   if(ArraySize(key_levels) > 0)
   {
      update += "• Key Levels:\\n";
      for(int i = 0; i < ArraySize(key_levels); i++)
      {
         update += "  - " + DoubleToString(key_levels[i], _Digits) + "\\n";
      }
   }
   
   update += "\\n";
   
   // Active Zones
   update += "🎯 <b>Active Zones</b>\\n";
   for(int i = 0; i < ArraySize(g_orderBlocks); i++)
   {
      if(!g_orderBlocks[i].is_tested)
      {
         update += "• " + g_orderBlocks[i].description + "\\n";
         update += "  Range: " + DoubleToString(g_orderBlocks[i].price_low, _Digits) + 
                  " - " + DoubleToString(g_orderBlocks[i].price_high, _Digits) + "\\n";
      }
   }
   for(int i = 0; i < ArraySize(g_fvgZones); i++)
   {
      if(!g_fvgZones[i].is_tested)
      {
         update += "• " + g_fvgZones[i].description + "\\n";
         update += "  Range: " + DoubleToString(g_fvgZones[i].price_low, _Digits) + 
                  " - " + DoubleToString(g_fvgZones[i].price_high, _Digits) + "\\n";
      }
   }
   update += "\\n";
   
   // Recent Price Action
   update += "📈 <b>Recent Price Action</b>\\n";
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double prev_price = iClose(_Symbol, PERIOD_CURRENT, 1);
   double price_change = ((current_price - prev_price) / prev_price) * 100;
   
   update += "• Current Price: " + DoubleToString(current_price, _Digits) + "\\n";
   update += "• Change: " + DoubleToString(price_change, 2) + "%\\n";
   update += "• Volume: " + DoubleToString(tick_volume[0], 0) + "\\n";
   
   // Add price action patterns
   string patterns = GetRecentPriceAction();
   if(StringLen(patterns) > 0)
   {
      update += "• Patterns:\\n" + patterns;
   }
   
   update += "\\n";
   
   // Technical Indicators
   update += "📊 <b>Technical Indicators</b>\\n";
   update += GetTechnicalIndicators();
   
   // Advanced Pattern Recognition
   update += "\\n";
   update += GetAdvancedPatterns();
   
   // Send update
   SendMarketUpdate(update);
}

//+------------------------------------------------------------------+
//| Check if market is in uptrend                                    |
//+------------------------------------------------------------------+
bool IsInUptrend()
{
   double ma20_handle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
   double ma50_handle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_SMA, PRICE_CLOSE);
   double ma200_handle = iMA(_Symbol, PERIOD_CURRENT, 200, 0, MODE_SMA, PRICE_CLOSE);
   
   double ma20[], ma50[], ma200[];
   if(CopyBuffer(ma20_handle, 0, 0, 1, ma20) > 0 && 
      CopyBuffer(ma50_handle, 0, 0, 1, ma50) > 0 &&
      CopyBuffer(ma200_handle, 0, 0, 1, ma200) > 0)
   {
      double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      return (current_price > ma20[0] && ma20[0] > ma50[0] && ma50[0] > ma200[0]);
   }
   return false;
}

//+------------------------------------------------------------------+
//| Check if market is in downtrend                                  |
//+------------------------------------------------------------------+
bool IsInDowntrend()
{
   double ma20_handle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
   double ma50_handle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_SMA, PRICE_CLOSE);
   double ma200_handle = iMA(_Symbol, PERIOD_CURRENT, 200, 0, MODE_SMA, PRICE_CLOSE);
   
   double ma20[], ma50[], ma200[];
   if(CopyBuffer(ma20_handle, 0, 0, 1, ma20) > 0 && 
      CopyBuffer(ma50_handle, 0, 0, 1, ma50) > 0 &&
      CopyBuffer(ma200_handle, 0, 0, 1, ma200) > 0)
   {
      double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      return (current_price < ma20[0] && ma20[0] < ma50[0] && ma50[0] < ma200[0]);
   }
   return false;
}

//+------------------------------------------------------------------+
//| Get key price levels                                             |
//+------------------------------------------------------------------+
void GetKeyLevels(double &levels[])
{
   ArrayResize(levels, 0);
   
   // Get recent highs and lows
   double highs[], lows[];
   ArrayResize(highs, 20);
   ArrayResize(lows, 20);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 20, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 20, lows);
   
   // Find swing highs and lows
   for(int i = 2; i < 18; i++)
   {
      // Swing high
      if(highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
         highs[i] > highs[i+1] && highs[i] > highs[i+2])
      {
         ArrayResize(levels, ArraySize(levels) + 1);
         levels[ArraySize(levels) - 1] = highs[i];
      }
      
      // Swing low
      if(lows[i] < lows[i-1] && lows[i] < lows[i-2] &&
         lows[i] < lows[i+1] && lows[i] < lows[i+2])
      {
         ArrayResize(levels, ArraySize(levels) + 1);
         levels[ArraySize(levels) - 1] = lows[i];
      }
   }
   
   // Sort levels
   ArraySort(levels);
   
   // Remove duplicates and levels too close to each other
   double min_distance = _Point * 50; // Minimum distance between levels
   for(int i = 0; i < ArraySize(levels) - 1; i++)
   {
      if(MathAbs(levels[i] - levels[i+1]) < min_distance)
      {
         for(int j = i + 1; j < ArraySize(levels) - 1; j++)
         {
            levels[j] = levels[j+1];
         }
         ArrayResize(levels, ArraySize(levels) - 1);
         i--;
      }
   }
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

//+------------------------------------------------------------------+
//| Draw Elliott Waves                                               |
//+------------------------------------------------------------------+
void DrawElliottWaves()
{
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   
   // Find wave points
   int wave_points[];
   ArrayResize(wave_points, 0);
   
   for(int i = 2; i < ArraySize(highs) - 2; i++)
   {
      // Wave 1
      if(highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
         highs[i] > highs[i+1] && highs[i] > highs[i+2])
      {
         ArrayResize(wave_points, ArraySize(wave_points) + 1);
         wave_points[ArraySize(wave_points) - 1] = i;
      }
      
      // Wave 2
      if(lows[i] < lows[i-1] && lows[i] < lows[i-2] &&
         lows[i] < lows[i+1] && lows[i] < lows[i+2])
      {
         ArrayResize(wave_points, ArraySize(wave_points) + 1);
         wave_points[ArraySize(wave_points) - 1] = i;
      }
   }
   
   // Draw waves
   for(int i = 0; i < ArraySize(wave_points) - 1; i++)
   {
      string name = PREFIX_EW + IntegerToString(i);
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(highs) - wave_points[i]) * PeriodSeconds(PERIOD_CURRENT),
                  highs[wave_points[i]],
                  TimeCurrent() - (ArraySize(highs) - wave_points[i+1]) * PeriodSeconds(PERIOD_CURRENT),
                  highs[wave_points[i+1]]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrBlue);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   }
}

//+------------------------------------------------------------------+
//| Draw harmonic patterns                                           |
//+------------------------------------------------------------------+
void DrawHarmonicPatterns()
{
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   
   // Find pattern points
   int pattern_points[];
   ArrayResize(pattern_points, 0);
   
   // Look for Gartley pattern
   if(IsGartleyPattern(highs, lows))
   {
      // Draw pattern
      string name = PREFIX_HARMONIC + "Gartley";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(highs) - pattern_points[0]) * PeriodSeconds(PERIOD_CURRENT),
                  highs[pattern_points[0]],
                  TimeCurrent() - (ArraySize(highs) - pattern_points[1]) * PeriodSeconds(PERIOD_CURRENT),
                  highs[pattern_points[1]]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrGreen);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   }
}

//+------------------------------------------------------------------+
//| Draw divergences                                                 |
//+------------------------------------------------------------------+
void DrawDivergences()
{
   // RSI Divergence
   int rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   double rsi[];
   if(CopyBuffer(rsi_handle, 0, 0, 20, rsi) > 0)
   {
      // Find divergence points
      int div_points[];
      ArrayResize(div_points, 0);
      
      for(int i = 1; i < ArraySize(rsi) - 1; i++)
      {
         if(rsi[i] > rsi[i-1] && rsi[i] > rsi[i+1])
         {
            ArrayResize(div_points, ArraySize(div_points) + 1);
            div_points[ArraySize(div_points) - 1] = i;
         }
      }
      
      // Draw divergences
      for(int i = 0; i < ArraySize(div_points) - 1; i++)
      {
         string name = PREFIX_DIV + IntegerToString(i);
         ObjectCreate(0, name, OBJ_TREND, 0, 
                     TimeCurrent() - (ArraySize(rsi) - div_points[i]) * PeriodSeconds(PERIOD_CURRENT),
                     rsi[div_points[i]],
                     TimeCurrent() - (ArraySize(rsi) - div_points[i+1]) * PeriodSeconds(PERIOD_CURRENT),
                     rsi[div_points[i+1]]);
         
         ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
         ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DOT);
         ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      }
   }
}

//+------------------------------------------------------------------+
//| Draw market profile                                              |
//+------------------------------------------------------------------+
void DrawMarketProfile()
{
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
   
   // Draw value area
   string name = PREFIX_MP + "ValueArea";
   ObjectCreate(0, name, OBJ_RECTANGLE, 0, 
               TimeCurrent() - 50 * PeriodSeconds(PERIOD_CURRENT),
               value_area_high,
               TimeCurrent(),
               value_area_low);
   
   ObjectSetInteger(0, name, OBJPROP_COLOR, clrBlue);
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
//| Draw order flow                                                  |
//+------------------------------------------------------------------+
void DrawOrderFlow()
{
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
   
   // Draw volume bars
   for(int i = 0; i < ArraySize(volumes); i++)
   {
      string name = PREFIX_OF + IntegerToString(i);
      color bar_color = (closes[i] > opens[i]) ? clrGreen : clrRed;
      
      ObjectCreate(0, name, OBJ_RECTANGLE, 0, 
                  TimeCurrent() - (ArraySize(volumes) - i) * PeriodSeconds(PERIOD_CURRENT),
                  closes[i],
                  TimeCurrent() - (ArraySize(volumes) - i - 1) * PeriodSeconds(PERIOD_CURRENT),
                  opens[i]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, bar_color);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, name, OBJPROP_FILL, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_SELECTED, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, name, OBJPROP_ZORDER, 0);
   }
}

//+------------------------------------------------------------------+
//| Draw advanced patterns                                           |
//+------------------------------------------------------------------+
void DrawAdvancedPatterns()
{
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
   
   // Draw double top/bottom
   if(IsDoubleTop(highs, lows))
   {
      string name = PREFIX_PATTERN + "DoubleTop";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(highs) - 20) * PeriodSeconds(PERIOD_CURRENT),
                  highs[20],
                  TimeCurrent() - (ArraySize(highs) - 40) * PeriodSeconds(PERIOD_CURRENT),
                  highs[40]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   }
   
   // Draw head and shoulders
   if(IsHeadAndShoulders(highs, lows))
   {
      string name = PREFIX_PATTERN + "HeadAndShoulders";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(highs) - 20) * PeriodSeconds(PERIOD_CURRENT),
                  highs[20],
                  TimeCurrent() - (ArraySize(highs) - 40) * PeriodSeconds(PERIOD_CURRENT),
                  highs[40]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   }
   
   // Draw triangles
   if(IsAscendingTriangle(highs, lows))
   {
      string name = PREFIX_PATTERN + "AscendingTriangle";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(highs) - 20) * PeriodSeconds(PERIOD_CURRENT),
                  highs[20],
                  TimeCurrent() - (ArraySize(highs) - 40) * PeriodSeconds(PERIOD_CURRENT),
                  highs[40]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrBlue);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   }
}

//+------------------------------------------------------------------+
//| Draw market structure                                            |
//+------------------------------------------------------------------+
void DrawMarketStructure()
{
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 50);
   ArrayResize(lows, 50);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 50, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 50, lows);
   
   // Draw higher highs and higher lows
   bool higher_highs = true;
   bool higher_lows = true;
   
   for(int i = 1; i < ArraySize(highs); i++)
   {
      if(highs[i] <= highs[i-1]) higher_highs = false;
      if(lows[i] <= lows[i-1]) higher_lows = false;
   }
   
   if(higher_highs && higher_lows)
   {
      string name = PREFIX_MS + "Uptrend";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - 50 * PeriodSeconds(PERIOD_CURRENT),
                  lows[0],
                  TimeCurrent(),
                  highs[ArraySize(highs)-1]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrGreen);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   }
   
   // Draw lower highs and lower lows
   bool lower_highs = true;
   bool lower_lows = true;
   
   for(int i = 1; i < ArraySize(highs); i++)
   {
      if(highs[i] >= highs[i-1]) lower_highs = false;
      if(lows[i] >= lows[i-1]) lower_lows = false;
   }
   
   if(lower_highs && lower_lows)
   {
      string name = PREFIX_MS + "Downtrend";
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - 50 * PeriodSeconds(PERIOD_CURRENT),
                  highs[0],
                  TimeCurrent(),
                  lows[ArraySize(lows)-1]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   }
}

//+------------------------------------------------------------------+
//| Draw technical indicators                                        |
//+------------------------------------------------------------------+
void DrawTechnicalIndicators()
{
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
   
   // Calculate indicators
   double rsi[], macd[], signal[], histogram[];
   double stoch_k[], stoch_d[];
   double adx[], di_plus[], di_minus[];
   double atr[];
   double obv[];
   double mfi[];
   
   ArrayResize(rsi, 100);
   ArrayResize(macd, 100);
   ArrayResize(signal, 100);
   ArrayResize(histogram, 100);
   ArrayResize(stoch_k, 100);
   ArrayResize(stoch_d, 100);
   ArrayResize(adx, 100);
   ArrayResize(di_plus, 100);
   ArrayResize(di_minus, 100);
   ArrayResize(atr, 100);
   ArrayResize(obv, 100);
   ArrayResize(mfi, 100);
   
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
   
   // Calculate MACD
   double ema12[], ema26[];
   ArrayResize(ema12, 100);
   ArrayResize(ema26, 100);
   
   for(int i = 0; i < ArraySize(ema12); i++)
   {
      ema12[i] = iMA(_Symbol, PERIOD_CURRENT, 12, 0, MODE_EMA, PRICE_CLOSE);
      ema26[i] = iMA(_Symbol, PERIOD_CURRENT, 26, 0, MODE_EMA, PRICE_CLOSE);
      macd[i] = ema12[i] - ema26[i];
      signal[i] = iMA(_Symbol, PERIOD_CURRENT, 9, 0, MODE_EMA, PRICE_CLOSE);
      histogram[i] = macd[i] - signal[i];
   }
   
   // Calculate Stochastic
   for(int i = 0; i < ArraySize(stoch_k); i++)
   {
      double highest_high = highs[ArrayMaximum(highs, i, 14)];
      double lowest_low = lows[ArrayMinimum(lows, i, 14)];
      stoch_k[i] = 100 * (closes[i] - lowest_low) / (highest_high - lowest_low);
      stoch_d[i] = iMA(_Symbol, PERIOD_CURRENT, 3, 0, MODE_SMA, PRICE_CLOSE);
   }
   
   // Calculate ADX
   for(int i = 0; i < ArraySize(adx); i++)
   {
      double tr = MathMax(highs[i] - lows[i], MathMax(MathAbs(highs[i] - closes[i-1]), MathAbs(lows[i] - closes[i-1])));
      double plus_dm = highs[i] - highs[i-1];
      double minus_dm = lows[i-1] - lows[i];
      
      if(plus_dm < 0) plus_dm = 0;
      if(minus_dm < 0) minus_dm = 0;
      if(plus_dm < minus_dm) plus_dm = 0;
      if(minus_dm < plus_dm) minus_dm = 0;
      
      di_plus[i] = 100 * iMA(_Symbol, PERIOD_CURRENT, 14, 0, MODE_EMA, PRICE_CLOSE);
      di_minus[i] = 100 * iMA(_Symbol, PERIOD_CURRENT, 14, 0, MODE_EMA, PRICE_CLOSE);
      adx[i] = 100 * MathAbs(di_plus[i] - di_minus[i]) / (di_plus[i] + di_minus[i]);
   }
   
   // Calculate ATR
   for(int i = 0; i < ArraySize(atr); i++)
   {
      double tr = MathMax(highs[i] - lows[i], MathMax(MathAbs(highs[i] - closes[i-1]), MathAbs(lows[i] - closes[i-1])));
      atr[i] = iMA(_Symbol, PERIOD_CURRENT, 14, 0, MODE_SMA, PRICE_CLOSE);
   }
   
   // Calculate OBV
   obv[0] = (double)tick_volume[0];
   for(int i = 1; i < ArraySize(obv); i++)
   {
      if(closes[i] > closes[i-1])
         obv[i] = obv[i-1] + (double)tick_volume[i];
      else if(closes[i] < closes[i-1])
         obv[i] = obv[i-1] - (double)tick_volume[i];
      else
         obv[i] = obv[i-1];
   }
   
   // Calculate MFI
   for(int i = 0; i < ArraySize(mfi); i++)
   {
      double typical_price = (highs[i] + lows[i] + closes[i]) / 3;
      double money_flow = typical_price * (double)tick_volume[i];
      
      double positive_flow = 0, negative_flow = 0;
      for(int j = i; j < i + 14 && j < ArraySize(closes); j++)
      {
         if(typical_price > (highs[j-1] + lows[j-1] + closes[j-1]) / 3)
            positive_flow += money_flow;
         else
            negative_flow += money_flow;
      }
      
      mfi[i] = 100 - (100 / (1 + positive_flow/negative_flow));
   }
   
   // Draw indicators
   DrawIndicator("RSI", rsi, clrRed);
   DrawIndicator("MACD", macd, clrBlue);
   DrawIndicator("Signal", signal, clrOrange);
   DrawIndicator("Histogram", histogram, clrGreen);
   DrawIndicator("Stoch_K", stoch_k, clrBlue);
   DrawIndicator("Stoch_D", stoch_d, clrRed);
   DrawIndicator("ADX", adx, clrPurple);
   DrawIndicator("DI+", di_plus, clrGreen);
   DrawIndicator("DI-", di_minus, clrRed);
   DrawIndicator("ATR", atr, clrOrange);
   DrawIndicator("OBV", obv, clrBlue);
   DrawIndicator("MFI", mfi, clrPurple);
}

//+------------------------------------------------------------------+
//| Draw indicator                                                    |
//+------------------------------------------------------------------+
void DrawIndicator(string name, double &values[], color clr)
{
   for(int i = 0; i < ArraySize(values); i++)
   {
      string obj_name = PREFIX_IND + name + IntegerToString(i);
      ObjectCreate(0, obj_name, OBJ_TREND, 0, 
                  TimeCurrent() - (ArraySize(values) - i) * PeriodSeconds(PERIOD_CURRENT),
                  values[i],
                  TimeCurrent() - (ArraySize(values) - i - 1) * PeriodSeconds(PERIOD_CURRENT),
                  values[i+1]);
      
      ObjectSetInteger(0, obj_name, OBJPROP_COLOR, clr);
      ObjectSetInteger(0, obj_name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, 1);
   }
}

//+------------------------------------------------------------------+
//| Draw Fibonacci levels                                             |
//+------------------------------------------------------------------+
void DrawFibonacciLevels()
{
   // Get price data
   double highs[], lows[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   
   double highest_high = highs[ArrayMaximum(highs, 0, ArraySize(highs))];
   double lowest_low = lows[ArrayMinimum(lows, 0, ArraySize(lows))];
   double range = highest_high - lowest_low;
   
   // Draw Fibonacci levels
   double levels[] = {0, 0.236, 0.382, 0.5, 0.618, 0.786, 1};
   color colors[] = {clrRed, clrOrange, clrYellow, clrGreen, clrBlue, clrPurple, clrRed};
   
   for(int i = 0; i < ArraySize(levels); i++)
   {
      string name = PREFIX_FIB + DoubleToString(levels[i], 3);
      double level = lowest_low + range * levels[i];
      
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - 100 * PeriodSeconds(PERIOD_CURRENT),
                  level,
                  TimeCurrent(),
                  level);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, colors[i]);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   }
}

//+------------------------------------------------------------------+
//| Draw pivot points                                                 |
//+------------------------------------------------------------------+
void DrawPivotPoints()
{
   // Get price data
   double opens[], highs[], lows[], closes[];
   ArrayResize(opens, 1);
   ArrayResize(highs, 1);
   ArrayResize(lows, 1);
   ArrayResize(closes, 1);
   
   CopyOpen(_Symbol, PERIOD_CURRENT, 1, 1, opens);
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 1, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 1, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 1, closes);
   
   // Calculate pivot points
   double pp = (highs[0] + lows[0] + closes[0]) / 3;
   double r1 = 2 * pp - lows[0];
   double s1 = 2 * pp - highs[0];
   double r2 = pp + (highs[0] - lows[0]);
   double s2 = pp - (highs[0] - lows[0]);
   double r3 = highs[0] + 2 * (pp - lows[0]);
   double s3 = lows[0] - 2 * (highs[0] - pp);
   
   // Draw pivot points
   double levels[] = {s3, s2, s1, pp, r1, r2, r3};
   string names[] = {"S3", "S2", "S1", "PP", "R1", "R2", "R3"};
   color colors[] = {clrRed, clrOrange, clrYellow, clrGreen, clrBlue, clrPurple, clrRed};
   
   for(int i = 0; i < ArraySize(levels); i++)
   {
      string name = PREFIX_PIVOT + names[i];
      ObjectCreate(0, name, OBJ_TREND, 0, 
                  TimeCurrent() - PeriodSeconds(PERIOD_CURRENT),
                  levels[i],
                  TimeCurrent(),
                  levels[i]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, colors[i]);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
   }
}

//+------------------------------------------------------------------+
//| Draw Ichimoku Cloud                                              |
//+------------------------------------------------------------------+
void DrawIchimokuCloud()
{
   // Get price data
   double highs[], lows[], closes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate Ichimoku components
   double tenkan_sen[], kijun_sen[], senkou_span_a[], senkou_span_b[];
   ArrayResize(tenkan_sen, 100);
   ArrayResize(kijun_sen, 100);
   ArrayResize(senkou_span_a, 100);
   ArrayResize(senkou_span_b, 100);
   
   for(int i = 0; i < ArraySize(tenkan_sen); i++)
   {
      // Tenkan-sen (Conversion Line)
      double highest_high = highs[ArrayMaximum(highs, i, 9)];
      double lowest_low = lows[ArrayMinimum(lows, i, 9)];
      tenkan_sen[i] = (highest_high + lowest_low) / 2;
      
      // Kijun-sen (Base Line)
      highest_high = highs[ArrayMaximum(highs, i, 26)];
      lowest_low = lows[ArrayMinimum(lows, i, 26)];
      kijun_sen[i] = (highest_high + lowest_low) / 2;
      
      // Senkou Span A (Leading Span A)
      senkou_span_a[i] = (tenkan_sen[i] + kijun_sen[i]) / 2;
      
      // Senkou Span B (Leading Span B)
      highest_high = highs[ArrayMaximum(highs, i, 52)];
      lowest_low = lows[ArrayMinimum(lows, i, 52)];
      senkou_span_b[i] = (highest_high + lowest_low) / 2;
   }
   
   // Draw Ichimoku components
   DrawIndicator("Tenkan", tenkan_sen, clrRed);
   DrawIndicator("Kijun", kijun_sen, clrBlue);
   DrawIndicator("SpanA", senkou_span_a, clrGreen);
   DrawIndicator("SpanB", senkou_span_b, clrOrange);
   
   // Draw cloud
   for(int i = 0; i < ArraySize(senkou_span_a); i++)
   {
      string name = PREFIX_CLOUD + IntegerToString(i);
      color cloud_color = (senkou_span_a[i] > senkou_span_b[i]) ? clrGreen : clrRed;
      
      ObjectCreate(0, name, OBJ_RECTANGLE, 0, 
                  TimeCurrent() - (ArraySize(senkou_span_a) - i) * PeriodSeconds(PERIOD_CURRENT),
                  senkou_span_a[i],
                  TimeCurrent() - (ArraySize(senkou_span_a) - i - 1) * PeriodSeconds(PERIOD_CURRENT),
                  senkou_span_b[i]);
      
      ObjectSetInteger(0, name, OBJPROP_COLOR, cloud_color);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, name, OBJPROP_FILL, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
   }
}

//+------------------------------------------------------------------+
//| Draw Bollinger Bands                                             |
//+------------------------------------------------------------------+
void DrawBollingerBands()
{
   // Get price data
   double closes[];
   ArrayResize(closes, 100);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate Bollinger Bands
   double middle_band[], upper_band[], lower_band[];
   ArrayResize(middle_band, 100);
   ArrayResize(upper_band, 100);
   ArrayResize(lower_band, 100);
   
   for(int i = 0; i < ArraySize(middle_band); i++)
   {
      middle_band[i] = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE, i);
      
      double sum = 0;
      for(int j = i; j < i + 20 && j < ArraySize(closes); j++)
         sum += MathPow(closes[j] - middle_band[i], 2);
      
      double std_dev = MathSqrt(sum / 20);
      upper_band[i] = middle_band[i] + 2 * std_dev;
      lower_band[i] = middle_band[i] - 2 * std_dev;
   }
   
   // Draw Bollinger Bands
   DrawIndicator("Middle", middle_band, clrBlue);
   DrawIndicator("Upper", upper_band, clrRed);
   DrawIndicator("Lower", lower_band, clrGreen);
}

//+------------------------------------------------------------------+
//| Draw RSI                                                        |
//+------------------------------------------------------------------+
void DrawRSI()
{
   // Get price data
   double closes[];
   ArrayResize(closes, 100);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate RSI
   double rsi[];
   ArrayResize(rsi, 100);
   
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
   
   // Draw RSI
   DrawIndicator("RSI", rsi, clrRed);
}

//+------------------------------------------------------------------+
//| Draw MACD                                                        |
//+------------------------------------------------------------------+
void DrawMACD()
{
   // Get price data
   double closes[];
   ArrayResize(closes, 100);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate MACD
   double macd[], signal[];
   ArrayResize(macd, 100);
   ArrayResize(signal, 100);
   
   for(int i = 0; i < ArraySize(macd); i++)
   {
      double ema12 = iMA(_Symbol, PERIOD_CURRENT, 12, 0, MODE_EMA, PRICE_CLOSE, i);
      double ema26 = iMA(_Symbol, PERIOD_CURRENT, 26, 0, MODE_EMA, PRICE_CLOSE, i);
      macd[i] = ema12 - ema26;
   }
   
   for(int i = 0; i < ArraySize(signal); i++)
   {
      double ema9 = iMA(_Symbol, PERIOD_CURRENT, 9, 0, MODE_EMA, PRICE_CLOSE, i);
      signal[i] = ema9;
   }
   
   // Draw MACD
   DrawIndicator("MACD", macd, clrBlue);
   DrawIndicator("Signal", signal, clrOrange);
}

//+------------------------------------------------------------------+
//| Draw Stochastic                                                 |
//+------------------------------------------------------------------+
void DrawStochastic()
{
   // Get price data
   double highs[], lows[], closes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate Stochastic
   double stoch_k[], stoch_d[];
   ArrayResize(stoch_k, 100);
   ArrayResize(stoch_d, 100);
   
   for(int i = 0; i < ArraySize(stoch_k); i++)
   {
      double highest_high = highs[ArrayMaximum(highs, i, 14)];
      double lowest_low = lows[ArrayMinimum(lows, i, 14)];
      stoch_k[i] = 100 * (closes[i] - lowest_low) / (highest_high - lowest_low);
   }
   
   for(int i = 0; i < ArraySize(stoch_d); i++)
   {
      double ema3 = iMA(_Symbol, PERIOD_CURRENT, 3, 0, MODE_EMA, PRICE_CLOSE, i);
      stoch_d[i] = iMAOnArray(stoch_k, 0, 3, 0, MODE_SMA, i);
   }
   
   // Draw Stochastic
   DrawIndicator("Stoch_K", stoch_k, clrBlue);
   DrawIndicator("Stoch_D", stoch_d, clrRed);
}

//+------------------------------------------------------------------+
//| Draw ADX                                                          |
//+------------------------------------------------------------------+
void DrawADX()
{
   // Get price data
   double highs[], lows[], closes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate ADX
   double adx[];
   ArrayResize(adx, 100);
   
   for(int i = 0; i < ArraySize(adx); i++)
   {
      double tr = MathMax(highs[i] - lows[i], MathMax(MathAbs(highs[i] - closes[i-1]), MathAbs(lows[i] - closes[i-1])));
      double plus_dm = highs[i] - highs[i-1];
      double minus_dm = lows[i-1] - lows[i];
      
      if(plus_dm < 0) plus_dm = 0;
      if(minus_dm < 0) minus_dm = 0;
      if(plus_dm < minus_dm) plus_dm = 0;
      if(minus_dm < plus_dm) minus_dm = 0;
      
      double di_plus = 100 * iMAOnArray(&plus_dm, 0, 14, 0, MODE_EMA, i) / iMAOnArray(&tr, 0, 14, 0, MODE_EMA, i);
      double di_minus = 100 * iMAOnArray(&minus_dm, 0, 14, 0, MODE_EMA, i) / iMAOnArray(&tr, 0, 14, 0, MODE_EMA, i);
      double sum = di_plus + di_minus;
      adx[i] = 100 * MathAbs(di_plus - di_minus) / sum;
   }
   
   // Draw ADX
   DrawIndicator("ADX", adx, clrPurple);
}

//+------------------------------------------------------------------+
//| Draw ATR                                                          |
//+------------------------------------------------------------------+
void DrawATR()
{
   // Get price data
   double highs[], lows[], closes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   
   // Calculate ATR
   double atr[];
   ArrayResize(atr, 100);
   
   for(int i = 0; i < ArraySize(atr); i++)
   {
      double tr = MathMax(highs[i] - lows[i], MathMax(MathAbs(highs[i] - closes[i-1]), MathAbs(lows[i] - closes[i-1])));
      atr[i] = iMAOnArray(&tr, 0, 14, 0, MODE_SMA, i);
   }
   
   // Draw ATR
   DrawIndicator("ATR", atr, clrOrange);
}

//+------------------------------------------------------------------+
//| Draw OBV                                                          |
//+------------------------------------------------------------------+
void DrawOBV()
{
   // Get price data
   double closes[], volumes[];
   ArrayResize(closes, 100);
   ArrayResize(volumes, 100);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 100, volumes);
   
   // Calculate OBV
   double obv[];
   ArrayResize(obv, 100);
   
   obv[0] = volumes[0];
   for(int i = 1; i < ArraySize(obv); i++)
   {
      if(closes[i] > closes[i-1])
         obv[i] = obv[i-1] + volumes[i];
      else if(closes[i] < closes[i-1])
         obv[i] = obv[i-1] - volumes[i];
      else
         obv[i] = obv[i-1];
   }
   
   // Draw OBV
   DrawIndicator("OBV", obv, clrBlue);
}

//+------------------------------------------------------------------+
//| Draw MFI                                                          |
//+------------------------------------------------------------------+
void DrawMFI()
{
   // Get price data
   double highs[], lows[], closes[], volumes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   ArrayResize(volumes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 100, volumes);
   
   // Calculate MFI
   double mfi[];
   ArrayResize(mfi, 100);
   
   for(int i = 0; i < ArraySize(mfi); i++)
   {
      double typical_price = (highs[i] + lows[i] + closes[i]) / 3;
      double money_flow = typical_price * volumes[i];
      
      double positive_flow = 0, negative_flow = 0;
      for(int j = i; j < i + 14 && j < ArraySize(closes); j++)
      {
         if(typical_price > (highs[j-1] + lows[j-1] + closes[j-1]) / 3)
            positive_flow += money_flow;
         else
            negative_flow += money_flow;
      }
      
      mfi[i] = 100 - (100 / (1 + positive_flow/negative_flow));
   }
   
   // Draw MFI
   DrawIndicator("MFI", mfi, clrPurple);
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

bool IsDoubleTop(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 2) return false;
   
   double first_high = highs[start_idx-2];
   double second_high = highs[start_idx];
   double neckline = lows[start_idx-1];
   
   return MathAbs(first_high - second_high) / first_high < 0.01 &&
          second_high > neckline;
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

bool IsAscendingTriangle(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double resistance = highs[start_idx-4];
   double slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return MathAbs(highs[start_idx] - resistance) / resistance < 0.01 &&
          slope > 0;
}

bool IsRisingWedge(const double &highs[], const double &lows[], int start_idx)
{
   if(start_idx < 4) return false;
   
   double upper_slope = (highs[start_idx] - highs[start_idx-4]) / (start_idx - (start_idx-4));
   double lower_slope = (lows[start_idx] - lows[start_idx-4]) / (start_idx - (start_idx-4));
   
   return upper_slope > 0 && lower_slope > 0 && upper_slope < lower_slope;
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

//+------------------------------------------------------------------+
//| Draw volume profile                                              |
//+------------------------------------------------------------------+
void DrawVolumeProfile()
{
   double highs[], lows[], closes[], volumes[];
   ArrayResize(highs, 100);
   ArrayResize(lows, 100);
   ArrayResize(closes, 100);
   ArrayResize(volumes, 100);
   
   CopyHigh(_Symbol, PERIOD_CURRENT, 1, 100, highs);
   CopyLow(_Symbol, PERIOD_CURRENT, 1, 100, lows);
   CopyClose(_Symbol, PERIOD_CURRENT, 1, 100, closes);
   CopyTickVolume(_Symbol, PERIOD_CURRENT, 1, 100, volumes);
   
   double max_volume = 0;
   for(int i = 0; i < ArraySize(volumes); i++)
   {
      if(volumes[i] > max_volume)
         max_volume = volumes[i];
   }
   
   for(int i = 0; i < ArraySize(volumes); i++)
   {
      string name = PREFIX_VP + "Vol_" + IntegerToString(i);
      double volume_ratio = volumes[i] / max_volume;
      color vol_color = ColorScale(volume_ratio);
      
      ObjectCreate(0, name, OBJ_RECTANGLE, 0, TimeCurrent(), highs[i], TimeCurrent() + PeriodSeconds(PERIOD_CURRENT), lows[i]);
      ObjectSetInteger(0, name, OBJPROP_COLOR, vol_color);
      ObjectSetInteger(0, name, OBJPROP_FILL, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_SELECTED, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, name, OBJPROP_ZORDER, 0);
   }
}

//+------------------------------------------------------------------+
//| Color scale function                                             |
//+------------------------------------------------------------------+
color ColorScale(double value)
{
   if(value < 0.2)
      return clrLightBlue;
   else if(value < 0.4)
      return clrBlue;
   else if(value < 0.6)
      return clrDarkBlue;
   else if(value < 0.8)
      return clrNavy;
   else
      return clrBlack;
}
  