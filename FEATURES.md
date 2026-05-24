# Rose Bot - Complete Feature List

## Command Summary (100+ Commands)

### Admin Management (5 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/promote [user]` | Promote user to admin | Yes |
| `/demote [user]` | Demote an admin | Yes |
| `/adminlist` | List all admins | No |
| `/admincache` | Refresh admin cache | Yes |

### Bans & Restrictions (13 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/ban [user] [reason]` | Ban user permanently | Yes |
| `/tban [user] [time]` | Temporarily ban user | Yes |
| `/dban [reply] [reason]` | Delete message & ban | Yes |
| `/sban [user] [reason]` | Silently ban user | Yes |
| `/unban [user]` | Unban user | Yes |
| `/mute [user] [reason]` | Mute user permanently | Yes |
| `/tmute [user] [time]` | Temporarily mute user | Yes |
| `/dmute [reply] [reason]` | Delete message & mute | Yes |
| `/smute [user] [reason]` | Silently mute user | Yes |
| `/unmute [user]` | Unmute user | Yes |
| `/kick [user] [reason]` | Kick user from group | Yes |
| `/dkick [reply] [reason]` | Delete message & kick | Yes |
| `/skick [user] [reason]` | Silently kick user | Yes |

### Warnings (9 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/warn [user] [reason]` | Warn a user | Yes |
| `/dwarn [reply] [reason]` | Delete & warn | Yes |
| `/swarn [user] [reason]` | Silently warn | Yes |
| `/resetwarn [user]` | Reset all warnings | Yes |
| `/warns [user]` | Show user warnings | No |
| `/setwarnlimit [number]` | Set warning limit | Yes |
| `/setwarnmode [mode]` | Set punishment mode | Yes |
| `/warnings` | Show warning settings | No |

### Welcome & Goodbye (13 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/welcome [on/off]` | Toggle welcome messages | Yes |
| `/setwelcome [text]` | Set welcome message | Yes |
| `/resetwelcome` | Reset welcome message | Yes |
| `/goodbye [on/off]` | Toggle goodbye messages | Yes |
| `/setgoodbye [text]` | Set goodbye message | Yes |
| `/resetgoodbye` | Reset goodbye message | Yes |
| `/welcomemute [on/off]` | Mute new members | Yes |
| `/captcha [on/off]` | Enable CAPTCHA | Yes |
| `/setcaptchatext [text]` | Set CAPTCHA text | Yes |
| `/cleanwelcome [on/off]` | Clean old welcomes | Yes |
| `/cleangoodbye [on/off]` | Clean old goodbyes | Yes |
| `/cleanservice [on/off]` | Clean service messages | Yes |

### Anti-Flood (3 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/setflood [number]` | Set flood limit | Yes |
| `/setfloodmode [mode]` | Set punishment | Yes |
| `/flood` | Show flood settings | No |

### Locks (5 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/lock [type]` | Lock message type | Yes |
| `/unlock [type]` | Unlock message type | Yes |
| `/locks` | Show current locks | No |
| `/locktypes` | List lock types | No |
| `/lockwarns [on/off]` | Toggle lock warnings | Yes |

**Lock Types:**
- `url` / `link` - URLs and links
- `forward` - Forwarded messages
- `bot` - Bot additions
- `command` / `cmd` - Commands
- `contact` - Contact shares
- `location` - Location shares
- `email` - Email addresses
- `phone` - Phone numbers
- `game` - Game messages
- `inline` - Inline bot usage
- `media` - Photos/videos/audio
- `sticker` - Stickers
- `rtl` - RTL text
- `arabic` - Arabic script
- `chinese` - Chinese characters
- `japanese` - Japanese characters
- `cyrillic` - Cyrillic script

### Filters (4 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/filter [keyword] [reply]` | Add text filter | Yes |
| `/stop [keyword]` | Remove filter | Yes |
| `/filters` | List filters | No |

### Notes (6 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/save [name] [content]` | Save note | Yes |
| `/get [name]` | Retrieve note | No |
| `#[name]` | Quick note access | No |
| `/clear [name]` | Delete note | Yes |
| `/notes` | List all notes | No |
| `/saved` | Alias for /notes | No |

### Rules (3 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/rules` | Show group rules | No |
| `/setrules [text]` | Set group rules | Yes |
| `/resetrules` | Remove rules | Yes |

### Blacklist (6 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/addblacklist [word]` | Blacklist word | Yes |
| `/addblocklist [word]` | Alias | Yes |
| `/rmblacklist [word]` | Remove word | Yes |
| `/rmblocklist [word]` | Alias | Yes |
| `/blacklist` | List words | No |
| `/setblacklistmode [mode]` | Set action | Yes |

**Blacklist Modes:** delete, warn, ban, mute

### Federations (9 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/newfed [name]` | Create federation | Yes |
| `/delfed` | Delete federation | Yes |
| `/joinfed [fed_id]` | Join federation | Yes |
| `/leavefed` | Leave federation | Yes |
| `/fpromote [user]` | Promote fed admin | Yes |
| `/fdemote [user]` | Demote fed admin | Yes |
| `/fban [user] [reason]` | Federation ban | Yes |
| `/unfban [user]` | Remove fed ban | Yes |
| `/fedinfo` | Show federation info | No |

### Approval (5 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/approve [user]` | Approve user | Yes |
| `/unapprove [user]` | Unapprove user | Yes |
| `/unapproveall` | Unapprove all | Yes |
| `/approval [user]` | Check status | No |
| `/approvedlist` | List approved | Yes |

### Purge & Clean (5 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/purge [number]` | Delete messages | Yes |
| `/del [reply]` | Delete one message | Yes |
| `/purgefrom [reply]` | Set purge start | Yes |
| `/purgeto [reply]` | Purge to end | Yes |
| `/cleanbot [number]` | Clean bot messages | Yes |

### Pinning (5 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/pin [reply] [loud]` | Pin message | Yes |
| `/unpin` | Unpin last | Yes |
| `/unpinall` | Unpin all | Yes |
| `/pinned` | Show pinned | No |

### Reports (3 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/report [reply]` | Report to admins | No |
| `@admin` | Quick report | No |
| `/reports [on/off]` | Toggle reports | Yes |

### Info (6 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/info [user]` | User info | No |
| `/id` | Show IDs | No |
| `/groupinfo` | Group info | No |
| `/admins` | List admins | No |
| `/botinfo` | Bot info | No |

### Connections (4 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/connect` | Connect to group | Yes |
| `/disconnect` | Disconnect | Yes |
| `/connected` | Show status | No |

### Command Disabling (3 commands)
| Command | Description | Admin Only |
|---------|-------------|------------|
| `/disable [command]` | Disable command | Yes |
| `/enable [command]` | Enable command | Yes |
| `/disablelist` | List disabled | No |

### Help & Info
| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help menu |
| `/donate` | Donation info |
| `/source` | Source code info |

---

## Automatic Features (No Commands Needed)

- **Welcome Messages**: Auto-greet new members
- **Goodbye Messages**: Auto-farewell leaving members
- **CAPTCHA Verification**: Auto-verify new members (when enabled)
- **Anti-Flood**: Auto-detect and punish flooding
- **Message Locks**: Auto-delete locked content types
- **Blacklist Filter**: Auto-delete messages with blacklisted words
- **Federation Bans**: Auto-ban fed-banned users joining
- **Bot Lock**: Auto-remove bots when locked
- **Service Cleaning**: Auto-delete join/leave messages (when enabled)

---

## Database Schema

### Tables
- **chats** - Group settings and configuration
- **users** - User information
- **chat_members** - Member tracking per group
- **warnings** - Warning records
- **filters** - Text filters
- **notes** - Saved notes
- **blacklist** - Blacklisted words
- **federations** - Federation data
- **chat_federations** - Group-federation links
- **welcome_captcha** - Active CAPTCHA sessions
- **bans** - Ban records
- **report_settings** - Report configuration
- **connections** - User-group connections

---

## Security Features

- Admin permission checks on all mod commands
- Bot admin verification before actions
- Cannot ban/kick/mute admins or the bot itself
- Owner-only commands for sensitive operations
- Sudo/Support/Whitelist user tiers
- Command disabling per group

---

## Deployment Support

- Heroku (with Procfile & app.json)
- Railway
- Render
- Koyeb
- DigitalOcean
- Microsoft Azure
- Docker & Docker Compose
- Any VPS with Python 3.8+

---

## Total

- **20+ Modules**
- **100+ Commands**
- **17 Lock Types**
- **Multiple Deployment Options**
- **Full Database Persistence**
- **Automatic Moderation Features**
