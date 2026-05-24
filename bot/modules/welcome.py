"""
Welcome/Goodbye module for Rose Bot
Handles welcome messages, goodbye messages, and CAPTCHA verification
"""

import random
import string
from telegram import (
    Update, ParseMode, ChatPermissions, 
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CallbackContext, CommandHandler, MessageHandler, 
    CallbackQueryHandler, Filters, ChatMemberHandler
)
from telegram.utils.helpers import mention_html
from bot.helpers import user_admin_required, bot_admin_required, is_group_chat, welcome_formatting
from bot.database import get_db, Chats, WelcomeCaptcha, add_chat

# Generate CAPTCHA
def generate_captcha():
    """Generate a simple text CAPTCHA"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def greet_new_member(update: Update, context: CallbackContext):
    """Handle new member joins"""
    chat = update.effective_chat
    
    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            # Bot was added to group
            add_chat(chat.id, chat.title, chat.type)
            update.message.reply_text(
                f"Hi everyone! Thanks for adding me to {chat.title}!\n"
                f"Make me an admin with these permissions:\n"
                f"• Delete messages\n"
                f"• Restrict members\n"
                f"• Pin messages\n"
                f"• Invite users\n\n"
                f"Use /help to see available commands!"
            )
            return
        
        # Get chat settings
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        
        if not chat_settings:
            chat_settings = add_chat(chat.id, chat.title, chat.type)
            db.refresh(chat_settings)
        
        # CAPTCHA check
        if chat_settings.captcha_enabled:
            captcha_code = generate_captcha()
            
            # Mute user until CAPTCHA is solved
            permissions = ChatPermissions(can_send_messages=False)
            try:
                context.bot.restrict_chat_member(chat.id, user.id, permissions)
            except Exception:
                pass
            
            # Store CAPTCHA
            captcha_entry = WelcomeCaptcha(
                chat_id=chat.id,
                user_id=user.id,
                captcha_message=captcha_code
            )
            db.add(captcha_entry)
            db.commit()
            
            # Send CAPTCHA message
            buttons = []
            for i in range(0, 4):
                row = []
                for j in range(2):
                    code = generate_captcha()
                    if i == 0 and j == 0:
                        code = captcha_code
                    row.append(InlineKeyboardButton(code, callback_data=f"captcha_{user.id}_{code}"))
                buttons.append(row)
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            captcha_msg = update.message.reply_text(
                f"Welcome {mention_html(user.id, user.first_name)}!\n\n"
                f"Please click the correct code to verify: <b>{captcha_code}</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Update with message_id
            captcha_entry.message_id = captcha_msg.message_id
            db.commit()
        
        # Send welcome message
        if chat_settings.welcome_enabled and chat_settings.welcome_message:
            welcome_msg = welcome_formatting(chat_settings.welcome_message, user, chat)
            update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
        elif chat_settings.welcome_enabled:
            update.message.reply_text(
                f"Welcome {mention_html(user.id, user.first_name)} to {chat.title}!",
                parse_mode=ParseMode.HTML
            )

def say_goodbye(update: Update, context: CallbackContext):
    """Handle member leaves"""
    chat = update.effective_chat
    user = update.message.left_chat_member
    
    if user.id == context.bot.id:
        return
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if chat_settings and chat_settings.goodbye_enabled and chat_settings.goodbye_message:
        goodbye_msg = welcome_formatting(chat_settings.goodbye_message, user, chat)
        update.message.reply_text(goodbye_msg, parse_mode=ParseMode.HTML)
    elif chat_settings and chat_settings.goodbye_enabled:
        update.message.reply_text(
            f"Goodbye {mention_html(user.id, user.first_name)}! We'll miss you!",
            parse_mode=ParseMode.HTML
        )

def captcha_callback(update: Update, context: CallbackContext):
    """Handle CAPTCHA verification"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    if not data.startswith("captcha_"):
        return
    
    parts = data.split("_")
    if len(parts) != 3:
        return
    
    target_user_id = int(parts[1])
    clicked_code = parts[2]
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Only target user can click
    if user_id != target_user_id:
        query.answer("This CAPTCHA is not for you!")
        return
    
    db = get_db()
    captcha_entry = db.query(WelcomeCaptcha).filter(
        WelcomeCaptcha.chat_id == chat_id,
        WelcomeCaptcha.user_id == user_id
    ).first()
    
    if not captcha_entry:
        query.answer("CAPTCHA expired!")
        return
    
    if clicked_code == captcha_entry.captcha_message:
        # Correct! Unmute user
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
        
        try:
            context.bot.restrict_chat_member(chat_id, user_id, permissions)
        except Exception:
            pass
        
        # Delete CAPTCHA message
        try:
            context.bot.delete_message(chat_id, captcha_entry.message_id)
        except Exception:
            pass
        
        # Remove from DB
        db.delete(captcha_entry)
        db.commit()
        
        query.answer("✅ Verification successful! You can now chat.")
        
        # Send success message
        context.bot.send_message(
            chat_id,
            f"✅ {mention_html(user_id, update.effective_user.first_name)} has been verified!",
            parse_mode=ParseMode.HTML
        )
    else:
        # Wrong code
        query.answer("❌ Wrong code! Try again.")

@is_group_chat
@user_admin_required
def welcome(update: Update, context: CallbackContext):
    """Toggle welcome messages - /welcome <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.welcome_enabled else "OFF"
        message.reply_text(f"Welcome messages are currently: {status}\n\nUse /welcome on/off to toggle.")
        return
    
    setting = context.args[0].lower()
    
    if setting in ('on', 'yes', 'true'):
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        if not chat_settings:
            chat_settings = add_chat(chat.id, chat.title, chat.type)
            db.refresh(chat_settings)
        chat_settings.welcome_enabled = True
        db.commit()
        message.reply_text("✅ Welcome messages have been enabled!")
    elif setting in ('off', 'no', 'false'):
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        if not chat_settings:
            chat_settings = add_chat(chat.id, chat.title, chat.type)
            db.refresh(chat_settings)
        chat_settings.welcome_enabled = False
        db.commit()
        message.reply_text("✅ Welcome messages have been disabled!")
    else:
        message.reply_text("Usage: /welcome on/off")

@is_group_chat
@user_admin_required
def setwelcome(update: Update, context: CallbackContext):
    """Set welcome message - /setwelcome <message>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args and not message.reply_to_message:
        message.reply_text(
            "You need to provide a welcome message!\n\n"
            "Available placeholders:\n"
            "{first} - User's first name\n"
            "{last} - User's last name\n"
            "{fullname} - Full name\n"
            "{username} - Username\n"
            "{mention} - Mention user\n"
            "{id} - User ID\n"
            "{chatname} - Group name"
        )
        return
    
    if message.reply_to_message:
        welcome_msg = message.reply_to_message.text
    else:
        welcome_msg = " ".join(context.args)
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.welcome_message = welcome_msg
    chat_settings.welcome_enabled = True
    db.commit()
    
    message.reply_text("✅ Welcome message has been set!")

@is_group_chat
@user_admin_required
def resetwelcome(update: Update, context: CallbackContext):
    """Reset welcome message to default - /resetwelcome"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if chat_settings:
        chat_settings.welcome_message = None
        db.commit()
    
    update.effective_message.reply_text("✅ Welcome message has been reset to default!")

@is_group_chat
@user_admin_required
def goodbye(update: Update, context: CallbackContext):
    """Toggle goodbye messages - /goodbye <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.goodbye_enabled else "OFF"
        message.reply_text(f"Goodbye messages are currently: {status}\n\nUse /goodbye on/off to toggle.")
        return
    
    setting = context.args[0].lower()
    
    if setting in ('on', 'yes', 'true'):
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        if not chat_settings:
            chat_settings = add_chat(chat.id, chat.title, chat.type)
            db.refresh(chat_settings)
        chat_settings.goodbye_enabled = True
        db.commit()
        message.reply_text("✅ Goodbye messages have been enabled!")
    elif setting in ('off', 'no', 'false'):
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        if not chat_settings:
            chat_settings = add_chat(chat.id, chat.title, chat.type)
            db.refresh(chat_settings)
        chat_settings.goodbye_enabled = False
        db.commit()
        message.reply_text("✅ Goodbye messages have been disabled!")
    else:
        message.reply_text("Usage: /goodbye on/off")

@is_group_chat
@user_admin_required
def setgoodbye(update: Update, context: CallbackContext):
    """Set goodbye message - /setgoodbye <message>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args and not message.reply_to_message:
        message.reply_text(
            "You need to provide a goodbye message!\n\n"
            "Available placeholders:\n"
            "{first}, {last}, {fullname}, {username}, {mention}, {id}, {chatname}"
        )
        return
    
    if message.reply_to_message:
        goodbye_msg = message.reply_to_message.text
    else:
        goodbye_msg = " ".join(context.args)
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.goodbye_message = goodbye_msg
    chat_settings.goodbye_enabled = True
    db.commit()
    
    message.reply_text("✅ Goodbye message has been set!")

@is_group_chat
@user_admin_required
def resetgoodbye(update: Update, context: CallbackContext):
    """Reset goodbye message - /resetgoodbye"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if chat_settings:
        chat_settings.goodbye_message = None
        db.commit()
    
    update.effective_message.reply_text("✅ Goodbye message has been reset!")

@is_group_chat
@user_admin_required
def welcomemute(update: Update, context: CallbackContext):
    """Toggle welcome mute - /welcomemute <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.welcome_mute else "OFF"
        message.reply_text(f"Welcome mute is currently: {status}\n\nUse /welcomemute on/off to toggle.")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.welcome_mute = True
        db.commit()
        message.reply_text("✅ Welcome mute has been enabled! New members will be muted until they verify.")
    elif setting in ('off', 'no', 'false'):
        chat_settings.welcome_mute = False
        db.commit()
        message.reply_text("✅ Welcome mute has been disabled!")
    else:
        message.reply_text("Usage: /welcomemute on/off")

@is_group_chat
@user_admin_required
def captcha(update: Update, context: CallbackContext):
    """Toggle CAPTCHA - /captcha <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.captcha_enabled else "OFF"
        message.reply_text(f"CAPTCHA is currently: {status}\n\nUse /captcha on/off to toggle.")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.captcha_enabled = True
        db.commit()
        message.reply_text("✅ CAPTCHA verification has been enabled! New members must solve CAPTCHA to chat.")
    elif setting in ('off', 'no', 'false'):
        chat_settings.captcha_enabled = False
        db.commit()
        message.reply_text("✅ CAPTCHA verification has been disabled!")
    else:
        message.reply_text("Usage: /captcha on/off")

@is_group_chat
@user_admin_required
def setcaptchatext(update: Update, context: CallbackContext):
    """Set CAPTCHA text - /setcaptchatext <text>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /setcaptchatext <text>\nSet the message shown to users during CAPTCHA verification.")
        return
    
    captcha_text = " ".join(context.args)
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    chat_settings.captcha_text = captcha_text
    db.commit()
    
    message.reply_text("✅ CAPTCHA text has been updated!")

@is_group_chat
@user_admin_required
def cleanwelcome(update: Update, context: CallbackContext):
    """Toggle clean welcome - /cleanwelcome <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /cleanwelcome on/off\nAutomatically delete old welcome messages.")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.cleanwelcome = True
        db.commit()
        message.reply_text("✅ Clean welcome enabled! Old welcome messages will be deleted.")
    elif setting in ('off', 'no', 'false'):
        chat_settings.cleanwelcome = False
        db.commit()
        message.reply_text("✅ Clean welcome disabled!")
    else:
        message.reply_text("Usage: /cleanwelcome on/off")

@is_group_chat
@user_admin_required
def cleangoodbye(update: Update, context: CallbackContext):
    """Toggle clean goodbye - /cleangoodbye <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /cleangoodbye on/off\nAutomatically delete old goodbye messages.")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.cleangoodbye = True
        db.commit()
        message.reply_text("✅ Clean goodbye enabled!")
    elif setting in ('off', 'no', 'false'):
        chat_settings.cleangoodbye = False
        db.commit()
        message.reply_text("✅ Clean goodbye disabled!")
    else:
        message.reply_text("Usage: /cleangoodbye on/off")

@is_group_chat
@user_admin_required
def cleanservice(update: Update, context: CallbackContext):
    """Toggle clean service messages - /cleanservice <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
        status = "ON" if chat_settings and chat_settings.cleanservice else "OFF"
        message.reply_text(f"Clean service is currently: {status}\n\nUse /cleanservice on/off to toggle.")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    if setting in ('on', 'yes', 'true'):
        chat_settings.cleanservice = True
        db.commit()
        message.reply_text("✅ Service messages (join/leave) will now be cleaned!")
    elif setting in ('off', 'no', 'false'):
        chat_settings.cleanservice = False
        db.commit()
        message.reply_text("✅ Clean service disabled!")
    else:
        message.reply_text("Usage: /cleanservice on/off")

# Delete service messages if enabled
def delete_service(update: Update, context: CallbackContext):
    """Delete service messages if cleanservice is enabled"""
    chat = update.effective_chat
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    
    if chat_settings and chat_settings.cleanservice:
        try:
            update.message.delete()
        except Exception:
            pass

@is_group_chat
@user_admin_required
def welcomehelp(update: Update, context: CallbackContext):
    text = """
*Welcome Module:*

/welcome <on/off> - Toggle welcome messages
/setwelcome <text> - Set welcome message
/resetwelcome - Reset welcome message
/goodbye <on/off> - Toggle goodbye messages
/setgoodbye <text> - Set goodbye message
/resetgoodbye - Reset goodbye message
/welcomemute <on/off> - Mute new members
/captcha <on/off> - Enable CAPTCHA verification
/setcaptchatext <text> - Set CAPTCHA message
/cleanwelcome <on/off> - Delete old welcomes
/cleangoodbye <on/off> - Delete old goodbyes
/cleanservice <on/off> - Delete join/leave msgs

Placeholders: {first}, {last}, {fullname}, {username}, {mention}, {id}, {chatname}
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Welcome"

HANDLERS = [
    CommandHandler("welcome", welcome),
    CommandHandler("setwelcome", setwelcome),
    CommandHandler("resetwelcome", resetwelcome),
    CommandHandler("goodbye", goodbye),
    CommandHandler("setgoodbye", setgoodbye),
    CommandHandler("resetgoodbye", resetgoodbye),
    CommandHandler("welcomemute", welcomemute),
    CommandHandler("captcha", captcha),
    CommandHandler("setcaptchatext", setcaptchatext),
    CommandHandler("cleanwelcome", cleanwelcome),
    CommandHandler("cleangoodbye", cleangoodbye),
    CommandHandler("cleanservice", cleanservice),
    CommandHandler("welcomehelp", welcomehelp),
    MessageHandler(Filters.status_update.new_chat_members, greet_new_member),
    MessageHandler(Filters.status_update.left_chat_member, say_goodbye),
    CallbackQueryHandler(captcha_callback, pattern=r"^captcha_"),
]
