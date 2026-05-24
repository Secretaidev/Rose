"""
Locks module for Rose Bot
Handles message type locks - URL, forward, bot, command, etc.
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import (
    user_admin_required, bot_admin_required, can_delete,
    is_url, is_email, is_phone, has_arabic, has_chinese, 
    has_japanese, has_cyrillic, is_group_chat
)
from bot.database import get_db, Chats, add_chat

LOCK_TYPES = {
    'url': 'lock_url',
    'link': 'lock_url',
    'forward': 'lock_forward',
    'bot': 'lock_bot',
    'command': 'lock_command',
    'cmd': 'lock_command',
    'contact': 'lock_contact',
    'location': 'lock_location',
    'email': 'lock_email',
    'phone': 'lock_phone',
    'game': 'lock_game',
    'inline': 'lock_inline',
    'media': 'lock_media',
    'sticker': 'lock_sticker',
    'rtl': 'lock_rtl',
    'arabic': 'lock_arabic',
    'chinese': 'lock_chinese',
    'japanese': 'lock_japanese',
    'cyrillic': 'lock_cyrillic',
}

LOCK_NAMES = {
    'url': 'URLs',
    'forward': 'Forwards',
    'bot': 'Bots',
    'command': 'Commands',
    'contact': 'Contacts',
    'location': 'Locations',
    'email': 'Emails',
    'phone': 'Phone numbers',
    'game': 'Games',
    'inline': 'Inline bots',
    'media': 'Media',
    'sticker': 'Stickers',
    'rtl': 'RTL text',
    'arabic': 'Arabic text',
    'chinese': 'Chinese text',
    'japanese': 'Japanese text',
    'cyrillic': 'Cyrillic text',
}

@is_group_chat
@bot_admin_required('can_delete_messages')
@user_admin_required
def lock(update: Update, context: CallbackContext):
    """Lock a message type - /lock <type>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to specify what to lock!\n\n"
            "Available lock types:\n"
            "url/link, forward, bot, command/cmd, contact, "
            "location, email, phone, game, inline, media, "
            "sticker, rtl, arabic, chinese, japanese, cyrillic\n\n"
            "Usage: /lock <type>"
        )
        return
    
    lock_type = context.args[0].lower()
    
    if lock_type not in LOCK_TYPES:
        message.reply_text(f"Invalid lock type: {lock_type}")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    setattr(chat_settings, LOCK_TYPES[lock_type], True)
    db.commit()
    
    message.reply_text(f"✅ {LOCK_NAMES.get(lock_type, lock_type)} has been locked!")

@is_group_chat
@bot_admin_required('can_delete_messages')
@user_admin_required
def unlock(update: Update, context: CallbackContext):
    """Unlock a message type - /unlock <type>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to specify what to unlock!\n\n"
            "Available types:\n"
            "url/link, forward, bot, command/cmd, contact, "
            "location, email, phone, game, inline, media, "
            "sticker, rtl, arabic, chinese, japanese, cyrillic\n\n"
            "Usage: /unlock <type>"
        )
        return
    
    lock_type = context.args[0].lower()
    
    if lock_type not in LOCK_TYPES:
        message.reply_text(f"Invalid lock type: {lock_type}")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    setattr(chat_settings, LOCK_TYPES[lock_type], False)
    db.commit()
    
    message.reply_text(f"✅ {LOCK_NAMES.get(lock_type, lock_type)} has been unlocked!")

@is_group_chat
def locks(update: Update, context: CallbackContext):
    """Show current locks - /locks"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    text = f"🔒 <b>Current Locks in {chat.title}</b>\n\n"
    
    locked_items = []
    unlocked_items = []
    
    for lock_type, attr_name in LOCK_TYPES.items():
        is_locked = getattr(chat_settings, attr_name, False)
        name = LOCK_NAMES.get(lock_type, lock_type)
        if is_locked:
            locked_items.append(name)
        else:
            unlocked_items.append(name)
    
    if locked_items:
        text += "<b>Locked:</b>\n"
        for item in locked_items:
            text += f"  🔴 {item}\n"
    else:
        text += "<b>Locked:</b> None\n"
    
    text += f"\n<i>Use /lock or /unlock to change settings</i>"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def locktypes(update: Update, context: CallbackContext):
    """Show available lock types - /locktypes"""
    text = "🔒 <b>Available Lock Types:</b>\n\n"
    for lock_type, name in LOCK_NAMES.items():
        text += f"  • {name} ({lock_type})\n"
    text += "\nUsage: /lock <type> or /unlock <type>"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
@bot_admin_required('can_delete_messages')
@user_admin_required
def lockwarns(update: Update, context: CallbackContext):
    """Toggle lock warnings - /lockwarns <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.lock_warns else "OFF"
        message.reply_text(f"Lock warnings are: {status}\nUse /lockwarns on/off")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.lock_warns = True
        db.commit()
        message.reply_text("✅ Lock warnings enabled! Users will be warned when violating locks.")
    elif setting in ('off', 'no', 'false'):
        chat_settings.lock_warns = False
        db.commit()
        message.reply_text("✅ Lock warnings disabled!")
    else:
        message.reply_text("Usage: /lockwarns on/off")

def check_locks(update: Update, context: CallbackContext):
    """Check and enforce locks on messages"""
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
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        return
    
    text = message.text or message.caption or ""
    should_delete = False
    lock_type = None
    
    # Check URL lock
    if chat_settings.lock_url and text and is_url(text):
        should_delete = True
        lock_type = 'url'
    
    # Check forward lock
    if chat_settings.lock_forward and message.forward_from or message.forward_from_chat:
        should_delete = True
        lock_type = 'forward'
    
    # Check command lock
    if chat_settings.lock_command and text and text.startswith('/'):
        should_delete = True
        lock_type = 'command'
    
    # Check email lock
    if chat_settings.lock_email and text and is_email(text):
        should_delete = True
        lock_type = 'email'
    
    # Check phone lock
    if chat_settings.lock_phone and text and is_phone(text):
        should_delete = True
        lock_type = 'phone'
    
    # Check Arabic lock
    if chat_settings.lock_arabic and text and has_arabic(text):
        should_delete = True
        lock_type = 'arabic'
    
    # Check Chinese lock
    if chat_settings.lock_chinese and text and has_chinese(text):
        should_delete = True
        lock_type = 'chinese'
    
    # Check Japanese lock
    if chat_settings.lock_japanese and text and has_japanese(text):
        should_delete = True
        lock_type = 'japanese'
    
    # Check Cyrillic lock
    if chat_settings.lock_cyrillic and text and has_cyrillic(text):
        should_delete = True
        lock_type = 'cyrillic'
    
    # Check media lock
    if chat_settings.lock_media and (message.photo or message.video or message.audio or message.document or message.voice):
        should_delete = True
        lock_type = 'media'
    
    # Check sticker lock
    if chat_settings.lock_sticker and message.sticker:
        should_delete = True
        lock_type = 'sticker'
    
    # Check game lock
    if chat_settings.lock_game and message.game:
        should_delete = True
        lock_type = 'game'
    
    # Check location lock
    if chat_settings.lock_location and (message.location or message.venue):
        should_delete = True
        lock_type = 'location'
    
    # Check contact lock
    if chat_settings.lock_contact and message.contact:
        should_delete = True
        lock_type = 'contact'
    
    # Check inline lock
    if chat_settings.lock_inline and message.via_bot:
        should_delete = True
        lock_type = 'inline'
    
    # Check RTL lock
    if chat_settings.lock_rtl and text:
        if '\u200F' in text or '\u202E' in text:
            should_delete = True
            lock_type = 'rtl'
    
    if should_delete and lock_type:
        try:
            message.delete()
            
            if chat_settings.lock_warns:
                context.bot.send_message(
                    chat.id,
                    f"🚫 {mention_html(user.id, user.first_name)}, {LOCK_NAMES.get(lock_type, lock_type)} is locked in this group!",
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            pass

# New chat members with bot check
def check_bot_lock(update: Update, context: CallbackContext):
    """Check if bots are locked when a new bot is added"""
    chat = update.effective_chat
    
    for user in update.message.new_chat_members:
        if user.is_bot and user.id != context.bot.id:
            db = get_db()
            chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
            
            if chat_settings and chat_settings.lock_bot:
                try:
                    chat.ban_member(user.id)
                    update.message.reply_text(
                        f"🤖 Bot {user.first_name} was removed because bots are locked in this group!"
                    )
                except Exception:
                    pass

@is_group_chat
@user_admin_required
def lockshelp(update: Update, context: CallbackContext):
    text = """
*Locks Module:*

/lock <type> - Lock a message type
/unlock <type> - Unlock a message type
/locks - Show current locks
/locktypes - Show available types
/lockwarns <on/off> - Toggle warnings

Types: url, forward, bot, command, contact, location, email, phone, game, inline, media, sticker, rtl, arabic, chinese, japanese, cyrillic
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Locks"

HANDLERS = [
    CommandHandler("lock", lock),
    CommandHandler("unlock", unlock),
    CommandHandler("locks", locks),
    CommandHandler("locktypes", locktypes),
    CommandHandler("lockwarns", lockwarns),
    CommandHandler("lockshelp", lockshelp),
    MessageHandler(Filters.group & ~Filters.status_update & ~Filters.command, check_locks),
    MessageHandler(Filters.status_update.new_chat_members, check_bot_lock),
]
