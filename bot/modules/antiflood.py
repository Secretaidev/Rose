"""
Anti-Flood module for Rose Bot
Handles flood detection and prevention
"""

import time
from collections import defaultdict
from telegram import Update, ChatPermissions, ParseMode
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import user_admin_required, bot_admin_required, extract_time, is_group_chat
from bot.database import get_db, Chats, add_chat

# In-memory flood tracking: {(chat_id, user_id): [timestamps]}
flood_tracker = defaultdict(list)
FLOOD_WINDOW = 10  # seconds

@is_group_chat
@user_admin_required
def setflood(update: Update, context: CallbackContext):
    """Set flood limit - /setflood <number>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args or not context.args[0].isdigit():
        message.reply_text(
            "You need to specify a number!\n"
            "Usage: /setflood <number> (0 to disable)\n\n"
            "Example: /setflood 5"
        )
        return
    
    limit = int(context.args[0])
    
    if limit < 0:
        message.reply_text("Flood limit must be 0 or higher!")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.flood_limit = limit
    chat_settings.antiflood_enabled = (limit > 0)
    db.commit()
    
    if limit == 0:
        message.reply_text("✅ Anti-flood has been disabled!")
    else:
        message.reply_text(f"✅ Flood limit set to {limit} messages per {FLOOD_WINDOW} seconds!")

@is_group_chat
@user_admin_required
def setfloodmode(update: Update, context: CallbackContext):
    """Set flood punishment mode - /setfloodmode <action> [time]"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to specify an action!\n\n"
            "Available modes:\n"
            "ban - Ban user\n"
            "kick - Kick user\n"
            "mute - Mute user\n"
            "tmute - Temporarily mute (e.g., tmute 1h)\n"
            "tban - Temporarily ban (e.g., tban 1h)\n\n"
            "Usage: /setfloodmode <mode> [time]"
        )
        return
    
    mode = context.args[0].lower()
    
    if mode not in ('ban', 'kick', 'mute', 'tmute', 'tban'):
        message.reply_text("Invalid mode! Use ban, kick, mute, tmute, or tban.")
        return
    
    duration = None
    if mode in ('tmute', 'tban') and len(context.args) > 1:
        duration = context.args[1]
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.flood_mode = mode
    chat_settings.flood_action_duration = duration
    db.commit()
    
    text = f"✅ Flood punishment mode set to: {mode}"
    if duration:
        text += f" for {duration}"
    
    message.reply_text(text)

@is_group_chat
def flood(update: Update, context: CallbackContext):
    """Show current flood settings - /flood"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    limit = chat_settings.flood_limit or 3
    mode = chat_settings.flood_mode or 'mute'
    duration = chat_settings.flood_action_duration
    
    text = f"🛡 <b>Anti-Flood Settings for {chat.title}</b>\n\n"
    text += f"<b>Status:</b> {'ON' if chat_settings.antiflood_enabled else 'OFF'}\n"
    text += f"<b>Flood Limit:</b> {limit} messages\n"
    text += f"<b>Punishment:</b> {mode}"
    if duration:
        text += f" ({duration})"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

def check_flood(update: Update, context: CallbackContext):
    """Check if user is flooding"""
    if not update.effective_chat or not update.effective_message:
        return
    
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    if not user or user.is_bot:
        return
    
    # Skip admins
    try:
        member = chat.get_member(user.id)
        if member.status in ('administrator', 'creator'):
            return
    except Exception:
        return
    
    # Get settings
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings or not chat_settings.antiflood_enabled:
        return
    
    limit = chat_settings.flood_limit or 3
    mode = chat_settings.flood_mode or 'mute'
    duration = chat_settings.flood_action_duration
    
    # Track messages
    key = (chat.id, user.id)
    current_time = time.time()
    
    # Remove old timestamps outside the window
    flood_tracker[key] = [t for t in flood_tracker[key] if current_time - t < FLOOD_WINDOW]
    flood_tracker[key].append(current_time)
    
    # Check if flood limit exceeded
    if len(flood_tracker[key]) > limit:
        # Punish user
        try:
            if mode == 'ban':
                chat.ban_member(user.id)
                action_text = "banned"
            elif mode == 'kick':
                chat.ban_member(user.id)
                chat.unban_member(user.id)
                action_text = "kicked"
            elif mode == 'mute':
                permissions = ChatPermissions(can_send_messages=False)
                chat.restrict_member(user.id, permissions)
                action_text = "muted"
            elif mode in ('tmute', 'tban'):
                from datetime import datetime, timedelta
                dur = extract_time(duration) if duration else timedelta(hours=1)
                until_date = datetime.utcnow() + dur
                
                if mode == 'tmute':
                    permissions = ChatPermissions(can_send_messages=False)
                    chat.restrict_member(user.id, permissions, until_date=until_date)
                    action_text = f"temporarily muted ({duration or '1h'})"
                else:
                    chat.ban_member(user.id, until_date=until_date)
                    action_text = f"temporarily banned ({duration or '1h'})"
            else:
                permissions = ChatPermissions(can_send_messages=False)
                chat.restrict_member(user.id, permissions)
                action_text = "muted"
            
            # Delete flood messages
            for msg_id in flood_tracker[key]:
                try:
                    pass  # We don't track message IDs, so we can't delete
                except Exception:
                    pass
            
            # Clear tracker
            flood_tracker[key] = []
            
            message.reply_text(
                f"🛡 Anti-Flood: {mention_html(user.id, user.first_name)} has been {action_text} for flooding!",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

@is_group_chat
@user_admin_required
def floodhelp(update: Update, context: CallbackContext):
    text = """
*Anti-Flood Module:*

/setflood <number> - Set flood limit (0 to disable)
/setfloodmode <mode> [time] - Set punishment
/flood - Show current settings

Modes: ban, kick, mute, tmute, tban
Time: Xm, Xh, Xd, Xw (e.g., 30m, 2h, 1d)
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Anti-Flood"

HANDLERS = [
    CommandHandler("setflood", setflood),
    CommandHandler("setfloodmode", setfloodmode),
    CommandHandler("flood", flood),
    CommandHandler("floodhelp", floodhelp),
    MessageHandler(Filters.group & ~Filters.status_update & ~Filters.command, check_flood),
]
