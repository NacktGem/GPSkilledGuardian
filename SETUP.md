# Setup and Deployment Guide

## Quick Start

This guide will help you set up the GPSkilledGuardian Discord bot with payment processing and OSRS automation.

## Prerequisites

- Python 3.10 or higher
- Discord Developer Account
- BlockCypher API account (for cryptocurrency payments)
- Ngrok account (for local development)
- RuneLite client (for OSRS automation)

## Step 1: Discord Bot Setup

### Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "GPSkilledGuardian" and create
4. Go to "Bot" tab
5. Click "Add Bot"
6. Enable these Privileged Gateway Intents:
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
7. Copy the bot token (you'll need this for `.env`)

### Invite Bot to Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Manage Roles
   - Kick Members
   - Ban Members
   - Moderate Members
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and open in browser
5. Select your server and authorize

### Get Server and Role IDs

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your server → Copy ID (this is `DISCORD_GUILD_ID`)
3. Create a role for paid members
4. Right-click the role → Copy ID (this is `DISCORD_PAYMENT_ROLE_ID`)
5. Create or identify moderator role
6. Right-click the role → Copy ID (this is `DISCORD_MOD_ROLE_ID`)

## Step 2: BlockCypher Setup (Cryptocurrency)

1. Sign up at [BlockCypher](https://www.blockcypher.com/)
2. Create a new API token
3. Copy the token (this is `BLOCKCYPHER_API_KEY`)
4. Note your Bitcoin wallet address (for `BTC_WALLET_ADDRESS`)
5. Note your Litecoin wallet address (for `LTC_WALLET_ADDRESS`)

## Step 3: Ngrok Setup (Local Development)

1. Sign up at [Ngrok](https://ngrok.com/)
2. Go to "Your Authtoken"
3. Copy the authtoken (this is `NGROK_AUTH_TOKEN`)
4. (Optional) Purchase a custom domain for permanent webhook URL

## Step 4: Project Setup

### Clone Repository

```bash
git clone https://github.com/NacktGem/GPSkilledGuardian.git
cd GPSkilledGuardian
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your favorite text editor:
```bash
nano .env  # or vim, code, etc.
```

3. Fill in all the required values:

```env
# Discord Configuration
DISCORD_TOKEN=your_bot_token_from_step_1
DISCORD_GUILD_ID=your_server_id
DISCORD_PAYMENT_ROLE_ID=your_payment_role_id
DISCORD_MOD_ROLE_ID=your_moderator_role_id

# Database
DATABASE_URL=sqlite+aiosqlite:///data/gpskilled.db

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=generated_secret_key_see_below

# Cryptocurrency Configuration
BTC_WALLET_ADDRESS=your_btc_address
LTC_WALLET_ADDRESS=your_ltc_address
BLOCKCYPHER_API_KEY=your_blockcypher_token

# OSRS Configuration
OSRS_GP_RATE=0.50
OSRS_RSN=YourTradingAccountRSN
OSRS_WORLD=302
OSRS_TRADE_LOCATION=Grand Exchange

# Ngrok
NGROK_AUTH_TOKEN=your_ngrok_token

# Encryption (generate below)
ENCRYPTION_KEY=generated_encryption_key_see_below

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Development
DEV_MODE=True
```

### Generate Keys

Generate API secret key:
```bash
openssl rand -hex 32
```

Generate encryption key:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add these to your `.env` file.

### Create Required Directories

```bash
mkdir -p data logs
```

## Step 5: Running the Bot

### Option A: Development Mode (Separate Terminals)

Terminal 1 - Discord Bot:
```bash
./start_bot.sh
```

Terminal 2 - API Server:
```bash
./start_api.sh
```

Terminal 3 - Ngrok Tunnel:
```bash
./start_ngrok.sh
```

### Option B: Direct Python Execution

Discord Bot:
```bash
source venv/bin/activate
python -m bot.main
```

API Server:
```bash
source venv/bin/activate
python -m api.main
```

Ngrok:
```bash
ngrok http 8000
```

### Option C: Production (systemd)

1. Create systemd service files (see README.md)
2. Enable and start services:
```bash
sudo systemctl enable gpskilled-bot gpskilled-api
sudo systemctl start gpskilled-bot gpskilled-api
```

## Step 6: Configure Webhooks

### Get Ngrok URL

After starting ngrok, you'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Configure BlockCypher Webhooks

You'll need to create webhooks for each payment address. This can be done programmatically or via the bot when payments are created.

Example webhook URL:
```
https://abc123.ngrok.io/webhooks/blockcypher
```

## Step 7: RuneLite Plugin Setup (OSRS Automation)

### Build the Plugin

1. Clone RuneLite:
```bash
git clone https://github.com/runelite/runelite.git
cd runelite
```

2. Copy plugin files:
```bash
mkdir -p runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian
cp /path/to/GPSkilledGuardian/plugins/runelite/*.java \
   runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian/
```

3. Build:
```bash
./gradlew runelite-client:build
```

### Install and Configure

1. Start RuneLite with the built client
2. Enable the plugin in settings
3. Configure:
   - Enable Plugin: ✓
   - Server Port: 9001
   - Enable Logging: ✓
   - Screenshot Trades: ✓

## Step 8: Testing

### Test Discord Commands

In your Discord server, try:

```
/help
```

Moderation commands (requires moderator role):
```
/warn @user Testing warning system
/mute @user 5 Testing mute for 5 minutes
```

Payment commands:
```
/pay btc 10.00
/pay ltc 10.00
/pay osrs_gp 10.00
```

### Test API Endpoints

Health check:
```bash
curl http://localhost:8000/webhooks/health
```

Root endpoint:
```bash
curl http://localhost:8000/
```

### Test RuneLite Plugin

With RuneLite running and logged in:
```bash
curl http://localhost:9001/status
```

## Troubleshooting

### Bot Not Starting

**Check logs:**
```bash
tail -f logs/bot.log
```

**Common issues:**
- Invalid Discord token
- Missing `.env` file
- Wrong Python version
- Missing dependencies

### API Not Starting

**Check if port is in use:**
```bash
lsof -i :8000
```

**Kill existing process:**
```bash
kill -9 $(lsof -t -i :8000)
```

### Payments Not Processing

**Check ngrok is running:**
```bash
curl http://localhost:4040/api/tunnels
```

**Verify webhook URLs:**
- Check ngrok URL is correct
- Ensure webhook is created in BlockCypher
- Check webhook logs in database

### OSRS Trades Failing

**Check plugin connection:**
```bash
curl http://localhost:9001/status
```

**Verify:**
- RuneLite is running
- Logged into OSRS
- Plugin is enabled
- Correct world and location

## Security Checklist

- [ ] Generated strong encryption key
- [ ] Set strong API secret key
- [ ] Never committed `.env` file
- [ ] Using HTTPS in production
- [ ] Webhook signatures verified
- [ ] Rate limiting configured
- [ ] Moderation roles properly set
- [ ] Plugin only accepts localhost connections
- [ ] Monitoring logs for suspicious activity

## Production Deployment

### Before Going Live

1. **Change DEV_MODE to False:**
```env
DEV_MODE=False
```

2. **Use production database:**
```env
DATABASE_URL=postgresql://user:pass@host/db  # Or your preferred DB
```

3. **Set up SSL/TLS:**
- Use a domain with SSL certificate
- Configure nginx/apache as reverse proxy
- Use Let's Encrypt for free certificates

4. **Configure firewall:**
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

5. **Set up monitoring:**
- Configure log rotation
- Set up error alerting
- Monitor resource usage

6. **Backup strategy:**
- Regular database backups
- Backup encryption keys securely
- Test restore procedures

### Scaling Considerations

- Use Redis for caching
- Use PostgreSQL instead of SQLite
- Run multiple bot instances (if needed)
- Use load balancer for API
- Monitor and optimize database queries

## Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for errors
- Check payment processing
- Verify bot uptime

**Weekly:**
- Review moderation actions
- Check database size
- Update dependencies if needed

**Monthly:**
- Security audit
- Performance review
- Backup verification

### Updates

Pull latest changes:
```bash
git pull origin main
```

Update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

Restart services:
```bash
sudo systemctl restart gpskilled-bot gpskilled-api
```

## Support

For issues and questions:
- Check logs in `logs/bot.log`
- Review documentation in `README.md`
- Check plugin documentation in `plugins/runelite/PLUGIN_README.md`
- Open an issue on GitHub

## Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [BlockCypher API Documentation](https://www.blockcypher.com/dev/)
- [RuneLite Wiki](https://github.com/runelite/runelite/wiki)
- [Ngrok Documentation](https://ngrok.com/docs)
