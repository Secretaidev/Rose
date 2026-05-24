"""
Approval module for Rose Bot
Handles approved users who are exempt from locks/antiflood/blacklist
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import user_admin_required, bot_admin_required, extract_user_and_text, is_group_chat
from bot.database import get_db, Users, add_user

@is_group_chat
@user_admin_required
def approve(update: Update, context: CallbackContext):
    """Approve a user - /approve <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("Usage: /approve <user>")
        return
    
    db = get_db()
    user = db.query(Users).filter(Users.user_id == user_id).first()
    
    if not user:
        try:
            member = chat.get_member(user_id)
            user = add_user(user_id, member.user.username, member.user.first_name, member.user.last_name)
            db.refresh(user)
        except Exception:
            user = add_user(user_id)
            db.refresh(user)
    
    user.approved = True
    db.commit()
    
    message.reply_text(
        f"✅ {mention_html(user_id, first_name or 'User')} has been approved!\n"
        f"They are now exempt from locks, antiflood, and blacklist.",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
@user_admin_required
def unapprove(update: Update, context: CallbackContext):
    """Unapprove a user - /unapprove <user>"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text("Usage: /unapprove <user>")
        return
    
    db = get_db()
    user = db.query(Users).filter(Users.user_id == user_id).first()
    
    if user:
        user.approved = False
        db.commit()
    
    message.reply_text(
        f"✅ {mention_html(user_id, first_name or 'User')} has been unapproved!",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
@user_admin_required
def unapproveall(update: Update, context: CallbackContext):
    """Unapprove all users - /unapproveall"""
    db = get_db()
    db.query(Users).update({Users.approved: False})
    db.commit()
    
    update.effective_message.reply_text("✅ All users have been unapproved!")

@is_group_chat
@user_admin_required
def approval(update: Update, context: CallbackContext):
    """Check approval status - /approval [user]"""
    chat = update.effective_chat
    message = update.effective_message
    user_id, first_name, _ = extract_user_and_text(update, context)
    
    if not user_id:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
    
    db = get_db()
    user = db.query(Users).filter(Users.user_id == user_id).first()
    
    status = "✅ Approved" if user and user.approved else "❌ Not approved"
    
    message.reply_text(
        f"Approval status for {mention_html(user_id, first_name or 'User')}: {status}",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
@user_admin_required
def approvedlist(update: Update, context: CallbackContext):
    """List approved users - /approval list"""
    chat = update.effective_chat
    
    db = get_db()
    approved_users = db.query(Users).filter(Users.approved == True).all()
    
    if not approved_users:
        update.effective_message.reply_text("No approved users!")
        return
    
    text = f"✅ <b>Approved Users in {chat.title}:</b>\n\n"
    for user in approved_users:
        name = user.first_name or user.username or f"User {user.user_id}"
        text += f" • {mention_html(user.user_id, name)}\n"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def approvalhelp(update: Update, context: CallbackContext):
    text = """
*Approval Module:*

/approve <user> - Approve a user
/unapprove <user> - Unapprove a user
/unapproveall - Unapprove all users
/approval [user] - Check approval status

Approved users are exempt from locks, antiflood, and blacklist checks.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Approval"

HANDLERS = [
    CommandHandler("approve", approve),
    CommandHandler("unapprove", unapprove),
    CommandHandler("unapproveall", unapproveall),
    CommandHandler("approval", approval),
    CommandHandler("approvedlist", approvedlist),
    CommandHandler("approvalhelp", approvalhelp),
]
