# GPSkilledGuardian

Production-ready Discord bot for moderation, cryptocurrency payments (BTC/LTC), OSRS GP payments, automated role assignment, and OSRS trade automation via RuneLite plugin.

## Features

- **Discord Bot with Moderation**
  - Warn, mute, kick, ban commands
  - Moderation action logging
  - DM notifications to users
  
- **Multi-Payment Support**
  - Bitcoin (BTC) payments via BlockCypher API
  - Litecoin (LTC) payments via BlockCypher API
  - OSRS Gold Pieces (GP) payments with automated trading
  - Real-time cryptocurrency rate conversion
  - Payment confirmations and webhooks
  
- **Automated Role Assignment**
  - Assigns Discord roles after successful payment
  - Tracks user payment history
  - Payment status tracking

- **FastAPI Backend**
  - Webhook handlers for payment notifications
  - BlockCypher webhook integration
  - Health check endpoints
  - CORS support

- **OSRS Trade Automation**
  - RuneLite/OpenOSRS plugin integration
  - Automated world hopping
  - Automated trade requests
  - GP offering and trade acceptance
  - Screenshot capture of trades
  - RSN (RuneScape Name) validation via OSRS Hiscores

- **Security**
  - Encrypted credential storage using Fernet
  - Environment-based configuration
  - Webhook signature verification
  - Rate limiting support

- **Database**
  - SQLite with async support
  - Payment tracking
  - User management
  - Moderation action logging
  - OSRS trade records
  - Webhook event logging

## Architecture

```
GPSkilledGuardian/
├── api/                    # FastAPI backend
│   ├── routers/
│   │   └── webhooks.py    # Payment webhook handlers
│   └── main.py            # FastAPI app
├── bot/                   # Discord bot
│   ├── cogs/
│   │   ├── moderation.py  # Moderation commands
│   │   └── payments.py    # Payment commands
│   ├── utils/
│   │   ├── crypto_payments.py  # BTC/LTC processing
│   │   ├── osrs_payments.py    # OSRS GP processing
│   │   └── logger.py      # Logging setup
│   ├── database.py        # Database session management
│   ├── models.py          # SQLAlchemy models
│   └── main.py            # Bot entry point
├── config/                # Configuration
│   └── settings.py        # Settings with encryption
├── plugins/               # RuneLite plugin
│   └── runelite/
│       ├── GPSkilledGuardianPlugin.java
│       └── GPSkilledGuardianConfig.java
├── data/                  # Database storage
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## Installation

### Prerequisites

- Python 3.10+
- Discord Bot Token
- BlockCypher API Key (for crypto payments)
- Ngrok account (for local webhook testing)
- RuneLite (for OSRS automation)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/NacktGem/GPSkilledGuardian.git
   cd GPSkilledGuardian
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `DISCORD_GUILD_ID`: Your Discord server ID
   - `DISCORD_PAYMENT_ROLE_ID`: Role ID to assign after payment
   - `DISCORD_MOD_ROLE_ID`: Moderator role ID
   - `BTC_WALLET_ADDRESS`: Your Bitcoin wallet address
   - `LTC_WALLET_ADDRESS`: Your Litecoin wallet address
   - `BLOCKCYPHER_API_KEY`: Your BlockCypher API key
   - `NGROK_AUTH_TOKEN`: Your ngrok auth token
   - `API_SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `ENCRYPTION_KEY`: Generate with the provided script
   - `OSRS_RSN`: Your OSRS character name for trading
   - `OSRS_GP_RATE`: Rate in USD per million GP (e.g., 0.50)

5. **Generate encryption key**
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   Add the output to your `.env` file as `ENCRYPTION_KEY`.

6. **Create necessary directories**
   ```bash
   mkdir -p data logs
   ```

## Usage

### Running the Discord Bot

```bash
./start_bot.sh
# Or directly:
python -m bot.main
```

### Running the API Server

```bash
./start_api.sh
# Or directly:
python -m api.main
```

### Setting up Ngrok for Local Testing

```bash
./start_ngrok.sh
# Or directly:
ngrok http 8000
```

Note the ngrok URL and update your webhook configurations:
- BlockCypher webhooks: `https://your-ngrok-url.ngrok.io/webhooks/blockcypher`
- Payment webhooks: `https://your-ngrok-url.ngrok.io/webhooks/payment`

### Running Both Services

For production, you can use a process manager like `systemd`, `supervisor`, or `pm2`:

```bash
# Terminal 1: Discord Bot
python -m bot.main

# Terminal 2: API Server
python -m api.main

# Terminal 3: Ngrok (for local testing)
./start_ngrok.sh
```

## Discord Bot Commands

### Moderation Commands

- `/warn <member> [reason]` - Warn a user
- `/mute <member> <duration> [reason]` - Mute a user (duration in minutes)
- `/unmute <member>` - Unmute a user
- `/kick <member> [reason]` - Kick a user
- `/ban <member> [reason] [delete_messages]` - Ban a user
- `/unban <user_id>` - Unban a user

### Payment Commands

- `/pay <payment_type> <amount_usd>` - Initiate a payment
  - `payment_type`: btc, ltc, or osrs_gp
  - `amount_usd`: Amount in USD
  
- `/setrsn <rsn>` - Set your RuneScape Name for OSRS GP payments
- `/checkpayment` - Check your payment status

## API Endpoints

### Webhooks

- `POST /webhooks/payment` - General payment webhook
- `POST /webhooks/blockcypher` - BlockCypher webhook for crypto confirmations
- `GET /webhooks/health` - Health check endpoint

### Root

- `GET /` - API information

## RuneLite Plugin Setup

### Building the Plugin

1. Clone the RuneLite repository
2. Copy the plugin files to `runelite/runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian/`
3. Build the plugin with Gradle:
   ```bash
   ./gradlew runelite-client:build
   ```

### Installing the Plugin

1. Copy the built JAR to RuneLite's plugins directory
2. Enable "GPSkilled Guardian" in RuneLite's plugin hub
3. Configure the plugin settings:
   - Enable Plugin: Yes
   - Server Port: 9001 (default)
   - Auto Accept Trades: No (recommended for security)
   - Enable Logging: Yes (for debugging)
   - Screenshot Trades: Yes

### Plugin API Endpoints

The RuneLite plugin exposes a local HTTP server on port 9001:

- `GET /status` - Check if plugin is connected
- `GET /world` - Get current world number
- `POST /world/hop` - Hop to a specific world
- `POST /trade/request` - Send trade request to player
- `POST /trade/offer` - Offer GP in trade window
- `POST /trade/accept` - Accept current trade
- `GET /trade/status` - Get current trade status
- `GET /screenshot` - Take a screenshot
- `POST /chat/send` - Send a chat message

## Payment Flow

### Cryptocurrency Payments (BTC/LTC)

1. User runs `/pay btc 10.00` (for $10 worth of BTC)
2. Bot calculates BTC amount and provides payment address
3. User sends BTC to the provided address
4. BlockCypher webhook notifies the API of incoming transaction
5. API updates payment status to "confirming"
6. After required confirmations, payment is marked "completed"
7. Bot assigns the payment role to the user
8. User receives confirmation DM

### OSRS GP Payments

1. User runs `/pay osrs_gp 10.00` (for $10 worth of GP)
2. Bot calculates GP amount (e.g., 20M GP at $0.50/M rate)
3. User sets their RSN with `/setrsn PlayerName`
4. Bot validates RSN via OSRS Hiscores
5. Bot creates trade record and instructs user
6. Bot communicates with RuneLite plugin to initiate trade
7. RuneLite plugin:
   - Hops to specified world
   - Sends trade request to player
   - Offers GP in trade window
   - Takes screenshot upon completion
8. Payment is marked "completed" after trade
9. Bot assigns the payment role to the user

## Database Schema

### Tables

- **payments** - Payment transactions
- **osrs_trades** - OSRS trade records
- **users** - Discord user records
- **moderation_actions** - Moderation history
- **webhook_logs** - Webhook event logs

## Security Considerations

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use encryption** - Sensitive data is encrypted with Fernet
3. **Validate webhooks** - Verify webhook signatures
4. **Rate limiting** - Prevent abuse of commands
5. **Permission checks** - Moderation commands require appropriate roles
6. **Secure communication** - Use HTTPS for production webhooks
7. **Plugin security** - RuneLite plugin should validate requests

## Logging

Logs are stored in `logs/bot.log` with the following levels:
- DEBUG: Detailed debugging information
- INFO: General operational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

Console logs are colored for better readability.

## Development

### Running Tests

```bash
pytest tests/ -v --cov=bot --cov=api
```

### Code Quality

```bash
# Format code
black bot/ api/ config/

# Lint code
flake8 bot/ api/ config/

# Type checking
mypy bot/ api/ config/
```

## Production Deployment

### Using Systemd

Create `/etc/systemd/system/gpskilled-bot.service`:

```ini
[Unit]
Description=GPSkilledGuardian Discord Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/GPSkilledGuardian
Environment="PATH=/path/to/GPSkilledGuardian/venv/bin"
ExecStart=/path/to/GPSkilledGuardian/venv/bin/python -m bot.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/gpskilled-api.service`:

```ini
[Unit]
Description=GPSkilledGuardian FastAPI Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/GPSkilledGuardian
Environment="PATH=/path/to/GPSkilledGuardian/venv/bin"
ExecStart=/path/to/GPSkilledGuardian/venv/bin/python -m api.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl enable gpskilled-bot gpskilled-api
sudo systemctl start gpskilled-bot gpskilled-api
```

### Using Docker (Optional)

A Dockerfile can be added for containerized deployment.

## Troubleshooting

### Bot won't start
- Check `.env` file is configured correctly
- Verify Discord token is valid
- Check logs in `logs/bot.log`

### Payments not processing
- Verify BlockCypher API key is valid
- Check webhook URL is accessible
- Verify ngrok is running (for local testing)
- Check webhook logs in database

### OSRS trades failing
- Verify RuneLite plugin is installed and enabled
- Check plugin is listening on port 9001
- Verify RSN is valid
- Check player is online in the correct world

### Database errors
- Ensure `data/` directory exists and is writable
- Check SQLite database isn't corrupted
- Verify database migrations are applied

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team

## Disclaimer

This bot is for educational and legitimate business purposes only. Always comply with:
- Discord Terms of Service
- Jagex Rules (for OSRS)
- Local laws regarding cryptocurrency
- Payment processing regulations

Do not use this bot for:
- Scamming or fraud
- Rule breaking in games
- Illegal activities

## Credits

Developed by the GPSkilledGuardian Team

Special thanks to:
- discord.py community
- FastAPI team
- RuneLite developers
- BlockCypher API

---

**Version:** 1.0.0  
**Last Updated:** 2025