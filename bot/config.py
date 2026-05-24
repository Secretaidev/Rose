"""
Configuration for Rose Bot
Supports both config.py and environment variables
"""

import os
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Determine if running in env mode
ENV = bool(os.environ.get('ENV', False))

if ENV:
    # Environment variables configuration (for Heroku, Railway, etc.)
    # TOKEN: get from @BotFather (example: 123456:ABCDEF...)
    TOKEN = os.environ.get('TOKEN', '')
    # OWNER_ID: get from @userinfobot (example: 123456789)
    OWNER_ID = int(os.environ.get('OWNER_ID', '0'))
    # OWNER_USERNAME: your Telegram username (example: your_username)
    OWNER_USERNAME = os.environ.get('OWNER_USERNAME', '')
    
    # Database
    # MONGODB_URL: MongoDB Atlas connection string (example: ******cluster/db)
    MONGODB_URL = os.environ.get('MONGODB_URL', '')
    # DATABASE_URL: SQLAlchemy DB URL (example: sqlite:///rose_bot.db or ******host/db)
    DATABASE_URL = os.environ.get('DATABASE_URL') or MONGODB_URL or 'sqlite:///rose_bot.db'
    
    # Webhook settings
    WEBHOOK = bool(os.environ.get('WEBHOOK', False))
    URL = os.environ.get('URL', '')
    PORT = int(os.environ.get('PORT', '8443'))
    CERT_PATH = os.environ.get('CERT_PATH', None)
    
    # Workers
    WORKERS = int(os.environ.get('WORKERS', '8'))
    
    # Features
    DEL_CMDS = bool(os.environ.get('DEL_CMDS', False))
    STRICT_GBAN = bool(os.environ.get('STRICT_GBAN', True))
    ALLOW_EXCL = bool(os.environ.get('ALLOW_EXCL', True))
    BAN_STICKER = os.environ.get('BAN_STICKER', 'CAADAgADOwADPPEcAXkko5EB3YmgAg')
    
    # Federation
    FED_ADMIN_TXT = os.environ.get('FED_ADMIN_TXT', 'Rose Bot')
    
    # Support users
    SUDO_USERS = [int(x) for x in os.environ.get('SUDO_USERS', '').split()] if os.environ.get('SUDO_USERS') else []
    SUPPORT_USERS = [int(x) for x in os.environ.get('SUPPORT_USERS', '').split()] if os.environ.get('SUPPORT_USERS') else []
    WHITELIST_USERS = [int(x) for x in os.environ.get('WHITELIST_USERS', '').split()] if os.environ.get('WHITELIST_USERS') else []
    
    # Load/No Load modules
    LOAD = os.environ.get('LOAD', '').split() if os.environ.get('LOAD') else []
    NO_LOAD = os.environ.get('NO_LOAD', '').split() if os.environ.get('NO_LOAD') else []
    
    # Messages dump channel (private channel ID, get via @userinfobot)
    MESSAGE_DUMP = os.environ.get('MESSAGE_DUMP', None)
    if MESSAGE_DUMP:
        MESSAGE_DUMP = int(MESSAGE_DUMP)
    
    # Logger channel (private channel ID for detailed logs; add bot as admin)
    LOGGER = os.environ.get('LOGGER_ID') or os.environ.get('LOGGER')
    if LOGGER:
        LOGGER = int(LOGGER)
    if not MESSAGE_DUMP and LOGGER:
        MESSAGE_DUMP = LOGGER
    
    # Default language
    DEFAULT_LANG = os.environ.get('DEFAULT_LANG', 'en')
    
else:
    # Local config.py configuration
    # TOKEN: get from @BotFather (example: 123456:ABCDEF...)
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    # OWNER_ID: get from @userinfobot (example: 123456789)
    OWNER_ID = 123456789  # Your Telegram user ID
    # OWNER_USERNAME: your Telegram username (example: your_username)
    OWNER_USERNAME = "your_username"
    
    # Database
    # MONGODB_URL: MongoDB Atlas connection string (example: ******cluster/db)
    MONGODB_URL = ''
    # DATABASE_URL: SQLAlchemy DB URL (example: sqlite:///rose_bot.db or ******host/db)
    DATABASE_URL = MONGODB_URL or 'sqlite:///rose_bot.db'
    
    # Webhook settings
    WEBHOOK = False
    URL = ""
    PORT = 8443
    CERT_PATH = None
    
    # Workers
    WORKERS = 8
    
    # Features
    DEL_CMDS = False
    STRICT_GBAN = True
    ALLOW_EXCL = True
    BAN_STICKER = 'CAADAgADOwADPPEcAXkko5EB3YmgAg'
    
    # Federation
    FED_ADMIN_TXT = 'Rose Bot'
    
    # Support users
    SUDO_USERS = []
    SUPPORT_USERS = []
    WHITELIST_USERS = []
    
    # Load/No Load modules
    LOAD = []
    NO_LOAD = []
    
    # Messages dump channel
    # MESSAGE_DUMP: private channel ID for moderation logs (example: -1001234567890)
    MESSAGE_DUMP = None
    
    # LOGGER: private channel ID for detailed logs (example: -1001234567890)
    LOGGER = None
    if not MESSAGE_DUMP and LOGGER:
        MESSAGE_DUMP = LOGGER
    
    # Default language
    DEFAULT_LANG = 'en'

# Constants
VERSION = "1.0.0"
START_IMG = "https://telegra.ph/file/5f1fac7d55e4ae5b0b55f.jpg"
START_TEXT = """
Hi {}, I'm *Rose*! 

I'm a powerful group management bot built to help you manage your groups efficiently. I can:

✅ Restrict users (ban/mute/kick)
✅ Greet users with customizable messages
✅ Protect against spam, flood & raids
✅ Filter messages & delete unwanted content
✅ Set rules, notes & filters
✅ Track warnings & user info
✅ And much more!

Send /help in a group to see available commands.

Made with ❤️ by Rose Bot Team
"""

HELP_TEXT = """
Hey! I'm *Rose*. I use various commands to keep your groups managed.

*Main Commands:*
/start - Start the bot
/help - Show this help message
/donate - Information about donations

*Admin Commands:*
/ban - Ban a user
/mute - Mute a user
/kick - Kick a user
/warn - Warn a user
/purge - Purge messages
/pin - Pin a message

*Settings Commands:*
/settings - Group settings
/setrules - Set group rules
/setwelcome - Set welcome message
/setgoodbye - Set goodbye message

*Info Commands:*
/info - User info
/id - Get chat/user ID
/adminlist - List admins

Send /help <module> for detailed info on a module.

*All commands can be used with / or !*
"""

DONATE_LINK = "https://t.me/rosebot"
