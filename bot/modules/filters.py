"""
Filters module for Rose Bot
Handles text triggers and responses
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from bot.helpers import user_admin_required, bot_admin_required, can_delete, is_group_chat
from bot.database import get_db, Filters as FiltersTable, add_chat

@is_group_chat
@user_admin_required
def addfilter(update: Update, context: CallbackContext):
    """Add a filter - /filter <keyword> <response>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args or len(context.args) < 2:
        message.reply_text(
            "You need to provide a keyword and response!\n\n"
            "Usage: /filter <keyword> <response>\n"
            "Or reply to a message with: /filter <keyword>\n\n"
            "Examples:\n"
            "/filter hello Hi there!\n"
            "/filter rules Please read the rules!"
        )
        return
    
    keyword = context.args[0].lower()
    response = " ".join(context.args[1:])
    
    if message.reply_to_message:
        # Get response from replied message
        if message.reply_to_message.text:
            response = message.reply_to_message.text
        elif message.reply_to_message.caption:
            response = message.reply_to_message.caption
    
    db = get_db()
    chat_settings = db.query(Chats).filter(Chats.chat_id == chat.id).first()
    if not chat_settings:
        from bot.database import add_chat
        chat_settings = add_chat(chat.id, chat.title, chat.type)
        db.refresh(chat_settings)
    
    # Check if filter exists
    existing = db.query(FiltersTable).filter(
        FiltersTable.chat_id == chat.id,
        FiltersTable.keyword == keyword
    ).first()
    
    if existing:
        existing.response = response
        existing.created_by = message.from_user.id
    else:
        new_filter = FiltersTable(
            chat_id=chat.id,
            keyword=keyword,
            response=response,
            created_by=message.from_user.id
        )
        db.add(new_filter)
    
    db.commit()
    message.reply_text(f"✅ Filter '{keyword}' has been added!")

@is_group_chat
@user_admin_required
def stopfilter(update: Update, context: CallbackContext):
    """Remove a filter - /stop <keyword>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /stop <keyword>")
        return
    
    keyword = context.args[0].lower()
    
    db = get_db()
    result = db.query(FiltersTable).filter(
        FiltersTable.chat_id == chat.id,
        FiltersTable.keyword == keyword
    ).delete()
    db.commit()
    
    if result:
        message.reply_text(f"✅ Filter '{keyword}' has been removed!")
    else:
        message.reply_text(f"Filter '{keyword}' not found!")

@is_group_chat
def listfilters(update: Update, context: CallbackContext):
    """List all filters - /filters"""
    chat = update.effective_chat
    
    db = get_db()
    filters_list = db.query(FiltersTable).filter(
        FiltersTable.chat_id == chat.id
    ).all()
    
    if not filters_list:
        update.effective_message.reply_text("No filters set in this group!")
        return
    
    text = f"🔍 <b>Filters in {chat.title}:</b>\n\n"
    for i, f in enumerate(filters_list, 1):
        text += f"{i}. <code>{f.keyword}</code>\n"
    
    text += "\nUse /stop <keyword> to remove a filter"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

def check_filters(update: Update, context: CallbackContext):
    """Check and respond to filters"""
    if not update.effective_chat or not update.effective_message:
        return
    
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.text:
        return
    
    text = message.text.lower()
    words = text.split()
    
    db = get_db()
    filters_list = db.query(FiltersTable).filter(
        FiltersTable.chat_id == chat.id
    ).all()
    
    for f in filters_list:
        if f.keyword.lower() in text or f.keyword.lower() in words:
            message.reply_text(f.response)
            break

@is_group_chat
@user_admin_required
def filtershelp(update: Update, context: CallbackContext):
    text = """
*Filters Module:*

/filter <keyword> <response> - Add a filter
/stop <keyword> - Remove a filter
/filters - List all filters

Reply to any message with /filter <keyword> to save that message as the response.

Filters are case-insensitive. When someone says the trigger word, the bot will reply with the saved response.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Filters"

HANDLERS = [
    CommandHandler("filter", addfilter),
    CommandHandler("stop", stopfilter),
    CommandHandler("filters", listfilters),
    CommandHandler("filtershelp", filtershelp),
    MessageHandler(Filters.group & Filters.text & ~Filters.command, check_filters),
]
