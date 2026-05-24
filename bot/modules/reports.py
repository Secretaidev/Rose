"""
Reports module for Rose Bot
Handles user reports to admins
"""

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from bot.helpers import is_group_chat
from bot.database import get_db, ReportSettings, add_chat

@is_group_chat
def report(update: Update, context: CallbackContext):
    """Report a message to admins - /report (reply) or @admin"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.reply_to_message:
        message.reply_text("Reply to the message you want to report!")
        return
    
    # Check if reports are enabled
    db = get_db()
    settings = db.query(ReportSettings).filter(ReportSettings.chat_id == chat.id).first()
    if settings and not settings.enabled:
        return
    
    reported_user = message.reply_to_message.from_user
    reporter = message.from_user
    
    # Get admins
    admins = chat.get_administrators()
    
    # Don't report admins
    if reported_user.id in [admin.user.id for admin in admins]:
        message.reply_text("You can't report an admin!")
        return
    
    # Build report message
    report_text = f"🚨 <b>Report in {chat.title}</b>\n\n"
    report_text += f"<b>Reported:</b> {mention_html(reported_user.id, reported_user.first_name)}\n"
    report_text += f"<b>Reporter:</b> {mention_html(reporter.id, reporter.first_name)}\n"
    
    if message.text and len(message.text.split()) > 1:
        reason = " ".join(message.text.split()[1:])
        report_text += f"<b>Reason:</b> {reason}\n"
    
    report_text += f"<b>Message:</b> <a href='https://t.me/c/{str(chat.id)[4:]}/{message.reply_to_message.message_id}'>Jump to message</a>"
    
    # Notify admins
    admin_notified = 0
    for admin in admins:
        if admin.user.is_bot:
            continue
        try:
            context.bot.send_message(
                admin.user.id,
                report_text,
                parse_mode=ParseMode.HTML
            )
            admin_notified += 1
        except Exception:
            pass
    
    if admin_notified > 0:
        message.reply_text(f"🚨 Report sent to {admin_notified} admin(s)!")
    else:
        message.reply_text("Could not notify any admins. They may not have started the bot in private.")

@is_group_chat
def reports(update: Update, context: CallbackContext):
    """Toggle reports - /reports <on/off>"""
    chat = update.effective_chat
    message = update.effective_message
    
    if not context.args:
        db = get_db()
        settings = db.query(ReportSettings).filter(ReportSettings.chat_id == chat.id).first()
        status = "ON" if settings and settings.enabled else "OFF"
        message.reply_text(f"Reports are currently: {status}\nUse /reports on/off")
        return
    
    setting = context.args[0].lower()
    
    db = get_db()
    settings = db.query(ReportSettings).filter(ReportSettings.chat_id == chat.id).first()
    
    if not settings:
        settings = ReportSettings(chat_id=chat.id, enabled=True)
        db.add(settings)
    
    if setting in ('on', 'yes', 'true'):
        settings.enabled = True
        db.commit()
        message.reply_text("✅ Reports have been enabled!")
    elif setting in ('off', 'no', 'false'):
        settings.enabled = False
        db.commit()
        message.reply_text("✅ Reports have been disabled!")
    else:
        message.reply_text("Usage: /reports on/off")

@is_group_chat
def reporthelp(update: Update, context: CallbackContext):
    text = """
*Reports Module:*

/report - Report a message (reply required)
@admin - Same as /report
/reports <on/off> - Toggle reports

When reporting, admins will receive a DM with the report details.
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

__mod_name__ = "Reports"

HANDLERS = [
    CommandHandler("report", report),
    CommandHandler("reports", reports),
    CommandHandler("reporthelp", reporthelp),
    MessageHandler(Filters.group & Filters.regex(r'@admin'), report),
]
