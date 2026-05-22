# 🔥 Guild-bot

A powerful Discord bot built for **Free Fire gaming communities**. Manage guild members, roles, ranks, and player profiles — all inside Discord.

> Built with Python & discord.py by **Asraf Shaikh**

---

## ✨ Features

- 🎭 **Role System** — Assign/remove any Discord role using `?rolename @user`
- 👥 **Guild Management** — Add/remove guilds and manage members
- 🏆 **Rank System** — Set ranks like Member, Officer, AGL, Leader
- 👤 **Player Profiles** — View IGN, UID, Guild, and Rank
- 🔍 **Player Search** — Search any Free Fire player by UID (live API)
- 🤖 **Auto Nickname** — Auto sets `FE <name>` format on member join
- 📊 **Guild Stats** — View all guilds with member counts by rank
- 🔗 **Account Linking** — Link Discord account to Free Fire profile

---

## 📋 Commands

### ⚡ Prefix Commands (Officer / AGL / Leader / Admin only)

| Command | Description |
|---------|-------------|
| `?rolename @user` | Assign a role to a user (e.g. `?fe07 @Asraf`) |
| `?removerolename @user` | Remove a role from a user (e.g. `?removefe07 @Asraf`) |

### 🔷 Slash Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/bind` | Link your Discord to your FF account (IGN, UID, Guild) | Everyone |
| `/profile` | View your or another user's profile | Everyone |
| `/search_player` | Search any player by UID (live + database) | Everyone |
| `/guild_list` | View all guilds with member/officer/leader counts | Everyone |
| `/guild_members` | View all members of a specific guild | Everyone |
| `/add_guild` | Add a new guild | Admin only |
| `/remove_guild` | Remove a guild | Admin only |
| `/remove_member` | Remove a member from their guild | Officer+ |
| `/edit_player` | Edit a player's full profile | Officer+ |
| `/set_rank` | Set a member's rank (Member/Officer/AGL/Leader) | Officer+ |

---

## 🏅 Rank Hierarchy

```
👑 Leader
⚔️  AGL (Assistant Guild Leader)
🛡️  Officer
👤 Member
```

> Officers, AGLs, and Leaders can use prefix role commands.

---

## 🛠️ Setup & Installation

### Requirements
- Python 3.8+
- discord.py 2.0+

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/asrafshaikh/Guild-bot.git
cd Guild-bot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set your bot token**

Create a `.env` file:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

**4. Run the bot**
```bash
python bot.py
```

---

## 🔐 Bot Permissions Required

- Manage Roles
- Manage Nicknames
- Send Messages
- Read Message History
- Use Slash Commands

---

## 👤 Author

**Asraf Shaikh** — Python Developer  
📧 asrafshaikh121412@gmail.com  
🔗 [GitHub](https://github.com/asrafshaikh)

---

## 📄 License

This project is open source under the [MIT License](LICENSE).
