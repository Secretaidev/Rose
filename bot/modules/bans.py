"""
Bans module for Rose Bot
Handles ban, tban, dban, sban, mute, tmute, dmute, smute, kick, dkick, skick
"""

import time
from datetime import datetime
from telegram import Update, ChatPermissions, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import (
    user_admin_required, can_restrict, bot_admin_required,
    extract_user_and_text, extract_time, is_group_chat,
    send_log, welcome_formatting
)
from bot.database import get_db, Bans

def ban_user(update: Update, context: CallbackContext, silent=False, delete_message=False, temp=False):
    """Core ban function handling all ban variants"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to ban.")
        return
    
    # Check if trying to ban admin or bot
    try:
        member = chat.get_member(user_id)
        if member.status in ('administrator', 'creator'):
            message.reply_text("I can't ban administrators!")
            return
        if member.user.id == context.bot.id:
            message.reply_text("Nice try, but I won't ban myself.")
            return
    except Exception:
        pass
    
    # Handle temp ban
    duration = None
    if temp and reason:
        parts = reason.split(maxsplit=1)
        duration = extract_time(parts[0])
        if duration:
            reason = parts[1] if len(parts) > 1 else ""
    
    try:
        if duration:
            until_date = datetime.utcnow() + duration
            chat.ban_member(user_id, until_date=until_date)
            time_text = f" for {reason.split()[0] if reason else 'specified time'}"
        else:
            chat.ban_member(user_id)
            time_text = " permanently"
        
        # Log action
        log_text = f"🚫 <b>Ban</b>\n"
        log_text += f"<b>User:</b> {mention_html(user_id, first_name or 'Unknown')}\n"
        log_text += f"<b>Admin:</b> {mention_html(message.from_user.id, message.from_user.first_name)}\n"
        if reason:
            log_text += f"<b>Reason:</b> {reason}\n"
        if duration:
            log_text += f"<b>Duration:</b> {reason.split()[0] if reason else 'specified time'}"
        
        # Store in database
        db = get_db()
        ban = Bans(
            chat_id=chat.id,
            user_id=user_id,
            admin_id=message.from_user.id,
            reason=reason,
            ban_type='ban',
            duration=str(duration) if duration else None
        )
        db.add(ban)
        db.commit()
        
        if not silent:
            message.reply_text(log_text, parse_mode=ParseMode.HTML)
        
        # Delete command message if silent or delete mode
        if silent or delete_message:
            try:
                message.delete()
            except Exception:
                pass
        
        # Delete replied message if in delete mode
        if delete_message and message.reply_to_message:
            try:
                message.reply_to_message.delete()
            except Exception:
                pass
                
    except Exception as e:
        message.reply_text(f"Failed to ban user: {str(e)}")

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def ban(update: Update, context: CallbackContext):
    """Ban a user permanently - /ban"""
    ban_user(update, context)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def tban(update: Update, context: CallbackContext):
    """Temporarily ban a user - /tban <user> <time> [reason]"""
    ban_user(update, context, temp=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def dban(update: Update, context: CallbackContext):
    """Delete message and ban user - /dban (reply)"""
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("You need to reply to a message to use dban.")
        return
    ban_user(update, context, delete_message=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def sban(update: Update, context: CallbackContext):
    """Silently ban a user - /sban"""
    ban_user(update, context, silent=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def unban(update: Update, context: CallbackContext):
    """Unban a user - /unban <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to unban.")
        return
    
    try:
        chat.unban_member(user_id)
        message.reply_text(
            f"✅ {mention_html(user_id, first_name or 'User')} has been unbanned!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        message.reply_text(f"Failed to unban user: {str(e)}")

def mute_user(update: Update, context: CallbackContext, silent=False, delete_message=False, temp=False):
    """Core mute function handling all mute variants"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to mute.")
        return
    
    # Check if trying to mute admin or bot
    try:
        member = chat.get_member(user_id)
        if member.status in ('administrator', 'creator'):
            message.reply_text("I can't mute administrators!")
            return
        if member.user.id == context.bot.id:
            message.reply_text("I won't mute myself.")
            return
    except Exception:
        pass
    
    # Handle temp mute
    duration = None
    if temp and reason:
        parts = reason.split(maxsplit=1)
        duration = extract_time(parts[0])
        if duration:
            reason = parts[1] if len(parts) > 1 else ""
    
    try:
        permissions = ChatPermissions(can_send_messages=False)
        
        if duration:
            until_date = datetime.utcnow() + duration
            chat.restrict_member(user_id, permissions, until_date=until_date)
            time_text = f" for {reason.split()[0] if reason else 'specified time'}"
        else:
            chat.restrict_member(user_id, permissions)
            time_text = " permanently"
        
        log_text = f"🔇 <b>Mute</b>\n"
        log_text += f"<b>User:</b> {mention_html(user_id, first_name or 'Unknown')}\n"
        log_text += f"<b>Admin:</b> {mention_html(message.from_user.id, message.from_user.first_name)}\n"
        if reason:
            log_text += f"<b>Reason:</b> {reason}\n"
        if duration:
            log_text += f"<b>Duration:</b> {reason.split()[0] if reason else 'specified time'}"
        
        if not silent:
            message.reply_text(log_text, parse_mode=ParseMode.HTML)
        
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
                
    except Exception as e:
        message.reply_text(f"Failed to mute user: {str(e)}")

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def mute(update: Update, context: CallbackContext):
    """Mute a user permanently - /mute"""
    mute_user(update, context)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def tmute(update: Update, context: CallbackContext):
    """Temporarily mute a user - /tmute <user> <time> [reason]"""
    mute_user(update, context, temp=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def dmute(update: Update, context: CallbackContext):
    """Delete message and mute user - /dmute (reply)"""
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("You need to reply to a message to use dmute.")
        return
    mute_user(update, context, delete_message=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def smute(update: Update, context: CallbackContext):
    """Silently mute a user - /smute"""
    mute_user(update, context, silent=True)

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def unmute(update: Update, context: CallbackContext):
    """Unmute a user - /unmute <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to unmute.")
        return
    
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        )
        chat.restrict_member(user_id, permissions)
        message.reply_text(
            f"🔊 {mention_html(user_id, first_name or 'User')} has been unmuted!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        message.reply_text(f"Failed to unmute user: {str(e)}")

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def kick(update: Update, context: CallbackContext):
    """Kick a user from the group - /kick <user> [reason]"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to kick.")
        return
    
    try:
        member = chat.get_member(user_id)
        if member.status in ('administrator', 'creator'):
            message.reply_text("I can't kick administrators!")
            return
        if member.user.id == context.bot.id:
            message.reply_text("I won't kick myself.")
            return
    except Exception:
        pass
    
    try:
        chat.ban_member(user_id)
        chat.unban_member(user_id)
        
        log_text = f"👢 <b>Kick</b>\n"
        log_text += f"<b>User:</b> {mention_html(user_id, first_name or 'Unknown')}\n"
        log_text += f"<b>Admin:</b> {mention_html(message.from_user.id, message.from_user.first_name)}\n"
        if reason:
            log_text += f"<b>Reason:</b> {reason}"
        
        message.reply_text(log_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        message.reply_text(f"Failed to kick user: {str(e)}")

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def dkick(update: Update, context: CallbackContext):
    """Delete message and kick user - /dkick (reply)"""
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("You need to reply to a message to use dkick.")
        return
    
    chat = update.effective_chat
    message = update.effective_message
    user = message.reply_to_message.from_user
    
    try:
        member = chat.get_member(user.id)
        if member.status in ('administrator', 'creator'):
            message.reply_text("I can't kick administrators!")
            return
    except Exception:
        pass
    
    try:
        chat.ban_member(user.id)
        chat.unban_member(user.id)
        
        log_text = f"👢 <b>Kick</b>\n"
        log_text += f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
        log_text += f"<b>Admin:</b> {mention_html(message.from_user.id, message.from_user.first_name)}"
        
        message.reply_text(log_text, parse_mode=ParseMode.HTML)
        
        try:
            message.reply_to_message.delete()
            message.delete()
        except Exception:
            pass
    except Exception as e:
        message.reply_text(f"Failed to kick user: {str(e)}")

@is_group_chat
@bot_admin_required('can_restrict_members')
@can_restrict
def skick(update: Update, context: CallbackContext):
    """Silently kick a user - /skick <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("You need to specify a user to kick.")
        return
    
    try:
        chat.ban_member(user_id)
        chat.unban_member(user_id)
        
        try:
            message.delete()
        except Exception:
            pass
    except Exception as e:
        message.reply_text(f"Failed to kick user: {str(e)}")

@is_group_chat
@user_admin_required
def bans_help(update: Update, context: CallbackContext):
    """Show bans module help"""
    text = """
*Bans Module:*

/ban <user> [reason] - Ban a user
/tban <user> <time> [reason] - Temporarily ban (e.g., 30m, 2h, 1d, 1w)
/dban <reply> [reason] - Delete message & ban user
/sban <user> [reason] - Silently ban user
/unban <user> - Unban a user

/mute <user> [reason] - Mute a user
/tmute <user> <time> [reason] - Temporarily mute
/dmute <reply> [reason] - Delete message & mute user
/smute <user> [reason] - Silently mute user
/unmute <user> - Unmute a user

/kick <user> [reason] - Kick a user
/dkick <reply> [reason] - Delete message & kick
/skick <user> [reason] - Silently kick

Time formats: Xm (minutes), Xh (hours), Xd (days), Xw (weeks)
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Bans"

HANDLERS = [
    CommandHandler("ban", ban),
    CommandHandler("tban", tban),
    CommandHandler("dban", dban),
    CommandHandler("sban", sban),
    CommandHandler("unban", unban),
    CommandHandler("mute", mute),
    CommandHandler("tmute", tmute),
    CommandHandler("dmute", dmute),
    CommandHandler("smute", smute),
    CommandHandler("unmute", unmute),
    CommandHandler("kick", kick),
    CommandHandler("dkick", dkick),
    CommandHandler("skick", skick),
    CommandHandler("banshelp", bans_help),
]
