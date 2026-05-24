"""
Help module for Rose Bot
Handles help command and module listing
"""

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Filters, CallbackQueryHandler

MODULES_HELP = {
    "Admin": [
        "/promote [user] - Promote user to admin",
        "/demote [user] - Demote admin",
        "/adminlist - List admins",
        "/admincache - Refresh admin cache",
    ],
    "Bans": [
        "/ban [user] [reason] - Ban user",
        "/tban [user] [time] - Temp ban (30m, 2h, 1d, 1w)",
        "/dban [reply] - Delete & ban",
        "/sban [user] - Silent ban",
        "/unban [user] - Unban",
        "/mute [user] - Mute user",
        "/tmute [user] [time] - Temp mute",
        "/dmute [reply] - Delete & mute",
        "/smute [user] - Silent mute",
        "/unmute [user] - Unmute",
        "/kick [user] - Kick user",
        "/dkick [reply] - Delete & kick",
        "/skick [user] - Silent kick",
    ],
    "Warnings": [
        "/warn [user] [reason] - Warn user",
        "/dwarn [reply] - Delete & warn",
        "/swarn [user] - Silent warn",
        "/resetwarn [user] - Reset warnings",
        "/warns [user] - Show warnings",
        "/setwarnlimit [number] - Set warn limit",
        "/setwarnmode [mode] - Set punishment",
        "/warnings - Show settings",
    ],
    "Welcome": [
        "/welcome [on/off] - Toggle welcome",
        "/setwelcome [text] - Set welcome",
        "/resetwelcome - Reset welcome",
        "/goodbye [on/off] - Toggle goodbye",
        "/setgoodbye [text] - Set goodbye",
        "/resetgoodbye - Reset goodbye",
        "/welcomemute [on/off] - Mute new users",
        "/captcha [on/off] - Enable CAPTCHA",
        "/setcaptchatext [text] - Set CAPTCHA text",
        "/cleanwelcome [on/off] - Clean welcomes",
        "/cleangoodbye [on/off] - Clean goodbyes",
        "/cleanservice [on/off] - Clean service",
    ],
    "Anti-Flood": [
        "/setflood [number] - Set flood limit",
        "/setfloodmode [mode] [time] - Set punishment",
        "/flood - Show settings",
    ],
    "Locks": [
        "/lock [type] - Lock message type",
        "/unlock [type] - Unlock type",
        "/locks - Show current locks",
        "/locktypes - Available types",
        "/lockwarns [on/off] - Toggle warnings",
    ],
    "Filters": [
        "/filter [keyword] [reply] - Add filter",
        "/stop [keyword] - Remove filter",
        "/filters - List filters",
    ],
    "Notes": [
        "/save [name] [content] - Save note",
        "/get [name] - Get note",
        "#[name] - Quick get note",
        "/clear [name] - Delete note",
        "/notes - List notes",
    ],
    "Rules": [
        "/rules - Show rules",
        "/setrules [text] - Set rules",
        "/resetrules - Remove rules",
    ],
    "Blacklist": [
        "/addblacklist [word] - Blacklist word",
        "/rmblacklist [word] - Remove word",
        "/blacklist - List words",
        "/setblacklistmode [mode] - Set action",
    ],
    "Federation": [
        "/newfed [name] - Create federation",
        "/delfed - Delete federation",
        "/joinfed [fed_id] - Join federation",
        "/leavefed - Leave federation",
        "/fban [user] [reason] - Fed ban",
        "/unfban [user] - Unfedban",
        "/fedinfo - Show fed info",
    ],
    "Approval": [
        "/approve [user] - Approve user",
        "/unapprove [user] - Unapprove",
        "/unapproveall - Unapprove all",
        "/approval [user] - Check status",
    ],
    "Purge": [
        "/purge [number] - Delete messages",
        "/del [reply] - Delete one message",
        "/purgefrom [reply] - Set start",
        "/purgeto [reply] - Purge to end",
    ],
    "Pin": [
        "/pin [reply] [loud] - Pin message",
        "/unpin - Unpin last",
        "/unpinall - Unpin all",
        "/pinned - Show pinned",
    ],
    "Reports": [
        "/report [reply] - Report to admins",
        "@admin - Report message",
        "/reports [on/off] - Toggle",
    ],
    "Info": [
        "/info [user] - User info",
        "/id - Show IDs",
        "/groupinfo - Group info",
        "/admins - List admins",
        "/botinfo - Bot info",
    ],
    "Connections": [
        "/connect - Connect to group",
        "/disconnect - Disconnect",
        "/connected - Show status",
    ],
    "Disable": [
        "/disable [cmd] - Disable command",
        "/enable [cmd] - Enable command",
        "/disablelist - List disabled",
    ],
}

def help_command(update: Update, context: CallbackContext):
    """Main help command"""
    if update.effective_chat.type != 'private':
        update.effective_message.reply_text(
            "Send me a PM to get the help menu!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Help", url=f"https://t.me/{context.bot.username}?start=help")]
            ])
        )
        return
    
    show_help_menu(update, context)

def show_help_menu(update: Update, context: CallbackContext):
    """Show help menu with module buttons"""
    keyboard = []
    row = []
    
    for i, module in enumerate(MODULES_HELP.keys()):
        callback_data = f"help_{module}"
        button = InlineKeyboardButton(module, callback_data=callback_data)
        
        if i % 3 == 0 and row:
            keyboard.append(row)
            row = [button]
        else:
            row.append(button)
    
    if row:
        keyboard.append(row)
    
    text = """
👋 <b>Welcome to Rose Bot Help!</b>

I'm a powerful group management bot. Select a module below to see available commands.

<b>Quick Commands:</b>
• /start - Start the bot
• /help - This menu
• /donate - Support the project

<b>Getting Started:</b>
1. Add me to your group
2. Make me an admin with required permissions
3. Use /help to explore commands

<b>Key Features:</b>
✅ Moderation (ban/mute/kick/warn)
✅ Welcome/Goodbye messages
✅ CAPTCHA verification
✅ Anti-flood protection
✅ Message locks
✅ Filters & Notes
✅ Federation bans
✅ Blacklist words

<i>Select a module below:</i>
"""
    
    if update.callback_query:
        update.callback_query.message.edit_text(
            text, 
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        update.effective_message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def help_button(update: Update, context: CallbackContext):
    """Handle help button callbacks"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data == "help_back":
        show_help_menu(update, context)
        return
    
    if data.startswith("help_"):
        module = data[5:]
        
        if module in MODULES_HELP:
            commands = MODULES_HELP[module]
            text = f"📖 <b>{module} Module</b>\n\n"
            for cmd in commands:
                text += f"• {cmd}\n"
            
            text += "\n<i>Use /start to go back to the main menu.</i>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀ Back", callback_data="help_back")]
            ])
            
            query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

def start(update: Update, context: CallbackContext):
    """Start command handler"""
    user = update.effective_user
    
    if update.effective_chat.type != 'private':
        update.effective_message.reply_text(
            "I'm alive! PM me for help.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Help", url=f"https://t.me/{context.bot.username}?start=help")]
            ])
        )
        return
    
    if context.args and context.args[0] == 'help':
        show_help_menu(update, context)
        return
    
    text = f"""
🌹 <b>Hello {user.first_name}!</b>

I'm <b>Rose</b>, a powerful group management bot. I can help you manage your Telegram groups efficiently!

<b>What I can do:</b>
✅ Restrict users (ban/mute/kick)
✅ Welcome new members with custom messages
✅ Protect against spam and flooding
✅ Filter messages and delete unwanted content
✅ Set group rules and notes
✅ Track warnings and user info
✅ Cross-group federation bans
✅ And much more!

<b>To get started:</b>
1. Add me to your group
2. Promote me to admin
3. Use /help to see all commands

<b>Need help?</b> Click the button below!
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Commands Help", callback_data="help_back")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
    ])
    
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

def donate(update: Update, context: CallbackContext):
    """Donate command"""
    text = """
💝 <b>Support Rose Bot</b>

Thank you for wanting to support Rose Bot!

Your donations help keep the bot running and enable new features.

<b>Ways to support:</b>
• Share the bot with your friends
• Report bugs and suggest features
• Contribute to the code

Thank you! 🌹
"""
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

def source(update: Update, context: CallbackContext):
    """Source code command"""
    update.effective_message.reply_text(
        "🌹 <b>Rose Bot</b>\n\n"
        "I'm a powerful group management bot clone.\n"
        "Built with Python and python-telegram-bot.\n\n"
        "<b>Features:</b>\n"
        "• Full moderation suite\n"
        "• Welcome/Goodbye with CAPTCHA\n"
        "• Anti-flood & Locks\n"
        "• Filters, Notes & Rules\n"
        "• Federation system\n"
        "• Blacklist & Warnings\n\n"
        "Version: 1.0.0",
        parse_mode=ParseMode.HTML
    )

# Module help commands
MODULE_HELP_COMMANDS = {
    'adminhelp': 'Admin',
    'banshelp': 'Bans',
    'warnshelp': 'Warnings',
    'welcomehelp': 'Welcome',
    'floodhelp': 'Anti-Flood',
    'lockshelp': 'Locks',
    'filtershelp': 'Filters',
    'noteshelp': 'Notes',
    'ruleshelp': 'Rules',
    'blacklisthelp': 'Blacklist',
    'federationhelp': 'Federation',
    'approvalhelp': 'Approval',
    'purgehelp': 'Purge',
    'pinhelp': 'Pin',
    'reporthelp': 'Reports',
    'infohelp': 'Info',
    'connectionshelp': 'Connections',
    'disablehelp': 'Disable',
}

def module_help(update: Update, context: CallbackContext, module_name: str):
    """Show help for a specific module"""
    if module_name in MODULES_HELP:
        commands = MODULES_HELP[module_name]
        text = f"📖 <b>{module_name} Module</b>\n\n"
        for cmd in commands:
            text += f"• {cmd}\n"
        update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    else:
        update.effective_message.reply_text(f"Unknown module: {module_name}")

__mod_name__ = "Help"

HANDLERS = [
    CommandHandler("start", start),
    CommandHandler("help", help_command),
    CommandHandler("donate", donate),
    CommandHandler("source", source),
    CallbackQueryHandler(help_button, pattern=r"^help_"),
]
