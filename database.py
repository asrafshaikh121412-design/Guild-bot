import sqlite3

conn = sqlite3.connect("guild.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    discord_id TEXT PRIMARY KEY,
    ign TEXT,
    uid TEXT,
    guild TEXT,
    rank TEXT,
    joined TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def bind_user(discord_id, ign, uid, guild, rank, joined):
    cursor.execute("""
    INSERT INTO users (discord_id, ign, uid, guild, rank, joined)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(discord_id) DO UPDATE SET
        ign=excluded.ign,
        uid=excluded.uid,
        guild=excluded.guild,
        rank=excluded.rank,
        joined=excluded.joined
    """, (discord_id, ign, uid, guild, rank, joined))
    conn.commit()

def get_user(discord_id):
    cursor.execute("SELECT * FROM users WHERE discord_id=?", (discord_id,))
    return cursor.fetchone()
# 🔍 Search by UID
def get_user_by_uid(uid):
    cursor.execute("SELECT * FROM users WHERE uid=?", (uid,))
    return cursor.fetchone()

# 📊 Get all guilds
def get_all_guilds():
    cursor.execute("SELECT DISTINCT guild FROM users")
    return cursor.fetchall()

# 👥 Guild members
def get_guild_members(guild):
    cursor.execute("SELECT * FROM users WHERE guild=?", (guild,))
    return cursor.fetchall()