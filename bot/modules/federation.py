"""
Federation module for Rose Bot
Handles cross-group ban management
"""

import json
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import is_owner, user_admin_required, is_group_chat
from bot.database import get_db, Federations, ChatFederations, add_chat
import secrets

def generate_fed_id():
    """Generate a unique federation ID"""
    return secrets.token_hex(16)

@is_group_chat
@user_admin_required
def newfed(update: Update, context: CallbackContext):
    """Create a new federation - /newfed <name>"""
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /newfed <federation_name>")
        return
    
    fed_name = " ".join(context.args)
    fed_id = generate_fed_id()
    owner_id = update.effective_user.id
    
    db = get_db()
    
    # Check if user already owns a federation
    existing = db.query(Federations).filter(Federations.owner_id == owner_id).first()
    if existing:
        message.reply_text("You already own a federation! Delete it first with /delfed.")
        return
    
    fed = Federations(
        fed_id=fed_id,
        owner_id=owner_id,
        fed_name=fed_name
    )
    db.add(fed)
    db.commit()
    
    message.reply_text(
        f"✅ Federation <b>{fed_name}</b> has been created!\n"
        f"Fed ID: <code>{fed_id}</code>\n\n"
        f"Use this ID to connect other groups with /joinfed",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
@user_admin_required
def delfed(update: Update, context: CallbackContext):
    """Delete federation - /delfed"""
    user_id = update.effective_user.id
    
    db = get_db()
    fed = db.query(Federations).filter(Federations.owner_id == user_id).first()
    
    if not fed:
        update.effective_message.reply_text("You don't own a federation!")
        return
    
    # Delete all chat connections
    db.query(ChatFederations).filter(ChatFederations.fed_id == fed.fed_id).delete()
    db.delete(fed)
    db.commit()
    
    update.effective_message.reply_text(f"✅ Federation <b>{fed.fed_name}</b> has been deleted!", parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def joinfed(update: Update, context: CallbackContext):
    """Join a federation - /joinfed <fed_id>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /joinfed <fed_id>")
        return
    
    fed_id = context.args[0]
    
    db = get_db()
    fed = db.query(Federations).filter(Federations.fed_id == fed_id).first()
    
    if not fed:
        message.reply_text("Invalid federation ID!")
        return
    
    # Remove existing connection
    existing = db.query(ChatFederations).filter(ChatFederations.chat_id == chat.id).first()
    if existing:
        db.delete(existing)
    
    connection = ChatFederations(
        chat_id=chat.id,
        fed_id=fed_id
    )
    db.add(connection)
    db.commit()
    
    message.reply_text(f"✅ This group has joined federation <b>{fed.fed_name}</b>!", parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def leavefed(update: Update, context: CallbackContext):
    """Leave federation - /leavefed"""
    chat = update.effective_chat
    
    db = get_db()
    connection = db.query(ChatFederations).filter(ChatFederations.chat_id == chat.id).first()
    
    if not connection:
        update.effective_message.reply_text("This group is not in any federation!")
        return
    
    fed = db.query(Federations).filter(Federations.fed_id == connection.fed_id).first()
    db.delete(connection)
    db.commit()
    
    update.effective_message.reply_text(f"✅ This group has left federation <b>{fed.fed_name}</b>!", parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def fpromote(update: Update, context: CallbackContext):
    """Promote a user to fed admin - /fpromote <user>"""
    message = update.effective_message
    user_id = update.effective_user.id
    
    if not context.args and not message.reply_to_message:
        message.reply_text("Usage: /fpromote <user>")
        return
    
    db = get_db()
    fed = db.query(Federations).filter(Federations.owner_id == user_id).first()
    
    if not fed:
        message.reply_text("You don't own a federation!")
        return
    
    # Get target user
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        try:
            target_id = int(context.args[0])
        except ValueError:
            message.reply_text("Invalid user ID!")
            return
    
    # Add to fed admins
    admins = fed.fed_admins.split(',') if fed.fed_admins else []
    if str(target_id) not in admins:
        admins.append(str(target_id))
        fed.fed_admins = ','.join(admins)
        db.commit()
    
    message.reply_text("✅ User has been promoted to federation admin!")

@is_group_chat
@user_admin_required
def fdemote(update: Update, context: CallbackContext):
    """Demote a fed admin - /fdemote <user>"""
    message = update.effective_message
    user_id = update.effective_user.id
    
    if not context.args and not message.reply_to_message:
        message.reply_text("Usage: /fdemote <user>")
        return
    
    db = get_db()
    fed = db.query(Federations).filter(Federations.owner_id == user_id).first()
    
    if not fed:
        message.reply_text("You don't own a federation!")
        return
    
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
    else:
        target_id = context.args[0]
    
    admins = fed.fed_admins.split(',') if fed.fed_admins else []
    if target_id in admins:
        admins.remove(target_id)
        fed.fed_admins = ','.join(admins) if admins else ""
        db.commit()
    
    message.reply_text("✅ User has been demoted from federation admin!")

@is_group_chat
@user_admin_required
def fban(update: Update, context: CallbackContext):
    """Ban a user across federation - /fban <user> [reason]"""
    message = update.effective_message
    user_id = update.effective_user.id
    
    if not context.args:
        message.reply_text("Usage: /fban <user_id> [reason]")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        message.reply_text("Invalid user ID!")
        return
    
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason"
    
    db = get_db()
    fed = db.query(Federations).filter(
        (Federations.owner_id == user_id) |
        (Federations.fed_admins.contains(str(user_id)))
    ).first()
    
    if not fed:
        message.reply_text("You are not a federation admin!")
        return
    
    # Add to fed bans
    bans = json.loads(fed.fed_bans) if fed.fed_bans else {}
    bans[str(target_id)] = reason
    fed.fed_bans = json.dumps(bans)
    db.commit()
    
    # Ban in all connected chats
    connections = db.query(ChatFederations).filter(ChatFederations.fed_id == fed.fed_id).all()
    banned_count = 0
    
    for conn in connections:
        try:
            context.bot.ban_chat_member(conn.chat_id, target_id)
            banned_count += 1
        except Exception:
            pass
    
    message.reply_text(
        f"🚫 <b>Fed Ban</b>\n"
        f"User ID: <code>{target_id}</code>\n"
        f"Reason: {reason}\n"
        f"Banned in {banned_count} groups",
        parse_mode=ParseMode.HTML
    )

@is_group_chat
@user_admin_required
def unfban(update: Update, context: CallbackContext):
    """Unban a user from federation - /unfban <user>"""
    message = update.effective_message
    user_id = update.effective_user.id
    
    if not context.args:
        message.reply_text("Usage: /unfban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        message.reply_text("Invalid user ID!")
        return
    
    db = get_db()
    fed = db.query(Federations).filter(
        (Federations.owner_id == user_id) |
        (Federations.fed_admins.contains(str(user_id)))
    ).first()
    
    if not fed:
        message.reply_text("You are not a federation admin!")
        return
    
    # Remove from fed bans
    bans = json.loads(fed.fed_bans) if fed.fed_bans else {}
    if str(target_id) in bans:
        del bans[str(target_id)]
        fed.fed_bans = json.dumps(bans)
        db.commit()
    
    # Unban in all connected chats
    connections = db.query(ChatFederations).filter(ChatFederations.fed_id == fed.fed_id).all()
    unbanned_count = 0
    
    for conn in connections:
        try:
            context.bot.unban_chat_member(conn.chat_id, target_id)
            unbanned_count += 1
        except Exception:
            pass
    
    message.reply_text(f"✅ User unbanned from {unbanned_count} groups in the federation!")

@is_group_chat
def fedinfo(update: Update, context: CallbackContext):
    """Show federation info - /fedinfo [fed_id]"""
    chat = update.effective_chat
    
    db = get_db()
    
    if context.args:
        fed_id = context.args[0]
        fed = db.query(Federations).filter(Federations.fed_id == fed_id).first()
    else:
        # Check if chat is in a federation
        connection = db.query(ChatFederations).filter(ChatFederations.chat_id == chat.id).first()
        if connection:
            fed = db.query(Federations).filter(Federations.fed_id == connection.fed_id).first()
        else:
            fed = None
    
    if not fed:
        update.effective_message.reply_text("No federation found!")
        return
    
    owner = context.bot.get_chat(fed.owner_id)
    admins = len(fed.fed_admins.split(',')) if fed.fed_admins else 0
    connections_count = db.query(ChatFederations).filter(ChatFederations.fed_id == fed.fed_id).count()
    bans = json.loads(fed.fed_bans) if fed.fed_bans else {}
    
    text = f"📢 <b>{fed.fed_name}</b>\n\n"
    text += f"<b>Owner:</b> {owner.first_name}\n"
    text += f"<b>Admins:</b> {admins}\n"
    text += f"<b>Groups:</b> {connections_count}\n"
    text += f"<b>Banned Users:</b> {len(bans)}\n"
    text += f"<b>Fed ID:</b> <code>{fed.fed_id}</code>"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
def fedadmins(update: Update, context: CallbackContext):
    """List federation admins - /fedadmins"""
    chat = update.effective_chat
    
    db = get_db()
    connection = db.query(ChatFederations).filter(ChatFederations.chat_id == chat.id).first()
    
    if not connection:
        update.effective_message.reply_text("This group is not in any federation!")
        return
    
    fed = db.query(Federations).filter(Federations.fed_id == connection.fed_id).first()
    
    text = f"👥 <b>Federation Admins of {fed.fed_name}</b>\n\n"
    
    owner = context.bot.get_chat(fed.owner_id)
    text += f"👑 Owner: {mention_html(owner.id, owner.first_name)}\n"
    
    if fed.fed_admins:
        for admin_id in fed.fed_admins.split(','):
            try:
                admin = context.bot.get_chat(int(admin_id))
                text += f"  • {mention_html(admin.id, admin.first_name)}\n"
            except Exception:
                text += f"  • Unknown User ({admin_id})\n"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

# Check fed bans on new members
def check_fed_ban(update: Update, context: CallbackContext):
    """Check if new member is fed banned"""
    chat = update.effective_chat
    
    for user in update.message.new_chat_members:
        db = get_db()
        connection = db.query(ChatFederations).filter(ChatFederations.chat_id == chat.id).first()
        
        if not connection:
            continue
        
        fed = db.query(Federations).filter(Federations.fed_id == connection.fed_id).first()
        if not fed or not fed.fed_bans:
            continue
        
        bans = json.loads(fed.fed_bans)
        if str(user.id) in bans:
            try:
                chat.ban_member(user.id)
                update.message.reply_text(
                    f"🚫 {mention_html(user.id, user.first_name)} is banned from the federation!\n"
                    f"Reason: {bans[str(user.id)]}",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass

@is_group_chat
def federationhelp(update: Update, context: CallbackContext):
    text = """
*Federation Module:*

/newfed <name> - Create a federation
/delfed - Delete your federation
/joinfed <fed_id> - Join a federation
/leavefed - Leave federation
/fpromote <user> - Promote fed admin
/fdemote <user> - Demote fed admin
/fban <user> [reason] - Fed ban
/unfban <user> - Remove fed ban
/fedinfo [fed_id] - Show federation info
/fedadmins - List fed admins

Federations allow you to share ban lists across multiple groups.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Federation"

HANDLERS = [
    CommandHandler("newfed", newfed),
    CommandHandler("delfed", delfed),
    CommandHandler("joinfed", joinfed),
    CommandHandler("leavefed", leavefed),
    CommandHandler("fpromote", fpromote),
    CommandHandler("fdemote", fdemote),
    CommandHandler("fban", fban),
    CommandHandler("unfban", unfban),
    CommandHandler("fedinfo", fedinfo),
    CommandHandler("fedadmins", fedadmins),
    CommandHandler("federationhelp", federationhelp),
]
