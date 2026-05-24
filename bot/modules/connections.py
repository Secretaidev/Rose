"""
Connections module for Rose Bot
Allows managing groups from private chat
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import is_group_chat
from bot.database import get_db, Connections, add_chat, add_user

@is_group_chat
def connect(update: Update, context: CallbackContext):
    """Connect to a group - /connect (in group)"""
    user = update.effective_user
    chat = update.effective_chat
    
    db = get_db()
    
    # Remove existing connection
    existing = db.query(Connections).filter(Connections.user_id == user.id).first()
    if existing:
        existing.chat_id = chat.id
    else:
        connection = Connections(user_id=user.id, chat_id=chat.id)
        db.add(connection)
    
    db.commit()
    
    update.effective_message.reply_text(
        f"✅ Connected to {chat.title}!\n"
        f"You can now manage this group from my private messages."
    )

@is_group_chat
def disconnect(update: Update, context: CallbackContext):
    """Disconnect from group - /disconnect"""
    user = update.effective_user
    
    db = get_db()
    result = db.query(Connections).filter(Connections.user_id == user.id).delete()
    db.commit()
    
    if result:
        update.effective_message.reply_text("✅ Disconnected!")
    else:
        update.effective_message.reply_text("You weren't connected to any group.")

@is_group_chat
def connected(update: Update, context: CallbackContext):
    """Show connection status - /connected"""
    user = update.effective_user
    
    db = get_db()
    connection = db.query(Connections).filter(Connections.user_id == user.id).first()
    
    if connection:
        try:
            chat = context.bot.get_chat(connection.chat_id)
            update.effective_message.reply_text(
                f"✅ Connected to: <b>{chat.title}</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            update.effective_message.reply_text("Connected to an unknown chat. Use /disconnect.")
    else:
        update.effective_message.reply_text("❌ Not connected to any group.")

def connectionshelp(update: Update, context: CallbackContext):
    text = """
*Connections Module:*

/connect - Connect to current group
/disconnect - Disconnect from group
/connected - Show connection status

When connected, you can manage group settings from private chat with the bot.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Connections"

HANDLERS = [
    CommandHandler("connect", connect),
    CommandHandler("disconnect", disconnect),
    CommandHandler("connected", connected),
    CommandHandler("connectionshelp", connectionshelp),
]
