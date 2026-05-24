# Rose Bot - Telegram Group Management Bot Clone

A powerful, fully-featured Telegram group management bot clone inspired by the famous Miss Rose Bot. Built with Python and python-telegram-bot, featuring SQLite/PostgreSQL database support and easy deployment to multiple platforms.

## Features

### Moderation
- **Bans**: `/ban`, `/tban` (temp), `/dban` (delete+ban), `/sban` (silent), `/unban`
- **Mutes**: `/mute`, `/tmute`, `/dmute`, `/smute`, `/unmute`
- **Kicks**: `/kick`, `/dkick`, `/skick`
- **Warnings**: `/warn`, `/dwarn`, `/swarn`, `/resetwarn`, `/warns`, `/setwarnlimit`, `/setwarnmode`
- **Admin Management**: `/promote`, `/demote`, `/adminlist`, `/admincache`

### Welcome & Goodbye
- Custom welcome/goodbye messages with placeholders
- CAPTCHA verification for new members
- Welcome mute (mute until verification)
- Auto-clean welcome/goodbye/service messages
- Placeholders: `{first}`, `{last}`, `{fullname}`, `{username}`, `{mention}`, `{id}`, `{chatname}`

### Protection
- **Anti-Flood**: Configurable message limits and punishments
- **Locks**: URL, forward, bot, command, contact, location, email, phone, game, inline, media, sticker
- **Language Locks**: Arabic, Chinese, Japanese, Cyrillic, RTL
- **Blacklist**: Word filtering with configurable actions (delete/warn/ban/mute)
- **CAPTCHA**: Button-based verification for new members

### Group Management
- **Filters**: Auto-respond to keywords
- **Notes**: Save and retrieve notes with `#name` shortcut
- **Rules**: Set and display group rules
- **Federations**: Cross-group ban management
- **Approval**: Exempt trusted users from restrictions
- **Pins**: `/pin`, `/unpin`, `/unpinall`, `/pinned`
- **Purge**: Bulk message deletion with `/purge`, `/del`, `/purgefrom`, `/purgeto`
- **Reports**: `/report` or `@admin` to notify admins

### Info & Utilities
- **User Info**: `/info`, `/id`
- **Group Info**: `/groupinfo`, `/admins`
- **Connections**: Manage groups from private chat
- **Command Disabling**: Disable specific commands per group

## Deployment

### Prerequisites
- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (get from [@userinfobot](https://t.me/userinfobot))

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rose-bot.git
cd rose-bot
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the bot**
```bash
python -m bot
```

### Heroku Deployment

**Option 1: Deploy Button**

Click the button below to deploy directly to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

**Option 2: Manual Deploy**

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set TOKEN=your_bot_token
heroku config:set OWNER_ID=your_user_id
heroku config:set ENV=ANYTHING

# Add PostgreSQL (optional)
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

### Railway Deployment

1. Create account at [Railway](https://railway.app)
2. Create new project from GitHub repo
3. Add environment variables in Railway dashboard:
   - `TOKEN`
   - `OWNER_ID`
   - `ENV=ANYTHING`
   - `DATABASE_URL` (auto-generated if using Railway PostgreSQL)
4. Deploy!

### Render Deployment

1. Create account at [Render](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Set environment variables in Render dashboard
5. Use `python -m bot` as start command
6. Deploy!

### Koyeb Deployment

1. Create account at [Koyeb](https://koyeb.com)
2. Create new App from GitHub
3. Set environment variables
4. Deploy!

### DigitalOcean App Platform

1. Create account at [DigitalOcean](https://cloud.digitalocean.com)
2. Create new App from GitHub
3. Select Python environment
4. Set environment variables
5. Deploy!

### Azure Deployment

**Option 1: Azure Container Instances**

```bash
# Build container
az acr build --registry myregistry --image rose-bot .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name rose-bot \
  --image myregistry.azurecr.io/rose-bot \
  --environment-variables TOKEN=xxx OWNER_ID=xxx
```

**Option 2: Azure App Service**

1. Create Web App in Azure Portal
2. Set runtime to Python 3.11
3. Deploy from GitHub or local git
4. Set application settings (environment variables)

### Docker Deployment

```bash
# Build image
docker build -t rose-bot .

# Run with env file
docker run -d --env-file .env --name rose-bot rose-bot

# Or with docker-compose
docker-compose up -d
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TOKEN` | Yes | Bot token from @BotFather |
| `OWNER_ID` | Yes | Your Telegram user ID |
| `OWNER_USERNAME` | No | Your Telegram username |
| `ENV` | Yes (for Heroku/Railway) | Set to `ANYTHING` to use env vars |
| `DATABASE_URL` | No | Database URL (default: SQLite) |
| `WEBHOOK` | No | Set to `True` to use webhooks |
| `URL` | No | Webhook URL |
| `PORT` | No | Webhook port (default: 8443) |
| `WORKERS` | No | Worker threads (default: 8) |
| `SUDO_USERS` | No | Space-separated sudo user IDs |
| `SUPPORT_USERS` | No | Space-separated support user IDs |
| `WHITELIST_USERS` | No | Space-separated whitelisted user IDs |
| `DEL_CMDS` | No | Delete unauthorized commands |
| `STRICT_GBAN` | No | Strict global ban enforcement |
| `MESSAGE_DUMP` | No | Chat ID for action logging |

## Required Bot Permissions

When adding Rose Bot to your group, grant these admin permissions:

- ✅ Delete messages
- ✅ Restrict members
- ✅ Pin messages
- ✅ Invite users
- ✅ Manage video chats
- ✅ Remain anonymous (optional)

## Commands Quick Reference

### Moderation
| Command | Description |
|---------|-------------|
| `/ban [user] [reason]` | Ban user |
| `/tban [user] [time]` | Temporarily ban |
| `/unban [user]` | Unban user |
| `/mute [user]` | Mute user |
| `/tmute [user] [time]` | Temporarily mute |
| `/unmute [user]` | Unmute user |
| `/kick [user]` | Kick user |
| `/warn [user] [reason]` | Warn user |
| `/resetwarn [user]` | Reset warnings |

### Settings
| Command | Description |
|---------|-------------|
| `/welcome [on/off]` | Toggle welcome |
| `/setwelcome [text]` | Set welcome message |
| `/setflood [number]` | Set flood limit |
| `/lock [type]` | Lock message type |
| `/unlock [type]` | Unlock type |

### Info
| Command | Description |
|---------|-------------|
| `/info [user]` | User info |
| `/id` | Get IDs |
| `/adminlist` | List admins |
| `/rules` | Show rules |

## Project Structure

```
rose-bot/
├── bot/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database models
│   ├── helpers.py           # Helper functions & decorators
│   └── modules/
│       ├── __init__.py
│       ├── admin.py         # Admin management
│       ├── bans.py          # Ban/mute/kick
│       ├── warnings.py      # Warning system
│       ├── welcome.py       # Welcome/Goodbye/CAPTCHA
│       ├── antiflood.py     # Anti-flood
│       ├── locks.py         # Message locks
│       ├── filters.py       # Text filters
│       ├── notes.py         # Saved notes
│       ├── rules.py         # Group rules
│       ├── blacklist.py     # Word blacklist
│       ├── federation.py    # Federation system
│       ├── approval.py      # User approval
│       ├── purge.py         # Message purging
│       ├── pinning.py       # Pin management
│       ├── reports.py       # Reports
│       ├── info.py          # User/Chat info
│       ├── connections.py   # Group connections
│       ├── disable.py       # Command disabling
│       └── help_module.py   # Help system
├── data/                    # SQLite database storage
├── requirements.txt
├── Procfile                 # Heroku config
├── Dockerfile               # Docker config
├── docker-compose.yml       # Docker Compose config
├── runtime.txt              # Python runtime version
├── app.json                 # Heroku app config
├── .env.example             # Environment template
└── README.md                # This file
```

## License

This project is open source and available under the MIT License.

## Disclaimer

This is a clone/educational project inspired by Miss Rose Bot. It is not affiliated with the original Rose Bot team.

## Support

For issues and feature requests, please open an issue on GitHub.

---

Made with love for the Telegram community.
