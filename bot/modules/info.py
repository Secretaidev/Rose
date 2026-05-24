"""
Info module for Rose Bot
Handles user info, chat info, and ID commands
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import is_group_chat
from bot.database import get_db, Warnings, Chats

@is_group_chat
def info(update: Update, context: CallbackContext):
    """Get user info - /info [user]"""
    chat = update.effective_chat
    message = update.effective_message
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif context.args:
        try:
            if context.args[0].startswith('@'):
                user = context.bot.get_chat_member(chat.id, context.args[0]).user
            else:
                user = context.bot.get_chat(int(context.args[0]))
        except Exception:
            message.reply_text("Could not find that user.")
            return
    else:
        user = message.from_user
    
    # Get warns count
    db = get_db()
    warn_count = db.query(Warnings).filter(
        Warnings.chat_id == chat.id,
        Warnings.user_id == user.id
    ).count()
    
    text = f"📋 <b>User Info:</b>\n\n"
    text += f"<b>ID:</b> <code>{user.id}</code>\n"
    text += f"<b>First Name:</b> {user.first_name}\n"
    if user.last_name:
        text += f"<b>Last Name:</b> {user.last_name}\n"
    if user.username:
        text += f"<b>Username:</b> @{user.username}\n"
    text += f"<b>Mention:</b> {mention_html(user.id, user.first_name)}\n"
    text += f"<b>Bot:</b> {'Yes' if user.is_bot else 'No'}\n"
    text += f"<b>Warnings:</b> {warn_count}\n"
    
    # Get chat member status
    try:
        member = chat.get_member(user.id)
        text += f"<b>Status:</b> {member.status.capitalize()}\n"
    except Exception:
        pass
    
    # Add profile picture count
    try:
        photos = user.get_profile_photos().total_count
        text += f"<b>Profile Photos:</b> {photos}\n"
    except Exception:
        pass
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def id_command(update: Update, context: CallbackContext):
    """Get IDs - /id"""
    chat = update.effective_chat
    message = update.effective_message
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        text = f"<b>User ID:</b> <code>{user.id}</code>\n"
        text += f"<b>Chat ID:</b> <code>{chat.id}</code>\n"
        if message.reply_to_message.forward_from:
            text += f"<b>Forwarded From ID:</b> <code>{message.reply_to_message.forward_from.id}</code>"
    else:
        text = f"<b>Chat ID:</b> <code>{chat.id}</code>\n"
        text += f"<b>Your ID:</b> <code>{message.from_user.id}</code>"
    
    message.reply_text(text, parse_mode=ParseMode.HTML)

def private_info(update: Update, context: CallbackContext):
    """Show info in private chat"""
    user = update.effective_user
    
    text = f"📋 <b>Your Info:</b>\n\n"
    text += f"<b>ID:</b> <code>{user.id}</code>\n"
    text += f"<b>First Name:</b> {user.first_name}\n"
    if user.last_name:
        text += f"<b>Last Name:</b> {user.last_name}\n"
    if user.username:
        text += f"<b>Username:</b> @{user.username}\n"
    text += f"<b>Language:</b> {user.language_code or 'Unknown'}\n"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def groupinfo(update: Update, context: CallbackContext):
    """Get group info - /groupinfo"""
    chat = update.effective_chat
    
    members_count = context.bot.get_chat_members_count(chat.id)
    
    text = f"📊 <b>Group Info:</b>\n\n"
    text += f"<b>Name:</b> {chat.title}\n"
    text += f"<b>ID:</b> <code>{chat.id}</code>\n"
    text += f"<b>Type:</b> {chat.type}\n"
    text += f"<b>Members:</b> {members_count}\n"
    
    if chat.username:
        text += f"<b>Link:</b> @{chat.username}\n"
    if chat.description:
        text += f"<b>Description:</b> {chat.description}\n"
    
    if chat.linked_chat_id:
        text += f"<b>Linked Chat ID:</b> <code>{chat.linked_chat_id}</code>\n"
    
    if chat.slow_mode_delay:
        text += f"<b>Slow Mode:</b> {chat.slow_mode_delay}s\n"
    
    text += f"<b>Permissions:</b>\n"
    if chat.permissions:
        perms = chat.permissions
        text += f"  • Send Messages: {'Yes' if perms.can_send_messages else 'No'}\n"
        text += f"  • Send Media: {'Yes' if perms.can_send_media_messages else 'No'}\n"
        text += f"  • Send Polls: {'Yes' if perms.can_send_polls else 'No'}\n"
        text += f"  • Add Previews: {'Yes' if perms.can_add_web_page_previews else 'No'}\n"
        text += f"  • Change Info: {'Yes' if perms.can_change_info else 'No'}\n"
        text += f"  • Invite Users: {'Yes' if perms.can_invite_users else 'No'}\n"
        text += f"  • Pin Messages: {'Yes' if perms.can_pin_messages else 'No'}"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def admins(update: Update, context: CallbackContext):
    """List admins - /admins"""
    chat = update.effective_chat
    
    administrators = chat.get_administrators()
    
    text = f"👮 <b>Admins in {chat.title}:</b>\n\n"
    for admin in administrators:
        if admin.status == 'creator':
            text += f"👑 {mention_html(admin.user.id, admin.user.first_name)} (Owner)\n"
        else:
            text += f"  • {mention_html(admin.user.id, admin.user.first_name)}\n"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def botinfo(update: Update, context: CallbackContext):
    """Show bot info - /botinfo"""
    me = context.bot.get_me()
    
    text = f"🤖 <b>Bot Info:</b>\n\n"
    text += f"<b>Name:</b> {me.first_name}\n"
    text += f"<b>ID:</b> <code>{me.id}</code>\n"
    text += f"<b>Username:</b> @{me.username}\n"
    text += f"<b>Version:</b> 1.0.0\n"
    text += f"<b>Library:</b> python-telegram-bot\n"
    text += f"<b>Language:</b> Python 3"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

def infohelp(update: Update, context: CallbackContext):
    text = """
*Info Module:*

/info [user] - Show user info
/id - Show IDs
/groupinfo - Show group info
/admins - List admins
/botinfo - Show bot info

Also works in private chat with /info.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Info"

HANDLERS = [
    CommandHandler("info", info),
    CommandHandler("id", id_command),
    CommandHandler("groupinfo", groupinfo),
    CommandHandler("admins", admins),
    CommandHandler("botinfo", botinfo),
    CommandHandler("infohelp", infohelp),
]
