//+------------------------------------------------------------------+
//|                                             QSS_SignalSender.mqh |
//|                        Copyright 2025, Quantum SmartFlow Systems |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantum SmartFlow Systems"
#property link      "https://yoursite.com"

#include "config.mqh"

//+-----------------------------------------------------------------+
//| Send signal to Telegram                                         |
//+-----------------------------------------------------------------+
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
   
   string message = "";
   message += direction_emoji + " <b>" + signal_type + " SIGNAL - " + signal.symbol + "</b>\\n";
   message += "🔹 <b>Bias:</b> " + BiasToString(signal.bias) + " (" + TimeframeToString(HTF_Bias_Period) + ")\\n";
   message += "🔸 <b>Zone:</b> " + signal.zone_description + " @ " + DoubleToString(signal.entry_price, _Digits) + "\\n";
   message += "🎯 <b>Target:</b> 1:" + DoubleToString(signal.risk_reward, 1) + " R:R\\n";
   message += "⏰ <b>Time:</b> " + TimeToString(signal.signal_time, TIME_DATE|TIME_MINUTES) + "\\n";
   message += "\\n#QuantumSmartFlow #ICT #SMC";
   
   return message;
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
