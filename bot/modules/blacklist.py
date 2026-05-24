"""
Blacklist module for Rose Bot
Handles blacklisted words and phrases
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import user_admin_required, bot_admin_required, is_group_chat
from bot.database import get_db, Blacklist as BlacklistTable, Chats, add_chat

@is_group_chat
@user_admin_required
def addblacklist(update: Update, context: CallbackContext):
    """Add a word to blacklist - /addblacklist <word>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to specify a word to blacklist!\n\n"
            "Usage: /addblacklist <word/phrase>\n"
            "You can add multiple words separated by spaces.\n\n"
            "Example: /addblacklist spam scam"
        )
        return
    
    added = []
    db = get_db()
    
    for word in context.args:
        # Check if already blacklisted
        existing = db.query(BlacklistTable).filter(
            BlacklistTable.chat_id == chat.id,
            BlacklistTable.trigger == word.lower()
        ).first()
        
        if not existing:
            bl = BlacklistTable(
                chat_id=chat.id,
                trigger=word.lower()
            )
            db.add(bl)
            added.append(word)
    
    db.commit()
    
    if added:
        message.reply_text(f"✅ Added to blacklist: {', '.join(added)}")
    else:
        message.reply_text("Those words are already blacklisted!")

@is_group_chat
@user_admin_required
def rmblacklist(update: Update, context: CallbackContext):
    """Remove a word from blacklist - /rmblacklist <word>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /rmblacklist <word>")
        return
    
    removed = []
    db = get_db()
    
    for word in context.args:
        result = db.query(BlacklistTable).filter(
            BlacklistTable.chat_id == chat.id,
            BlacklistTable.trigger == word.lower()
        ).delete()
        if result:
            removed.append(word)
    
    db.commit()
    
    if removed:
        message.reply_text(f"✅ Removed from blacklist: {', '.join(removed)}")
    else:
        message.reply_text("Those words were not in the blacklist!")

@is_group_chat
@user_admin_required
def unblacklist(update: Update, context: CallbackContext):
    """Alias for rmblacklist"""
    return rmblacklist(update, context)

@is_group_chat
def listblacklist(update: Update, context: CallbackContext):
    """List blacklisted words - /blacklist"""
    chat = update.effective_chat
    
    db = get_db()
    blacklist = db.query(BlacklistTable).filter(
        BlacklistTable.chat_id == chat.id
    ).all()
    
    if not blacklist:
        update.effective_message.reply_text("No blacklisted words in this group!")
        return
    
    text = f"🚫 <b>Blacklisted words in {chat.title}:</b>\n\n"
    for i, bl in enumerate(blacklist, 1):
        text += f"{i}. <code>{bl.trigger}</code>\n"
    
    text += "\nUse /rmblacklist <word> to remove a word"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def setblacklistmode(update: Update, context: CallbackContext):
    """Set blacklist action mode - /setblacklistmode <warn/delete/ban>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "Usage: /setblacklistmode <mode>\n\n"
            "Modes:\n"
            "delete - Delete message only\n"
            "warn - Delete message and warn user\n"
            "ban - Ban user\n"
            "mute - Mute user"
        )
        return
    
    mode = context.args[0].lower()
    
    if mode not in ('delete', 'warn', 'ban', 'mute'):
        message.reply_text("Invalid mode! Use: delete, warn, ban, or mute")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.blacklist_mode = mode
    db.commit()
    
    message.reply_text(f"✅ Blacklist action mode set to: {mode}")

def check_blacklist(update: Update, context: CallbackContext):
    """Check messages for blacklisted words"""
    if not update.effective_chat or not update.effective_message:
        return
    
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    if not user or not message.text:
        return
    
    # Skip admins
    try:
        member = chat.get_member(user.id)
        if member.status in ('administrator', 'creator'):
            return
    except Exception:
        return
    
    db = get_db()
    blacklist = db.query(BlacklistTable).filter(
        BlacklistTable.chat_id == chat.id
    ).all()
    
    if not blacklist:
        return
    
    text = message.text.lower()
    triggered = False
    
    for bl in blacklist:
        if bl.trigger.lower() in text:
            triggered = True
            break
    
    if triggered:
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        mode = chat_settings.blacklist_mode if chat_settings else 'delete'
        
        try:
            # Delete the message
            message.delete()
            
            if mode == 'warn':
                message.reply_text(
                    f"⚠️ {mention_html(user.id, user.first_name)}, your message contained blacklisted words!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == 'ban':
                chat.ban_member(user.id)
                message.reply_text(
                    f"🚫 {mention_html(user.id, user.first_name)} was banned for using blacklisted words!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == 'mute':
                from telegram import ChatPermissions
                permissions = ChatPermissions(can_send_messages=False)
                chat.restrict_member(user.id, permissions)
                message.reply_text(
                    f"🔇 {mention_html(user.id, user.first_name)} was muted for using blacklisted words!",
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            pass

@is_group_chat
@user_admin_required
def blacklisthelp(update: Update, context: CallbackContext):
    text = """
*Blacklist Module:*

/addblacklist <word> - Blacklist a word
/rmblacklist <word> - Remove from blacklist
/unblacklist <word> - Same as rmblacklist
/blacklist - List blacklisted words
/setblacklistmode <mode> - Set action

Modes: delete (default), warn, ban, mute
Messages containing blacklisted words will be automatically handled.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Blacklist"

HANDLERS = [
    CommandHandler("addblacklist", addblacklist),
    CommandHandler("addblocklist", addblacklist),
    CommandHandler("rmblacklist", rmblacklist),
    CommandHandler("rmblocklist", rmblacklist),
    CommandHandler("unblacklist", unblacklist),
    CommandHandler("unblocklist", unblacklist),
    CommandHandler("blacklist", listblacklist),
    CommandHandler("blocklist", listblacklist),
    CommandHandler("setblacklistmode", setblacklistmode),
    CommandHandler("setblocklistmode", setblacklistmode),
    CommandHandler("blacklisthelp", blacklisthelp),
    CommandHandler("blocklisthelp", blacklisthelp),
    MessageHandler(Filters.group & Filters.text & ~Filters.command, check_blacklist),
]
