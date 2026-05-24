"""
Purge/Clean module for Rose Bot
Handles message purging and cleaning
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import user_admin_required, can_delete, bot_admin_required, is_group_chat

@is_group_chat
@bot_admin_required('can_delete_messages')
@can_delete
def purge(update: Update, context: CallbackContext):
    """Purge messages - /purge or /purge <number>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if message.reply_to_message:
        # Purge from replied message to current
        start_msg_id = message.reply_to_message.message_id
        end_msg_id = message.message_id
        
        deleted = 0
        for msg_id in range(start_msg_id, end_msg_id + 1):
            try:
                context.bot.delete_message(chat.id, msg_id)
                deleted += 1
            except Exception:
                pass
        
        # Send confirmation and delete it after 3 seconds
        confirm = message.reply_text(f"✅ Purged {deleted} messages!")
        
        # Delete command and confirmation after delay
        import threading
        def delete_confirm():
            import time
            time.sleep(3)
            try:
                confirm.delete()
            except Exception:
                pass
        
        threading.Thread(target=delete_confirm).start()
    
    elif context.args and context.args[0].isdigit():
        count = int(context.args[0])
        if count < 1 or count > 1000:
            message.reply_text("Please specify a number between 1 and 1000.")
            return
        
        deleted = 0
        msg_id = message.message_id - 1
        
        while count > 0 and msg_id > 0:
            try:
                context.bot.delete_message(chat.id, msg_id)
                deleted += 1
                count -= 1
            except Exception:
                pass
            msg_id -= 1
        
        # Delete the command message
        try:
            message.delete()
        except Exception:
            pass
        
        confirm = context.bot.send_message(chat.id, f"✅ Purged {deleted} messages!")
        
        import threading
        def delete_confirm():
            import time
            time.sleep(3)
            try:
                confirm.delete()
            except Exception:
                pass
        
        threading.Thread(target=delete_confirm).start()
    
    else:
        message.reply_text(
            "Usage:\n"
            "/purge - Purge from replied message\n"
            "/purge <number> - Purge last N messages"
        )

@is_group_chat
@bot_admin_required('can_delete_messages')
@can_delete
def del_command(update: Update, context: CallbackContext):
    """Delete a message - /del (reply)"""
    message = update.effective_message
    
    if message.reply_to_message:
        try:
            message.reply_to_message.delete()
            message.delete()
        except Exception as e:
            message.reply_text(f"Failed to delete: {str(e)}")
    else:
        message.reply_text("Reply to a message to delete it!")

@is_group_chat
@bot_admin_required('can_delete_messages')
@can_delete
def purgefrom(update: Update, context: CallbackContext):
    """Set purge start point - /purgefrom (reply)"""
    message = update.effective_message
    
    if message.reply_to_message:
        # Store the message ID in bot data
        if 'purge_points' not in context.chat_data:
            context.chat_data['purge_points'] = {}
        
        context.chat_data['purge_points'][message.from_user.id] = message.reply_to_message.message_id
        message.reply_text("✅ Start point set! Now reply to the end message with /purgeto.")
    else:
        message.reply_text("Reply to a message to set as the start point!")

@is_group_chat
@bot_admin_required('can_delete_messages')
@can_delete
def purgeto(update: Update, context: CallbackContext):
    """Purge from set point - /purgeto (reply)"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.reply_to_message:
        message.reply_text("Reply to the end message!")
        return
    
    purge_points = context.chat_data.get('purge_points', {})
    start_msg_id = purge_points.get(message.from_user.id)
    
    if not start_msg_id:
        message.reply_text("No start point set! Use /purgefrom first.")
        return
    
    end_msg_id = message.reply_to_message.message_id
    
    deleted = 0
    for msg_id in range(start_msg_id, end_msg_id + 1):
        try:
            context.bot.delete_message(chat.id, msg_id)
            deleted += 1
        except Exception:
            pass
    
    confirm = message.reply_text(f"✅ Purged {deleted} messages!")
    
    import threading
    def delete_confirm():
        import time
        time.sleep(3)
        try:
            confirm.delete()
        except Exception:
            pass
    
    threading.Thread(target=delete_confirm).start()
    
    # Clear the purge point
    if message.from_user.id in purge_points:
        del purge_points[message.from_user.id]

@is_group_chat
@bot_admin_required('can_delete_messages')
@can_delete
def clean_bot_messages(update: Update, context: CallbackContext):
    """Clean bot messages - /cleanbot <number>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args or not context.args[0].isdigit():
        message.reply_text("Usage: /cleanbot <number>")
        return
    
    count = int(context.args[0])
    if count < 1 or count > 100:
        message.reply_text("Please specify between 1 and 100.")
        return
    
    deleted = 0
    msg_id = message.message_id - 1
    
    while count > 0 and msg_id > 0:
        try:
            msg = context.bot.get_message(chat.id, msg_id)
            if msg and msg.from_user.is_bot:
                context.bot.delete_message(chat.id, msg_id)
                deleted += 1
                count -= 1
        except Exception:
            pass
        msg_id -= 1
    
    message.reply_text(f"✅ Cleaned {deleted} bot messages!")

@is_group_chat
def purgehelp(update: Update, context: CallbackContext):
    text = """
*Purge Module:*

/purge - Purge from replied message to now
/purge <number> - Purge last N messages
/del - Delete replied message
/purgefrom - Set purge start point (reply)
/purgeto - Purge to this point (reply)

All commands require Delete Messages permission.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Purge"

HANDLERS = [
    CommandHandler("purge", purge),
    CommandHandler("del", del_command),
    CommandHandler("purgefrom", purgefrom),
    CommandHandler("purgeto", purgeto),
    CommandHandler("cleanbot", clean_bot_messages),
    CommandHandler("purgehelp", purgehelp),
]
