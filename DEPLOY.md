# Rose Bot - Deployment Guide

## Quick Start

### 1. Get Your Bot Token
- Message [@BotFather](https://t.me/BotFather) on Telegram
- Create a new bot with `/newbot`
- Copy the bot token

### 2. Get Your User ID
- Message [@userinfobot](https://t.me/userinfobot)
- Copy your ID number

---

## Platform-Specific Deployment

### Heroku (Easiest)

**Method 1: One-Click Deploy**
1. Click the Deploy to Heroku button in README.md
2. Fill in `TOKEN` and `OWNER_ID`
3. Click Deploy

**Method 2: CLI**
```bash
# Login to Heroku
heroku login

# Create app
heroku create my-rose-bot

# Set config vars
heroku config:set TOKEN=your_bot_token_here
heroku config:set OWNER_ID=your_user_id
heroku config:set ENV=ANYTHING
heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)

# Push code
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

### Railway

1. Fork this repo to GitHub
2. Go to [Railway Dashboard](https://railway.app/dashboard)
3. Click "New Project" -> "Deploy from GitHub repo"
4. Select your forked repo
5. Go to Variables tab, add:
   - `TOKEN` = your_bot_token
   - `OWNER_ID` = your_user_id
   - `ENV` = ANYTHING
6. Deploy!

### Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" -> "Web Service"
3. Connect your GitHub repo
4. Set:
   - Name: `rose-bot`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m bot`
5. Add Environment Variables:
   - `TOKEN`, `OWNER_ID`, `ENV`
6. Create Web Service

### Koyeb

1. Go to [Koyeb Control Panel](https://app.koyeb.com)
2. Click "Create App" -> "GitHub"
3. Select repository
4. Set:
   - Builder: `Python`
   - Run command: `python -m bot`
5. Add Environment Variables
6. Deploy

### DigitalOcean App Platform

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Choose GitHub source
4. Select Python environment
5. Add env vars in "Environment Variables" section
6. Launch App

### Microsoft Azure

**Container Instances:**
```bash
# Build and push to ACR
az acr login --name myregistry
az acr build --registry myregistry --image rose-bot .

# Create container
az container create \
  --resource-group myRG \
  --name rose-bot \
  --image myregistry.azurecr.io/rose-bot:latest \
  --cpu 1 --memory 1 \
  --environment-variables TOKEN=xxx OWNER_ID=xxx ENV=ANYTHING
```

**App Service:**
```bash
# Create webapp
az webapp up --name my-rose-bot --runtime "PYTHON:3.11"

# Set env vars
az webapp config appsettings set \
  --name my-rose-bot \
  --settings TOKEN=xxx OWNER_ID=xxx ENV=ANYTHING
```

### VPS / Dedicated Server

```bash
# Clone repo
git clone https://github.com/yourusername/rose-bot.git
cd rose-bot

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit with your settings

# Run
python -m bot

# Or use PM2 for background running
npm install -g pm2
pm2 start "python -m bot" --name rose-bot
pm2 save
pm2 startup
```

### Docker

```bash
# Build
docker build -t rose-bot .

# Run
docker run -d \
  --name rose-bot \
  --restart unless-stopped \
  -e TOKEN=your_token \
  -e OWNER_ID=your_id \
  -e ENV=ANYTHING \
  rose-bot

# Or with docker-compose
docker-compose up -d
```

---

## Verifying Deployment

After deploying:

1. Message your bot `/start`
2. Add bot to a test group
3. Promote bot to admin with these permissions:
   - ✅ Delete messages
   - ✅ Restrict members
   - ✅ Pin messages
   - ✅ Invite users
4. Test commands:
   - `/adminlist` - Should list admins
   - `/ban @username` - Should ban user
   - `/warn @username` - Should warn user
   - `/welcome on` - Should enable welcome

---

## Troubleshooting

### Bot not responding
- Check TOKEN is correct
- Check OWNER_ID is correct
- Check logs: `heroku logs --tail` or `docker logs rose-bot`

### Database errors
- Default SQLite works without configuration
- For PostgreSQL: ensure DATABASE_URL is correct

### Permission errors
- Ensure bot is admin in the group
- Ensure bot has required permissions

### Module import errors
- Ensure all dependencies installed: `pip install -r requirements.txt`

---

## Updating the Bot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart
# (depends on your deployment method)
```

---

## Support

For issues, please open a GitHub issue with:
1. Your deployment method
2. Error logs
3. Steps to reproduce
