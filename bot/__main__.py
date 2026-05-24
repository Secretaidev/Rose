"""
Rose Bot - Main Entry Point
A Telegram Group Management Bot Clone
"""

import logging
import sys
import os
from typing import Iterable

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ParseMode
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, CallbackContext, InlineQueryHandler,
    ChosenInlineResultHandler
)
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError

from bot.config import TOKEN, OWNER_ID, WORKERS, WEBHOOK, URL, PORT, CERT_PATH, LOGGER
from bot.database import init_db, get_db, Chats, add_chat
from bot.modules import (
    admin, bans, warnings, welcome, antiflood, locks, 
    filters, notes, rules, blacklist, federation, approval,
    purge, pinning, reports, info, connections, disable, help_module
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def _chunk_message(message: str, limit: int = 4000) -> Iterable[str]:
    for start in range(0, len(message), limit):
        yield message[start:start + limit]

class TelegramLogHandler(logging.Handler):
    def __init__(self, bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            for chunk in _chunk_message(message):
                self.bot.send_message(self.chat_id, chunk)
        except Exception:
            pass

def setup_telegram_logging(bot):
    if not LOGGER:
        return
    handler = TelegramLogHandler(bot, LOGGER)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(pathname)s:%(lineno)d)'
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

# Error handler
def error_handler(update: Update, context: CallbackContext):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    if isinstance(context.error, Unauthorized):
        logger.warning("Unauthorized error - removing chat")
        return
    
    elif isinstance(context.error, BadRequest):
        logger.warning(f"Bad request: {context.error}")
    
    elif isinstance(context.error, TimedOut):
        logger.warning("Connection timed out")
        return
    
    elif isinstance(context.error, NetworkError):
        logger.warning("Network error")
        return
    
    elif isinstance(context.error, ChatMigrated):
        logger.info(f"Chat migrated to {context.error.new_chat_id}")
        return
    
    elif isinstance(context.error, TelegramError):
        logger.error(f"Telegram error: {context.error}")
        return
    
    try:
        if update and update.effective_message:
            update.effective_message.reply_text(
                "⚠️ An error occurred while processing your command.\n"
                "Please try again later."
            )
    except Exception:
        pass

# Load all modules
def load_modules(dispatcher):
    """Load all bot modules and their handlers"""
    modules = [
        admin, bans, warnings, welcome, antiflood, locks,
        filters, notes, rules, blacklist, federation, approval,
        purge, pinning, reports, info, connections, disable, help_module
    ]
    
    for module in modules:
        try:
            if hasattr(module, 'HANDLERS'):
                for handler in module.HANDLERS:
                    dispatcher.add_handler(handler)
                logger.info(f"Loaded module: {module.__name__}")
        except Exception as e:
            logger.error(f"Failed to load module {module.__name__}: {e}")

# Stats command (owner only)
def stats(update: Update, context: CallbackContext):
    """Show bot stats - /stats (owner only)"""
    if update.effective_user.id != OWNER_ID:
        update.effective_message.reply_text("This command is restricted to the bot owner.")
        return
    
    db = get_db()
    
    total_chats = db.query(Chats).count()
    
    from bot.database import Users, Filters, Notes, Blacklist, Federations, Warnings
    total_users = db.query(Users).count()
    total_filters = db.query(Filters).count()
    total_notes = db.query(Notes).count()
    total_blacklist = db.query(Blacklist).count()
    total_feds = db.query(Federations).count()
    total_warnings = db.query(Warnings).count()
    
    text = f"""
📊 <b>Bot Statistics</b>

<b>Groups:</b> {total_chats}
<b>Users:</b> {total_users}
<b>Filters:</b> {total_filters}
<b>Notes:</b> {total_notes}
<b>Blacklisted Words:</b> {total_blacklist}
<b>Federations:</b> {total_feds}
<b>Warnings:</b> {total_warnings}
"""
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

# Broadcast command (owner only)
def broadcast(update: Update, context: CallbackContext):
    """Broadcast message to all groups - /broadcast <message> (owner only)"""
    if update.effective_user.id != OWNER_ID:
        update.effective_message.reply_text("This command is restricted to the bot owner.")
        return
    
    if not context.args:
        update.effective_message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    
    db = get_db()
    chats = db.query(Chats).all()
    
    sent = 0
    failed = 0
    
    for chat in chats:
        try:
            context.bot.send_message(chat.chat_id, message, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            failed += 1
    
    update.effective_message.reply_text(
        f"Broadcast complete!\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}"
    )

# Chat migration handler
def migrate_chat(update: Update, context: CallbackContext):
    """Handle chat migration to supergroup"""
    old_chat_id = update.message.migrate_from_chat_id or update.message.chat_id
    new_chat_id = update.message.chat_id
    
    db = get_db()
    chat = db.query(Chats).filter(Chats.chat_id == old_chat_id).first()
    
    if chat:
        chat.chat_id = new_chat_id
        db.commit()
        logger.info(f"Migrated chat from {old_chat_id} to {new_chat_id}")

def main():
    """Main function to start the bot"""
    logger.info("Starting Rose Bot...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create updater
    updater = Updater(TOKEN, workers=WORKERS, use_context=True)
    dispatcher = updater.dispatcher

    setup_telegram_logging(updater.bot)
    
    # Load modules
    load_modules(dispatcher)
    logger.info("All modules loaded")
    
    # Add error handler
    dispatcher.add_error_handler(error_handler)
    
    # Add owner commands
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))
    
    # Add migration handler
    dispatcher.add_handler(MessageHandler(Filters.status_update.migrate, migrate_chat))
    
    # Start the bot
    if WEBHOOK and URL:
        logger.info(f"Starting webhook on port {PORT}")
        
        # Use different port configuration for Railway/Heroku compatibility
        webhook_port = int(os.environ.get('PORT', PORT))
        
        updater.start_webhook(
            listen="0.0.0.0",
            port=webhook_port,
            url_path=TOKEN,
            webhook_url=f"{URL}/{TOKEN}",
            cert=CERT_PATH
        )
    else:
        logger.info("Starting polling...")
        updater.start_polling(drop_pending_updates=True)
    
    logger.info("Rose Bot is running!")
    updater.idle()

if __name__ == '__main__':
    main()
