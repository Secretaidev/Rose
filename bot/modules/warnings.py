"""
Warnings module for Rose Bot
Handles warn, dwarn, swarn, resetwarn, warnings, setwarnlimit, setwarnmode
"""

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import (
    user_admin_required, can_restrict, bot_admin_required,
    extract_user_and_text, is_group_chat
)
from bot.database import get_db, Warnings, Chats

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def warn_user(update: Update, context: CallbackContext, silent=False, delete_message=False):
    """Core warning function"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to warn.")
        return
    
    # Don't warn admins
    try:
        member = chat.get_member(user_id)
        if member.status in ('administrator', 'creator'):
            message.reply_text("I can't warn administrators!")
            return
        first_name = member.user.first_name
    except Exception:
        pass
    
    # Get chat settings
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        from bot.database import add_chat
        chat_settings = add_chat(chat.id, chat.title)
        db.refresh(chat_settings)
    
    warn_limit = chat_settings.warn_limit or 3
    warn_mode = chat_settings.warn_mode or 'ban'
    
    # Add warning
    warning = Warnings(
        chat_id=chat.id,
        user_id=user_id,
        admin_id=message.from_user.id,
        reason=reason
    )
    db.add(warning)
    db.commit()
    
    # Count warnings
    warn_count = db.query(Warnings).filter(
        Warnings.chat_id == chat.id,
        Warnings.user_id == user_id
    ).count()
    
    if warn_count >= warn_limit:
        # Execute punishment
        if warn_mode == 'ban':
            try:
                chat.ban_member(user_id)
                action_text = "banned"
            except Exception:
                action_text = "failed to ban"
        elif warn_mode == 'kick':
            try:
                chat.ban_member(user_id)
                chat.unban_member(user_id)
                action_text = "kicked"
            except Exception:
                action_text = "failed to kick"
        elif warn_mode.startswith('tban'):
            from datetime import datetime, timedelta
            from bot.helpers import extract_time
            time_str = warn_mode.split(' ', 1)[1] if ' ' in warn_mode else '1d'
            duration = extract_time(time_str)
            if duration:
                until_date = datetime.utcnow() + duration
                chat.ban_member(user_id, until_date=until_date)
                action_text = f"temporarily banned ({time_str})"
            else:
                chat.ban_member(user_id)
                action_text = "banned"
        else:
            action_text = "banned"
        
        # Clear warnings after punishment
        db.query(Warnings).filter(
            Warnings.chat_id == chat.id,
            Warnings.user_id == user_id
        ).delete()
        db.commit()
        
        text = f"⚠️ {mention_html(user_id, first_name)} has reached {warn_limit} warnings and has been {action_text}!"
        if reason:
            text += f"\n<b>Last reason:</b> {reason}"
    else:
        text = f"⚠️ {mention_html(user_id, first_name)} has been warned ({warn_count}/{warn_limit})!"
        if reason:
            text += f"\n<b>Reason:</b> {reason}"
    
    if not silent:
        # Add remove warn button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Remove Warn", callback_data=f"rmwarn_{user_id}")]
        ]) if warn_count < warn_limit else None
        
        message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    
    if silent or delete_message:
        try:
            message.delete()
        except Exception:
            pass
    
    if delete_message and message.reply_to_message:
        try:
            message.reply_to_message.delete()
        except Exception:
            pass

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def warn(update: Update, context: CallbackContext):
    """Warn a user - /warn <user> [reason]"""
    warn_user(update, context)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def dwarn(update: Update, context: CallbackContext):
    """Delete message and warn - /dwarn (reply)"""
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("You need to reply to a message to use dwarn.")
        return
    warn_user(update, context, delete_message=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def swarn(update: Update, context: CallbackContext):
    """Silently warn a user - /swarn <user> [reason]"""
    warn_user(update, context, silent=True)

@is_group_chat
@can_restrict
def resetwarn(update: Update, context: CallbackContext):
    """Reset warnings for a user - /resetwarn <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to reset warnings for.")
        return
    
    try:
        member = chat.get_member(user_id)
        first_name = member.user.first_name
    except Exception:
        pass
    
    db = get_db()
    deleted = db.query(Warnings).filter(
        Warnings.chat_id == chat.id,
        Warnings.user_id == user_id
    ).delete()
    db.commit()
    
    message.reply_text(
        f"✅ Warnings for {mention_html(user_id, first_name or 'User')} have been reset!\n"
        f"Removed {deleted} warning(s).",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
def warns(update: Update, context: CallbackContext):
    """Show warnings for a user - /warns [user]"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
    else:
        try:
            member = chat.get_member(user_id)
            first_name = member.user.first_name
        except Exception:
            pass
    
    db = get_db()
    warnings = db.query(Warnings).filter(
        Warnings.chat_id == chat.id,
        Warnings.user_id == user_id
    ).all()
    
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    warn_limit = chat_settings.warn_limit if chat_settings else 3
    
    if not warnings:
        message.reply_text(
            f"✅ {mention_html(user_id, first_name or 'User')} has no warnings! (0/{warn_limit})",
            parse_mode=ParseMode.HTML
        )
        return
    
    text = f"⚠️ Warnings for {mention_html(user_id, first_name or 'User')}:\n\n"
    for i, warn in enumerate(warnings, 1):
        admin = context.bot.get_chat(warn.admin_id)
        text += f"{i}. By {admin.first_name}"
        if warn.reason:
            text += f" - {warn.reason}"
        text += "\n"
    
    text += f"\nTotal: {len(warnings)}/{warn_limit}"
    
    message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def setwarnlimit(update: Update, context: CallbackContext):
    """Set warning limit - /setwarnlimit <number>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args or not context.args[0].isdigit():
        message.reply_text("You need to specify a number!\nUsage: /setwarnlimit <number>")
        return
    
    limit = int(context.args[0])
    if limit < 1 or limit > 20:
        message.reply_text("Warning limit must be between 1 and 20!")
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        from bot.database import add_chat
        chat_settings = add_chat(chat.id, chat.title)
        db.refresh(chat_settings)
    
    chat_settings.warn_limit = limit
    db.commit()
    
    message.reply_text(f"✅ Warning limit has been set to {limit}!")

@is_group_chat
@user_admin_required
def setwarnmode(update: Update, context: CallbackContext):
    """Set warning punishment mode - /setwarnmode <kick/ban/tban time>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to specify a mode!\n"
            "Usage: /setwarnmode <kick/ban/tban time>\n\n"
            "Modes:\n"
            "kick - Kick user\n"
            "ban - Ban user\n"
            "tban - Temporarily ban (e.g., tban 1d)"
        )
        return
    
    mode = context.args[0].lower()
    
    if mode not in ('kick', 'ban', 'tban'):
        message.reply_text("Invalid mode! Use: kick, ban, or tban")
        return
    
    mode_value = mode
    if mode == 'tban' and len(context.args) > 1:
        mode_value = f"tban {context.args[1]}"
    elif mode == 'tban':
        mode_value = "tban 1d"
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        from bot.database import add_chat
        chat_settings = add_chat(chat.id, chat.title)
        db.refresh(chat_settings)
    
    chat_settings.warn_mode = mode_value
    db.commit()
    
    message.reply_text(f"✅ Warning mode has been set to: {mode_value}")

@is_group_chat
@user_admin_required
def warnings_settings(update: Update, context: CallbackContext):
    """Show current warning settings - /warnings"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if not chat_settings:
        from bot.database import add_chat
        chat_settings = add_chat(chat.id, chat.title)
        db.refresh(chat_settings)
    
    warn_limit = chat_settings.warn_limit or 3
    warn_mode = chat_settings.warn_mode or 'ban'
    
    text = f"⚠️ <b>Warning Settings for {chat.title}</b>\n\n"
    text += f"<b>Warn Limit:</b> {warn_limit}\n"
    text += f"<b>Warn Mode:</b> {warn_mode}\n\n"
    text += f"Users will be {warn_mode} after receiving {warn_limit} warnings."
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

def rmwarn_callback(update: Update, context: CallbackContext):
    """Handle remove warning callback"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    if data.startswith("rmwarn_"):
        user_id = int(data.split("_")[1])
        chat_id = update.effective_chat.id
        admin_id = update.effective_user.id
        
        # Check if admin
        try:
            member = context.bot.get_chat_member(chat_id, admin_id)
            if member.status not in ('administrator', 'creator'):
                query.edit_message_reply_markup(None)
                return
        except Exception:
            return
        
        db = get_db()
        # Get latest warning
        warning = db.query(Warnings).filter(
            Warnings.chat_id == chat_id,
            Warnings.user_id == user_id
        ).order_by(Warnings.created_at.desc()).first()
        
        if warning:
            db.delete(warning)
            db.commit()
            query.edit_message_reply_markup(None)
            query.answer("Warning removed!")
        else:
            query.answer("No warnings to remove!")

@is_group_chat
@user_admin_required
def warns_help(update: Update, context: CallbackContext):
    """Show warnings module help"""
    text = """
*Warnings Module:*

/warn <user> [reason] - Warn a user
/dwarn <reply> [reason] - Delete message & warn
/swarn <user> [reason] - Silently warn
/resetwarn <user> - Reset all warnings
/warns [user] - Show user warnings
/setwarnlimit <number> - Set max warnings (1-20)
/setwarnmode <mode> - Set punishment mode
/warnings - Show current warning settings

Modes: kick, ban, tban (e.g., tban 1d)
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Warnings"

HANDLERS = [
    CommandHandler("warn", warn),
    CommandHandler("dwarn", dwarn),
    CommandHandler("swarn", swarn),
    CommandHandler("resetwarn", resetwarn),
    CommandHandler("warns", warns),
    CommandHandler("setwarnlimit", setwarnlimit),
    CommandHandler("setwarnmode", setwarnmode),
    CommandHandler("warnings", warnings_settings),
    CommandHandler("warnshelp", warns_help),
    CallbackQueryHandler(rmwarn_callback, pattern=r"^rmwarn_"),
]
