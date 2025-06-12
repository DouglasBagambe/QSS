//+------------------------------------------------------------------+
//|                                                       config.mqh |
//|                        Copyright 2025, Quantum SmartFlow Systems |
//|                                             https://yoursite.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantum SmartFlow Systems"
#property link      "https://yoursite.com"

#include <Object.mqh>

//--- Enums
enum ENUM_SIGNAL_BIAS
{
   BIAS_BULLISH = 1,    // Bullish Bias
   BIAS_BEARISH = -1,   // Bearish Bias  
   BIAS_NEUTRAL = 0     // Neutral/Range
};

enum ENUM_ZONE_TYPE
{
   ZONE_ORDER_BLOCK,    // Order Block
   ZONE_FVG,           // Fair Value Gap
   ZONE_LIQUIDITY      // Liquidity Zone
};

//--- Input Parameters
input group "=== TIMEFRAME SETTINGS ==="
input ENUM_TIMEFRAMES HTF_Bias_Period = PERIOD_H1;          // HTF for Bias (1H/4H)
input ENUM_TIMEFRAMES LTF_Entry_Period = PERIOD_M15;        // LTF for Entry (15M/30M)

input group "=== STRATEGY PARAMETERS ==="
input int MinDisplacementPips = 20;                         // Min Displacement Size (pips)
input int FVG_MinSizePips = 5;                              // Min FVG Size (pips)
input int OrderBlock_LookbackBars = 50;                     // Order Block Lookback Period
input double EquilibriumLevel = 50.0;                       // 50% Equilibrium Level
input bool DrawVisuals = true;                              // Draw Visual Objects
input int SignalCooldownSeconds = 600;                      // Signal Cooldown (seconds)

input group "=== RISK MANAGEMENT ==="
input double DefaultRiskReward = 3.0;                       // Default R:R Ratio
input int StopLossBuffer = 5;                               // Stop Loss Buffer (pips)

input group "=== TELEGRAM SETTINGS ==="
input bool EnableTelegramAlerts = true;                     // Enable Telegram Alerts
input string TelegramBotToken = "";                         // Telegram Bot Token
input string TelegramChatID = "";                           // Telegram Chat ID
input int TelegramTimeout = 5000;                           // Request Timeout (ms)

input group "=== VISUAL SETTINGS ==="
input color BullishOB_Color = clrLimeGreen;                // Bullish Order Block Color
input color BearishOB_Color = clrCrimson;                  // Bearish Order Block Color
input color FVG_Bull_Color = clrAqua;                      // Bullish FVG Color
input color FVG_Bear_Color = clrOrange;                    // Bearish FVG Color
input color CHOCH_Color = clrYellow;                       // CHOCH Marker Color
input color BOS_Color = clrMagenta;                        // BOS Marker Color
input int VisualTransparency = 80;                         // Object Transparency (0-255)

//--- Global Constants
#define EXPERT_NAME "QuantumSmartFlow"
#define EXPERT_VERSION "1.0"

//--- Object Name Prefixes
#define PREFIX_OB "QSS_OB_"
#define PREFIX_FVG "QSS_FVG_"
#define PREFIX_CHOCH "QSS_CHOCH_"
#define PREFIX_BOS "QSS_BOS_"
#define PREFIX_SIGNAL "QSS_SIGNAL_"
#define PREFIX_EQUI "QSS_EQUI_"

//--- Structure Definitions
struct ZoneInfo
{
   ENUM_ZONE_TYPE type;
   datetime time_start;
   datetime time_end;
   double price_high;
   double price_low;
   bool is_bullish;
   bool is_tested;
   string description;
};

struct SignalInfo
{
   datetime signal_time;
   string symbol;
   ENUM_SIGNAL_BIAS bias;
   string zone_description;
   double entry_price;
   double stop_loss;
   double take_profit;
   double risk_reward;
   bool telegram_sent;
};

//--- Global Variables
datetime g_lastSignalTime = 0;
SignalInfo g_lastSignal;
ZoneInfo g_orderBlocks[];
ZoneInfo g_fvgZones[];

//--- Utility Functions
double PipsToPrice(double pips)
{
   return pips * SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 
          (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) == 5 || 
           SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) == 3 ? 10 : 1);
}

double PriceToPips(double price_diff)
{
   return price_diff / (SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 
          (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) == 5 || 
           SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) == 3 ? 10 : 1));
}

string TimeframeToString(ENUM_TIMEFRAMES tf)
{
   switch(tf)
   {
      case PERIOD_M1:  return "1M";
      case PERIOD_M5:  return "5M";
      case PERIOD_M15: return "15M";
      case PERIOD_M30: return "30M";
      case PERIOD_H1:  return "1H";
      case PERIOD_H4:  return "4H";
      case PERIOD_D1:  return "1D";
      default:         return "UNKNOWN";
   }
}

string BiasToString(ENUM_SIGNAL_BIAS bias)
{
   switch(bias)
   {
      case BIAS_BULLISH: return "Bullish";
      case BIAS_BEARISH: return "Bearish";
      default:           return "Neutral";
   }
}

bool IsNewBar()
{
   static datetime lastBarTime = 0;
   datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
   
   if(currentBarTime != lastBarTime)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   
   return false;
}

void CleanupObjects(string prefix)
{
   for(int i = ObjectsTotal(0, 0, -1) - 1; i >= 0; i--)
   {
      string objName = ObjectName(0, i, 0, -1);
      if(StringFind(objName, prefix) == 0)
      {
         ObjectDelete(0, objName);
      }
   }
} 