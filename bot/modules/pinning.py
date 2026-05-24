"""
Pin module for Rose Bot
Handles pinning messages
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import user_admin_required, can_pin, bot_admin_required, is_group_chat

@is_group_chat
@bot_admin_required('can_pin_messages')
@can_pin
def pin(update: Update, context: CallbackContext):
    """Pin a message - /pin (reply) [loud/notify]"""
    message = update.effective_message
    
    if not message.reply_to_message:
        message.reply_text("Reply to a message to pin it!")
        return
    
    # Check for loud mode
    loud = False
    if context.args and context.args[0].lower() in ('loud', 'notify', 'notify'):
        loud = True
    
    try:
        context.bot.pin_chat_message(
            update.effective_chat.id,
            message.reply_to_message.message_id,
            disable_notification=not loud
        )
        
        if loud:
            message.reply_text("📌 Message pinned with notification!")
        else:
            message.reply_text("📌 Message pinned silently!")
            # Delete command in silent mode
            try:
                message.delete()
            except Exception:
                pass
    except Exception as e:
        message.reply_text(f"Failed to pin message: {str(e)}")

@is_group_chat
@bot_admin_required('can_pin_messages')
@can_pin
def unpin(update: Update, context: CallbackContext):
    """Unpin the current message - /unpin"""
    try:
        context.bot.unpin_chat_message(update.effective_chat.id)
        update.effective_message.reply_text("📌 Unpinned the last pinned message!")
    except Exception as e:
        update.effective_message.reply_text(f"Failed to unpin: {str(e)}")

@is_group_chat
@bot_admin_required('can_pin_messages')
@can_pin
def unpinall(update: Update, context: CallbackContext):
    """Unpin all messages - /unpinall"""
    try:
        context.bot.unpin_all_chat_messages(update.effective_chat.id)
        update.effective_message.reply_text("📌 All pinned messages have been unpinned!")
    except Exception as e:
        update.effective_message.reply_text(f"Failed to unpin all: {str(e)}")

@is_group_chat
def pinned(update: Update, context: CallbackContext):
    """Show pinned message - /pinned"""
    chat = update.effective_chat
    
    try:
        chat_info = context.bot.get_chat(chat.id)
        if chat_info.pinned_message:
            message = update.effective_message
            message.reply_text(
                "📌 Current pinned message:",
                reply_to_message_id=chat_info.pinned_message.message_id
            )
        else:
            update.effective_message.reply_text("No pinned message in this group.")
    except Exception as e:
        update.effective_message.reply_text(f"Error: {str(e)}")

@is_group_chat
def pinhelp(update: Update, context: CallbackContext):
    text = """
*Pin Module:*

/pin - Pin a message (reply required)
/pin loud - Pin with notification
/unpin - Unpin last message
/unpinall - Unpin all messages
/pinned - Show pinned message

Requires Pin Messages permission.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Pin"

HANDLERS = [
    CommandHandler("pin", pin),
    CommandHandler("unpin", unpin),
    CommandHandler("unpinall", unpinall),
    CommandHandler("pinned", pinned),
    CommandHandler("pinhelp", pinhelp),
]
