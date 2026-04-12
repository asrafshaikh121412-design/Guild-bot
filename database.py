import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

# 🔥 ENV se Firebase key load
firebase_key = os.getenv("FIREBASE_KEY")

if not firebase_key:
    raise ValueError("❌ FIREBASE_KEY not found in environment variables")

cred = credentials.Certificate(json.loads(firebase_key))
firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔗 Bind / Save user
def bind_user(discord_id, ign, uid, guild, rank, joined):
    db.collection("users").document(discord_id).set({
        "ign": ign,
        "uid": uid,
        "guild": guild,
        "rank": rank,
        "joined": joined,
        "last_active": datetime.now().strftime("%d/%m/%Y")
    })

# 👤 Get user by Discord ID
def get_user(discord_id):
    doc = db.collection("users").document(discord_id).get()
    return doc.to_dict() if doc.exists else None

# 🔍 Get user by UID
def get_user_by_uid(uid):
    docs = db.collection("users").where("uid", "==", uid).stream()
    for doc in docs:
        data = doc.to_dict()
        data["discord_id"] = doc.id
        return data
    return None

# 📊 Get all guilds
def get_all_guilds():
    docs = db.collection("users").stream()
    guilds = set()

    for doc in docs:
        data = doc.to_dict()
        guilds.add(data.get("guild", "Unknown"))

    return list(guilds)

# 👥 Get guild members
def get_guild_members(guild):
    docs = db.collection("users").where("guild", "==", guild).stream()
    return [doc.to_dict() for doc in docs]

# 🔄 Update last active
def update_activity(discord_id):
    try:
        db.collection("users").document(discord_id).update({
            "last_active": datetime.now().strftime("%d/%m/%Y")
        })
    except:
        pass