import sqlite3

conn = sqlite3.connect("guild.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS guilds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    guild_id INTEGER
)
""")

conn.commit()

# Add guild
def add_guild(name):
    cursor.execute("INSERT INTO guilds (name) VALUES (?)", (name,))
    conn.commit()

# Remove guild
def remove_guild(name):
    cursor.execute("DELETE FROM guilds WHERE name=?", (name,))
    conn.commit()

# Add player
def add_player(player, guild_name):
    cursor.execute("SELECT id FROM guilds WHERE name=?", (guild_name,))
    guild = cursor.fetchone()
    if guild:
        cursor.execute("INSERT INTO players (name, guild_id) VALUES (?, ?)", (player, guild[0]))
        conn.commit()
        return True
    return False

# Remove player
def remove_player(player):
    cursor.execute("DELETE FROM players WHERE name=?", (player,))
    conn.commit()

# Get player info
def get_player(player):
    cursor.execute("""
    SELECT players.name, guilds.name 
    FROM players 
    JOIN guilds ON players.guild_id = guilds.id 
    WHERE players.name=?
    """, (player,))
    return cursor.fetchone()