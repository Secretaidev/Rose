"""
Helper functions and decorators for Rose Bot
"""

import re
import time
import html
from functools import wraps
from datetime import datetime, timedelta
from telegram import Update, ChatMember, ParseMode
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html, escape_markdown
from bot.config import DEL_CMDS, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS
from bot.database import get_db, Chats, Users, ChatMembers, add_chat, add_user

# Admin check decorators
def is_owner(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text("This command is restricted to the bot owner.")
    return wrapper

def is_sudo(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == OWNER_ID or user.id in SUDO_USERS:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text("This command is restricted to sudo users.")
    return wrapper

def is_support(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == OWNER_ID or user.id in SUDO_USERS or user.id in SUPPORT_USERS:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text("This command is restricted to support users.")
    return wrapper

def is_whitelist(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == OWNER_ID or user.id in SUDO_USERS or user.id in SUPPORT_USERS or user.id in WHITELIST_USERS:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text("This command is restricted to whitelisted users.")
    return wrapper

def is_group_chat(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_chat.type in ['group', 'supergroup']:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text("This command can only be used in groups.")
    return wrapper

def bot_admin_required(permission=None):
    def decorator(func):
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
            chat = update.effective_chat
            bot_member = chat.get_member(context.bot.id)
            
            if not bot_member.status == 'administrator':
                update.effective_message.reply_text(
                    "I need to be an administrator to perform this action!"
                )
                return
            
            if permission and not getattr(bot_member, permission, False):
                update.effective_message.reply_text(
                    f"I don't have the necessary permission: {permission}!"
                )
                return
                
            return func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def user_admin_required(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status in ('administrator', 'creator'):
            return func(update, context, *args, **kwargs)
        
        if DEL_CMDS and update.effective_message:
            update.effective_message.delete()
        else:
            update.effective_message.reply_text(
                "You need to be an admin to use this command."
            )
    return wrapper

def user_admin_required_no_reply(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status in ('administrator', 'creator'):
            return func(update, context, *args, **kwargs)
    return wrapper

def can_restrict(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status == 'creator':
            return func(update, context, *args, **kwargs)
        if member.status == 'administrator' and member.can_restrict_members:
            return func(update, context, *args, **kwargs)
        
        update.effective_message.reply_text(
            "You need to have 'Restrict Members' admin permission to use this command."
        )
    return wrapper

def can_pin(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status == 'creator':
            return func(update, context, *args, **kwargs)
        if member.status == 'administrator' and member.can_pin_messages:
            return func(update, context, *args, **kwargs)
        
        update.effective_message.reply_text(
            "You need to have 'Pin Messages' admin permission to use this command."
        )
    return wrapper

def can_promote(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status == 'creator':
            return func(update, context, *args, **kwargs)
        if member.status == 'administrator' and member.can_promote_members:
            return func(update, context, *args, **kwargs)
        
        update.effective_message.reply_text(
            "You need to have 'Add Admins' permission to use this command."
        )
    return wrapper

def can_delete(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if user.id == OWNER_ID:
            return func(update, context, *args, **kwargs)
        
        member = chat.get_member(user.id)
        if member.status == 'creator':
            return func(update, context, *args, **kwargs)
        if member.status == 'administrator' and member.can_delete_messages:
            return func(update, context, *args, **kwargs)
        
        update.effective_message.reply_text(
            "You need to have 'Delete Messages' admin permission to use this command."
        )
    return wrapper

# Extract user from message
def extract_user(update: Update, context: CallbackContext):
    """Extract user from message (reply, mention, or user_id)"""
    message = update.effective_message
    user_id = None
    first_name = None
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        first_name = user.first_name
    elif len(context.args) >= 1:
        args = context.args[0]
        if args.startswith('@'):
            # Username
            username = args[1:]
            try:
                chat_member = context.bot.get_chat_member(update.effective_chat.id, args)
                user_id = chat_member.user.id
                first_name = chat_member.user.first_name
            except Exception:
                message.reply_text(f"I couldn't find user {args}.")
                return None, None
        else:
            try:
                user_id = int(args)
                try:
                    user = context.bot.get_chat(user_id)
                    first_name = user.first_name
                except Exception:
                    message.reply_text("I couldn't find that user.")
                    return None, None
            except ValueError:
                message.reply_text("Invalid user ID or username.")
                return None, None
    
    return user_id, first_name

def extract_user_and_text(update: Update, context: CallbackContext):
    """Extract user and reason text from message"""
    message = update.effective_message
    user_id = None
    first_name = None
    text = ""
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        first_name = user.first_name
        text = " ".join(context.args) if context.args else ""
    elif len(context.args) >= 1:
        args = context.args
        if args[0].startswith('@'):
            username = args[0]
            try:
                chat_member = context.bot.get_chat_member(update.effective_chat.id, username)
                user_id = chat_member.user.id
                first_name = chat_member.user.first_name
            except Exception:
                message.reply_text(f"I couldn't find user {username}.")
                return None, None, ""
            text = " ".join(args[1:])
        else:
            try:
                user_id = int(args[0])
                try:
                    user = context.bot.get_chat(user_id)
                    first_name = user.first_name
                except Exception:
                    message.reply_text("I couldn't find that user.")
                    return None, None, ""
            except ValueError:
                message.reply_text("Invalid user ID or username.")
                return None, None, ""
            text = " ".join(args[1:])
    
    return user_id, first_name, text

# Time parser for temporary bans/mutes
def extract_time(time_str):
    """Extract time from string like 30m, 2h, 1d, 1w"""
    if not time_str:
        return None
    
    unit = time_str[-1].lower()
    try:
        value = int(time_str[:-1])
    except ValueError:
        return None
    
    if unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'w':
        return timedelta(weeks=value)
    else:
        return None

def format_time(time_str):
    """Format time string to readable format"""
    if not time_str:
        return "forever"
    
    unit = time_str[-1].lower()
    try:
        value = int(time_str[:-1])
    except ValueError:
        return time_str
    
    units = {
        'm': 'minute(s)',
        'h': 'hour(s)',
        'd': 'day(s)',
        'w': 'week(s)'
    }
    
    return f"{value} {units.get(unit, time_str)}"

# Check if user is admin
def is_user_admin(chat, user_id):
    member = chat.get_member(user_id)
    return member.status in ('administrator', 'creator')

def is_bot_admin(chat, bot_id):
    member = chat.get_member(bot_id)
    return member.status == 'administrator'

# Welcome formatting
def welcome_formatting(text, user, chat):
    """Format welcome message with placeholders"""
    if not text:
        return text
    
    placeholders = {
        '{first}': user.first_name or '',
        '{last}': user.last_name or '',
        '{fullname}': f"{user.first_name or ''} {user.last_name or ''}".strip(),
        '{username}': f"@{user.username}" if user.username else user.first_name,
        '{mention}': mention_html(user.id, user.first_name),
        '{id}': str(user.id),
        '{chatname}': chat.title or 'this chat',
    }
    
    for placeholder, value in placeholders.items():
        text = text.replace(placeholder, value)
    
    return text

# Message type checkers
def is_url(text):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    return bool(url_pattern.search(text))

def is_email(text):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    return bool(email_pattern.search(text))

def is_phone(text):
    phone_pattern = re.compile(r'[\+]?[1-9]?[0-9]{7,15}')
    return bool(phone_pattern.search(text))

def has_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))

def has_chinese(text):
    chinese_pattern = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
    return bool(chinese_pattern.search(text))

def has_japanese(text):
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
    return bool(japanese_pattern.search(text))

def has_cyrillic(text):
    cyrillic_pattern = re.compile(r'[\u0400-\u04FF\u0500-\u052F]')
    return bool(cyrillic_pattern.search(text))

def is_command(text):
    return text.startswith('/') or text.startswith('!')

# Log action
def log_action(update, context, action, user, target=None, reason=None):
    """Log moderation actions"""
    chat = update.effective_chat
    admin = update.effective_user
    
    log_text = f"""
<b>Action:</b> {action}
<b>Chat:</b> {chat.title} (<code>{chat.id}</code>)
<b>Admin:</b> {mention_html(admin.id, admin.first_name)}
"""
    if target:
        log_text += f"<b>Target:</b> {mention_html(target.id, target.first_name)} (<code>{target.id}</code>)\n"
    if reason:
        log_text += f"<b>Reason:</b> {reason}"
    
    return log_text

# Send action to log channel
def send_log(update, context, action, user, target=None, reason=None):
    """Send log to log channel if configured"""
    from bot.config import MESSAGE_DUMP
    
    if MESSAGE_DUMP:
        log_text = log_action(update, context, action, user, target, reason)
        try:
            context.bot.send_message(MESSAGE_DUMP, log_text, parse_mode=ParseMode.HTML)
        except Exception:
            pass
