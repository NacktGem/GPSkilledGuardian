# Quick Reference Guide

## Discord Bot Commands

### Moderation Commands (Requires Moderator Role)

| Command | Description | Usage |
|---------|-------------|-------|
| `/warn` | Warn a user | `/warn @user [reason]` |
| `/mute` | Mute a user temporarily | `/mute @user <duration_minutes> [reason]` |
| `/unmute` | Unmute a user | `/unmute @user` |
| `/kick` | Kick a user from server | `/kick @user [reason]` |
| `/ban` | Ban a user from server | `/ban @user [reason] [delete_messages_days]` |
| `/unban` | Unban a user | `/unban <user_id>` |

### Payment Commands (All Users)

| Command | Description | Usage |
|---------|-------------|-------|
| `/pay` | Initiate a payment | `/pay <btc\|ltc\|osrs_gp> <amount_usd>` |
| `/setrsn` | Set RuneScape Name | `/setrsn <your_rsn>` |
| `/checkpayment` | Check payment status | `/checkpayment` |

## Payment Types

### Bitcoin (BTC)
```
/pay btc 10.00
```
- Calculates BTC amount from USD
- Provides payment address
- Monitors blockchain confirmations
- Assigns role after 3 confirmations (default)

### Litecoin (LTC)
```
/pay ltc 10.00
```
- Calculates LTC amount from USD
- Provides payment address
- Monitors blockchain confirmations
- Assigns role after 3 confirmations (default)

### OSRS Gold Pieces (GP)
```
/pay osrs_gp 10.00
/setrsn YourRSN
```
- Calculates GP amount from USD
- Validates RSN via OSRS Hiscores
- Initiates automated trade
- Assigns role after trade completion

## API Endpoints

### Webhooks

**General Payment Webhook**
```
POST /webhooks/payment
Content-Type: application/json

{
  "payment_id": 123,
  "status": "completed",
  "user_id": "123456789"
}
```

**BlockCypher Webhook**
```
POST /webhooks/blockcypher
X-EventType: tx-confirmation
X-EventId: abc123

{
  "hash": "tx_hash",
  "confirmations": 3
}
```

**Health Check**
```
GET /webhooks/health

Response: {
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00"
}
```

### Root
```
GET /

Response: {
  "name": "GPSkilledGuardian API",
  "version": "1.0.0",
  "status": "running"
}
```

## RuneLite Plugin API

All endpoints on `http://localhost:9001`

### Status Check
```
GET /status

Response: {
  "status": "connected",
  "logged_in": true,
  "world": 302
}
```

### World Management
```
GET /world
Response: {"world": 302}

POST /world/hop
Body: {"world": 302}
Response: {"success": true, "world": 302}
```

### Trading
```
POST /trade/request
Body: {"rsn": "PlayerName"}
Response: {"success": true, "rsn": "PlayerName"}

POST /trade/offer
Body: {"amount": 20000000}
Response: {"success": true, "amount": 20000000}

POST /trade/accept
Response: {"success": true}

GET /trade/status
Response: {
  "status": "in_progress",
  "player": "PlayerName",
  "offered_amount": 20000000
}
```

### Screenshot
```
GET /screenshot
Response: Binary PNG image data
```

### Chat
```
POST /chat/send
Body: {
  "message": "Trade complete!",
  "public": false
}
Response: {"success": true}
```

## Environment Variables Reference

### Discord
- `DISCORD_TOKEN` - Bot token from Discord Developer Portal
- `DISCORD_GUILD_ID` - Your server ID
- `DISCORD_PAYMENT_ROLE_ID` - Role ID for paid members
- `DISCORD_MOD_ROLE_ID` - Moderator role ID

### Database
- `DATABASE_URL` - Database connection string (default: SQLite)

### API
- `API_HOST` - Host to bind (default: 0.0.0.0)
- `API_PORT` - Port to listen on (default: 8000)
- `API_SECRET_KEY` - Secret key for API (generate with openssl)

### Cryptocurrency
- `BTC_WALLET_ADDRESS` - Your Bitcoin address
- `LTC_WALLET_ADDRESS` - Your Litecoin address
- `BLOCKCYPHER_API_KEY` - BlockCypher API key
- `BLOCKCHAIN_INFO_API_KEY` - Blockchain.info API key (optional)

### OSRS
- `OSRS_GP_RATE` - USD per million GP (e.g., 0.50)
- `OSRS_RSN` - Your trading character name
- `OSRS_WORLD` - Preferred trading world (default: 302)
- `OSRS_TRADE_LOCATION` - Trading location (default: Grand Exchange)

### Payment Configuration
- `PAYMENT_CONFIRMATION_BLOCKS` - Required confirmations (default: 3)
- `PAYMENT_TIMEOUT_MINUTES` - Payment expiry time (default: 30)

### Ngrok
- `NGROK_AUTH_TOKEN` - Ngrok authentication token
- `NGROK_DOMAIN` - Custom ngrok domain (optional)

### Security
- `ENCRYPTION_KEY` - Fernet encryption key
- `PAYMENT_WEBHOOK_URL` - Webhook URL for payment notifications
- `BLOCKCYPHER_WEBHOOK_TOKEN` - Webhook token

### RuneLite Plugin
- `RUNELITE_PLUGIN_HOST` - Plugin host (default: localhost)
- `RUNELITE_PLUGIN_PORT` - Plugin port (default: 9001)

### Logging
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE` - Log file path (default: logs/bot.log)

### Development
- `DEV_MODE` - Enable development mode (True/False)

## Common Workflows

### Setup New User Payment (BTC)

1. User runs: `/pay btc 10.00`
2. Bot calculates BTC amount and provides address
3. User sends BTC to provided address
4. BlockCypher detects transaction and sends webhook
5. API processes webhook and updates payment status
6. After confirmations, bot assigns payment role
7. User receives DM confirmation

### Setup OSRS GP Payment

1. User runs: `/pay osrs_gp 10.00`
2. Bot calculates GP amount
3. User runs: `/setrsn PlayerName`
4. Bot validates RSN via OSRS Hiscores
5. Bot creates trade record and instructs user
6. Bot sends trade request to RuneLite plugin
7. Plugin hops to world and sends trade
8. Plugin offers GP and waits for acceptance
9. User accepts trade
10. Plugin takes screenshot
11. Bot marks payment complete and assigns role

### Moderate User

1. Moderator runs: `/warn @user Breaking rules`
2. Bot logs warning to database
3. Bot sends DM to user with warning details
4. User sees warning embed with reason and moderator

### Check Payment Status

1. User runs: `/checkpayment`
2. Bot queries database for user's payments
3. Bot displays embed with payment history
4. Shows status, amount, and timestamps

## Database Schema Quick Reference

### payments
- `id`, `user_id`, `username`, `payment_type`, `amount_usd`
- `amount_crypto`, `amount_gp`, `wallet_address`, `transaction_id`
- `status`, `confirmations`, `created_at`, `completed_at`, `expires_at`

### osrs_trades
- `id`, `payment_id`, `user_id`, `rsn`, `gp_amount`
- `world`, `location`, `status`
- `trade_started_at`, `trade_completed_at`, `screenshot_path`

### users
- `id`, `discord_id`, `username`, `has_paid_role`
- `total_payments`, `total_spent_usd`, `osrs_rsn`
- `created_at`, `last_payment_at`

### moderation_actions
- `id`, `user_id`, `moderator_id`, `action_type`
- `reason`, `duration`, `created_at`, `expires_at`, `is_active`

### webhook_logs
- `id`, `webhook_type`, `payload`, `status`
- `processed_at`, `created_at`, `error_message`

## Troubleshooting Quick Tips

### Bot Won't Start
```bash
# Check logs
tail -f logs/bot.log

# Verify token
grep DISCORD_TOKEN .env

# Test Python
python3 -m bot.main --help
```

### Payments Not Processing
```bash
# Check API status
curl http://localhost:8000/webhooks/health

# Check ngrok
curl http://localhost:4040/api/tunnels

# View recent webhooks
sqlite3 data/gpskilled.db "SELECT * FROM webhook_logs ORDER BY created_at DESC LIMIT 5;"
```

### OSRS Trades Failing
```bash
# Check plugin status
curl http://localhost:9001/status

# Verify RSN
python3 -c "from bot.utils.osrs_payments import OSRSGPPaymentProcessor; import asyncio; processor = OSRSGPPaymentProcessor(0.5); print(asyncio.run(processor.validate_rsn('Zezima')))"
```

## Keyboard Shortcuts for Development

**Start all services:**
```bash
# Create a tmux session
tmux new -s gpskilled

# Split into 3 panes
Ctrl+B then %  # Split vertically
Ctrl+B then "  # Split horizontally

# In each pane:
./start_bot.sh
./start_api.sh
./start_ngrok.sh
```

**View logs:**
```bash
# Real-time bot logs
tail -f logs/bot.log

# Search for errors
grep ERROR logs/bot.log

# Count warnings
grep -c WARNING logs/bot.log
```

**Database queries:**
```bash
# Count payments
sqlite3 data/gpskilled.db "SELECT COUNT(*) FROM payments;"

# Recent payments
sqlite3 data/gpskilled.db "SELECT * FROM payments ORDER BY created_at DESC LIMIT 10;"

# User stats
sqlite3 data/gpskilled.db "SELECT discord_id, total_payments, total_spent_usd FROM users WHERE total_payments > 0;"
```
