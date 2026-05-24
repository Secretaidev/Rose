"""
Rules module for Rose Bot
Handles group rules
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import user_admin_required, is_group_chat
from bot.database import get_db, Chats, add_chat

@is_group_chat
def rules(update: Update, context: CallbackContext):
    """Show group rules - /rules"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings or not chat_settings.rules:
        update.effective_message.reply_text(
            "No rules have been set for this group!\n"
            "Admins can set rules with: /setrules <rules>"
        )
        return
    
    text = f"📜 <b>Rules for {chat.title}:</b>\n\n"
    text += chat_settings.rules
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def setrules(update: Update, context: CallbackContext):
    """Set group rules - /setrules <rules>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args and not message.reply_to_message:
        message.reply_text(
            "You need to provide the rules!\n\n"
            "Usage: /setrules <rules>\n"
            "Or reply to a message containing the rules."
        )
        return
    
    if message.reply_to_message:
        rules_text = message.reply_to_message.text
    else:
        rules_text = " ".join(context.args)
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.rules = rules_text
    db.commit()
    
    message.reply_text("✅ Group rules have been set!")

@is_group_chat
@user_admin_required
def resetrules(update: Update, context: CallbackContext):
    """Reset rules - /resetrules"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if chat_settings:
        chat_settings.rules = None
        db.commit()
    
    update.effective_message.reply_text("✅ Group rules have been reset!")

@is_group_chat
@user_admin_required
def ruleshelp(update: Update, context: CallbackContext):
    text = """
*Rules Module:*

/rules - Show group rules
/setrules <rules> - Set group rules
/resetrules - Remove all rules

Admins only for /setrules and /resetrules.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Rules"

HANDLERS = [
    CommandHandler("rules", rules),
    CommandHandler("setrules", setrules),
    CommandHandler("resetrules", resetrules),
    CommandHandler("ruleshelp", ruleshelp),
]
