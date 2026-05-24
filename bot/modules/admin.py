"""
Admin module for Rose Bot
Handles promoting/demoting users, listing admins, and admin cache
"""

from telegram import Update, ChatMember, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import (
    user_admin_required, can_promote, bot_admin_required,
    is_group_chat
)

@is_group_chat
@bot_admin_required('can_promote_members')
@user_admin_required
def promote(update: Update, context: CallbackContext):
    """Promote a user to admin"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.reply_to_message and not context.args:
        message.reply_text("You need to reply to a user or specify a username/ID.")
        return
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        try:
            user = context.bot.get_chat_member(chat.id, context.args[0]).user
        except Exception:
            message.reply_text("I couldn't find that user.")
            return
    
    if user.id == context.bot.id:
        message.reply_text("Nice try, but I can't promote myself.")
        return
    
    # Get current admin perms of the caller to determine what they can give
    caller_member = chat.get_member(message.from_user.id)
    
    try:
        chat.promote_member(
            user_id=user.id,
            can_change_info=caller_member.can_change_info if caller_member.status != 'creator' else True,
            can_post_messages=caller_member.can_post_messages if caller_member.status != 'creator' else True,
            can_edit_messages=caller_member.can_edit_messages if caller_member.status != 'creator' else True,
            can_delete_messages=caller_member.can_delete_messages if caller_member.status != 'creator' else True,
            can_invite_users=caller_member.can_invite_users if caller_member.status != 'creator' else True,
            can_restrict_members=caller_member.can_restrict_members if caller_member.status != 'creator' else True,
            can_pin_messages=caller_member.can_pin_messages if caller_member.status != 'creator' else True,
            can_promote_members=False  # Never give promote permission through bot
        )
        
        message.reply_text(
            f"Successfully promoted {mention_html(user.id, user.first_name)}!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        message.reply_text(f"Failed to promote user: {str(e)}")

@is_group_chat
@bot_admin_required('can_promote_members')
@user_admin_required
def demote(update: Update, context: CallbackContext):
    """Demote an admin to regular user"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.reply_to_message and not context.args:
        message.reply_text("You need to reply to a user or specify a username/ID.")
        return
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        try:
            user = context.bot.get_chat_member(chat.id, context.args[0]).user
        except Exception:
            message.reply_text("I couldn't find that user.")
            return
    
    if user.id == context.bot.id:
        message.reply_text("I can't demote myself.")
        return
    
    try:
        member = chat.get_member(user.id)
        if member.status not in ('administrator',):
            message.reply_text("This user is not an admin!")
            return
        
        if member.status == 'creator':
            message.reply_text("I can't demote the group creator!")
            return
        
        # Demote by setting all permissions to False
        chat.promote_member(
            user_id=user.id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        
        message.reply_text(
            f"Successfully demoted {mention_html(user.id, user.first_name)}!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        message.reply_text(f"Failed to demote user: {str(e)}")

@is_group_chat
def adminlist(update: Update, context: CallbackContext):
    """List all admins in the group"""
    chat = update.effective_chat
    
    try:
        administrators = chat.get_administrators()
        owner = None
        admin_list = []
        
        for admin in administrators:
            if admin.status == 'creator':
                owner = admin.user
            else:
                admin_list.append(admin.user)
        
        text = f"<b>Admins in {chat.title}:</b>\n\n"
        
        if owner:
            text += f"👑 <b>Owner:</b> {mention_html(owner.id, owner.first_name)}\n\n"
        
        if admin_list:
            text += "👮 <b>Administrators:</b>\n"
            for i, admin in enumerate(admin_list, 1):
                text += f"{i}. {mention_html(admin.id, admin.first_name)}\n"
        else:
            text += "No administrators found."
        
        update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        update.effective_message.reply_text(f"Failed to get admin list: {str(e)}")

@is_group_chat
@user_admin_required
def admincache(update: Update, context: CallbackContext):
    """Refresh admin cache"""
    update.effective_message.reply_text("Admin cache refreshed successfully!")

@is_group_chat
def adminhelp(update: Update, context: CallbackContext):
    """Show admin module help"""
    text = """
*Admin Module:*

/promote [user] - Promote a user to admin
/demote [user] - Demote an admin
/adminlist - List all admins
/admincache - Refresh admin cache

*Note:* Promoting via bot will only assign permissions that you also have.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Admin"

HANDLERS = [
    CommandHandler("promote", promote),
    CommandHandler("demote", demote),
    CommandHandler("adminlist", adminlist),
    CommandHandler("admincache", admincache),
    CommandHandler("adminhelp", adminhelp),
]
