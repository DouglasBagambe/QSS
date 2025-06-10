# Premium Trading Telegram Bot

A high-end, well-structured Telegram bot for semi-automated trading systems. Built with Python 3.10+ and aiogram 3.x.

## Features

- 🔐 Password-protected access
- 📊 Real-time trading signals
- ⚙️ Customizable risk management
- 🔒 Secure webhook endpoint
- 💼 Multiple risk modes (Aggressive, Balanced, Conservative)
- 🎯 Clean, modern UI with inline keyboards

## Prerequisites

- Python 3.10 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Basic understanding of trading concepts

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd telegram-trading-bot
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:

```
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
SIGNAL_SECRET=your_secret_key
PASSWORD=your_bot_password
```

## Running the Bot

1. Start the bot:

```bash
python -m bot.main
```

2. Start the signal webhook server (in a separate terminal):

```bash
python -m webhook.signal_api
```

## Usage

1. Start the bot with `/start` command
2. Enter the password when prompted
3. Use the following commands:
   - `/status` - Check bot status
   - `/risk` - Configure risk settings
   - `/lastsignal` - View last trading signal
   - `/help` - Show help message

## Sending Trading Signals

Send POST requests to the webhook endpoint with the following format:

```json
{
  "pair": "EURUSD",
  "direction": "buy",
  "entry": 1.2345,
  "sl": 1.23,
  "tp": 1.24
}
```

Headers required:

```
X-Signal-Secret: your_secret_key
```

## Security Features

- Password protection for bot access
- Secure webhook endpoint with secret key
- User authorization system
- Rate limiting and error handling

## Deployment

The bot can be deployed on:

- Local machine
- VPS (e.g., DigitalOcean, AWS)
- Cloud platforms (e.g., Heroku, Render)

For production deployment:

1. Set up a proper web server (e.g., Nginx)
2. Use SSL/TLS for the webhook endpoint
3. Set up proper logging and monitoring
4. Use a production-grade database for user data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
