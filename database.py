import sqlite3

conn = sqlite3.connect("guild.db")
cursor = conn.cursor()

# 🔥 FULL TABLE (better structure)
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

# 🔗 Bind user (update if exists)
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

# 👤 Get user
def get_user(discord_id):
    cursor.execute("SELECT * FROM users WHERE discord_id=?", (discord_id,))
    return cursor.fetchone()

# ❌ Remove user
def remove_user(discord_id):
    cursor.execute("DELETE FROM users WHERE discord_id=?", (discord_id,))
    conn.commit()

# 📊 All users (future leaderboard)
def get_all_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()