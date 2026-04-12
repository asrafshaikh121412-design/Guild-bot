import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 🔐 Firebase init
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔗 Bind user
def bind_user(discord_id, ign, uid, guild, rank, joined):
    db.collection("users").document(discord_id).set({
        "ign": ign,
        "uid": uid,
        "guild": guild,
        "rank": rank,
        "joined": joined,
        "last_active": datetime.now().strftime("%d/%m/%Y")
    })

# 👤 Get user
def get_user(discord_id):
    doc = db.collection("users").document(discord_id).get()
    return doc.to_dict() if doc.exists else None

# 🔍 UID search
def get_user_by_uid(uid):
    docs = db.collection("users").where("uid", "==", uid).stream()
    for doc in docs:
        data = doc.to_dict()
        data["discord_id"] = doc.id
        return data
    return None

# 📊 Guild list
def get_all_guilds():
    docs = db.collection("users").stream()
    guilds = set()
    for doc in docs:
        data = doc.to_dict()
        guilds.add(data.get("guild", "Unknown"))
    return list(guilds)

# 👥 Guild members
def get_guild_members(guild):
    docs = db.collection("users").where("guild", "==", guild).stream()
    return [doc.to_dict() for doc in docs]

# 🔄 Activity update
def update_activity(discord_id):
    db.collection("users").document(discord_id).update({
        "last_active": datetime.now().strftime("%d/%m/%Y")
    })