"""
Notes module for Rose Bot
Handles saved notes and retrieval
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from bot.helpers import user_admin_required, bot_admin_required, is_group_chat
from bot.database import get_db, Notes as NotesTable, add_chat

@is_group_chat
@user_admin_required
def savenote(update: Update, context: CallbackContext):
    """Save a note - /save <name> <content>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text(
            "You need to provide a name for the note!\n\n"
            "Usage: /save <name> <content>\n"
            "Or reply to a message with: /save <name>\n\n"
            "Example: /save rules Follow these rules!"
        )
        return
    
    name = context.args[0].lower()
    content = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    
    if message.reply_to_message:
        # Get content from replied message
        replied = message.reply_to_message
        if replied.text:
            content = replied.text
        elif replied.caption:
            content = replied.caption
    
    if not content:
        message.reply_text("You need to provide content for the note!")
        return
    
    db = get_db()
    
    # Check if note exists
    existing = db.query(NotesTable).filter(
        NotesTable.chat_id == chat.id,
        NotesTable.name == name
    ).first()
    
    if existing:
        existing.value = content
        existing.created_by = message.from_user.id
    else:
        new_note = NotesTable(
            chat_id=chat.id,
            name=name,
            value=content,
            created_by=message.from_user.id
        )
        db.add(new_note)
    
    db.commit()
    message.reply_text(f"✅ Note '{name}' has been saved!")

@is_group_chat
def getnote(update: Update, context: CallbackContext):
    """Get a note - #<name> or /get <name>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if message.text.startswith('#'):
        name = message.text[1:].split()[0].lower()
    elif context.args:
        name = context.args[0].lower()
    else:
        return
    
    db = get_db()
    note = db.query(NotesTable).filter(
        NotesTable.chat_id == chat.id,
        NotesTable.name == name
    ).first()
    
    if note:
        message.reply_text(note.value)
    else:
        message.reply_text(f"Note '{name}' not found!")

@is_group_chat
@user_admin_required
def clearnote(update: Update, context: CallbackContext):
    """Remove a note - /clear <name>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        message.reply_text("Usage: /clear <note_name>")
        return
    
    name = context.args[0].lower()
    
    db = get_db()
    result = db.query(NotesTable).filter(
        NotesTable.chat_id == chat.id,
        NotesTable.name == name
    ).delete()
    db.commit()
    
    if result:
        message.reply_text(f"✅ Note '{name}' has been removed!")
    else:
        message.reply_text(f"Note '{name}' not found!")

@is_group_chat
def listnotes(update: Update, context: CallbackContext):
    """List all notes - /notes or /saved"""
    chat = update.effective_chat
    
    db = get_db()
    notes_list = db.query(NotesTable).filter(
        NotesTable.chat_id == chat.id
    ).all()
    
    if not notes_list:
        update.effective_message.reply_text("No notes saved in this group!")
        return
    
    text = f"📝 <b>Notes in {chat.title}:</b>\n\n"
    for note in notes_list:
        text += f" • <code>{note.name}</code>\n"
    
    text += "\nUse /get <name> or #<name> to retrieve a note"
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@is_group_chat
@user_admin_required
def noteshelp(update: Update, context: CallbackContext):
    text = """
*Notes Module:*

/save <name> <content> - Save a note
/get <name> - Retrieve a note
#<name> - Shortcut to get a note
/clear <name> - Remove a note
/notes or /saved - List all notes

Reply to any message with /save <name> to save that message as a note.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Notes"

HANDLERS = [
    CommandHandler("save", savenote),
    CommandHandler("get", getnote),
    CommandHandler("clear", clearnote),
    CommandHandler("notes", listnotes),
    CommandHandler("saved", listnotes),
    CommandHandler("noteshelp", noteshelp),
    MessageHandler(Filters.group & Filters.regex(r'^#\w+') & ~Filters.command, getnote),
]
