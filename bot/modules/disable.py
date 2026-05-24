"""
Command Disabling module for Rose Bot
Allows admins to disable specific commands
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import user_admin_required, is_group_chat
from bot.database import get_db, Chats, add_chat

ALL_COMMANDS = [
    'adminlist', 'approval', 'ban', 'blacklist', 'botinfo', 'captcha',
    'cleanwelcome', 'cleangoodbye', 'cleanservice', 'connect', 'connected',
    'disconnect', 'del', 'demote', 'dban', 'dkick', 'dmute', 'dwarn',
    'echo', 'fban', 'fedinfo', 'fban', 'unfban', 'filter', 'filters',
    'flood', 'goodbye', 'groupinfo', 'id', 'info', 'kick', 'lock', 'locks',
    'locktypes', 'lockwarns', 'mute', 'newfed', 'notes', 'pin', 'promote',
    'purge', 'purgefrom', 'purgeto', 'report', 'reports', 'resetwarn',
    'rules', 'save', 'setwelcome', 'setgoodbye', 'setflood', 'setfloodmode',
    'setrules', 'setwarnlimit', 'setwarnmode', 'sban', 'skick', 'smute',
    'stop', 'swarn', 'tban', 'tmute', 'unban', 'unlock', 'unmute', 'unpin',
    'unpinall', 'warn', 'warns', 'welcome'
]

@is_group_chat
@user_admin_required
def disable(update: Update, context: CallbackContext):
    """Disable a command - /disable <command>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "Usage: /disable <command>\n"
            "Use /disablelist to see disabled commands."
        )
        return
    
    command = context.args[0].lower().lstrip('/')
    
    if command not in ALL_COMMANDS:
        message.reply_text(f"Unknown command: {command}")
        return
    
    if command in ('disable', 'enable', 'disablelist'):
        message.reply_text("You can't disable command management commands!")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    disabled = chat_settings.disabled_commands.split(',') if chat_settings.disabled_commands else []
    
    if command in disabled:
        message.reply_text(f"Command /{command} is already disabled!")
        return
    
    disabled.append(command)
    chat_settings.disabled_commands = ','.join(disabled)
    db.commit()
    
    message.reply_text(f"✅ Command /{command} has been disabled!")

@is_group_chat
@user_admin_required
def enable(update: Update, context: CallbackContext):
    """Enable a command - /enable <command>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /enable <command>")
        return
    
    command = context.args[0].lower().lstrip('/')
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings or not chat_settings.disabled_commands:
        message.reply_text("No commands are disabled!")
        return
    
    disabled = chat_settings.disabled_commands.split(',')
    
    if command not in disabled:
        message.reply_text(f"Command /{command} is not disabled!")
        return
    
    disabled.remove(command)
    chat_settings.disabled_commands = ','.join(disabled) if disabled else ""
    db.commit()
    
    message.reply_text(f"✅ Command /{command} has been enabled!")

@is_group_chat
def disablelist(update: Update, context: CallbackContext):
    """List disabled commands - /disablelist"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings or not chat_settings.disabled_commands:
        update.effective_message.reply_text("No commands are disabled in this group!")
        return
    
    disabled = chat_settings.disabled_commands.split(',')
    
    text = "🚫 <b>Disabled Commands:</b>\n\n"
    for cmd in disabled:
        text += f"  • /{cmd}\n"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def disablehelp(update: Update, context: CallbackContext):
    text = """
*Disable Module:*

/disable <command> - Disable a command
/enable <command> - Enable a command
/disablelist - List disabled commands

Disabled commands will not work for regular users.
Admins can still use them.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Disable"

HANDLERS = [
    CommandHandler("disable", disable),
    CommandHandler("enable", enable),
    CommandHandler("disablelist", disablelist),
    CommandHandler("disablehelp", disablehelp),
]
