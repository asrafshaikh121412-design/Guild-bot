import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

# 🔥 Firebase init
if not firebase_admin._apps:
    firebase_key = os.getenv("FIREBASE_KEY")

    if not firebase_key:
        raise ValueError("❌ FIREBASE_KEY not found")

    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔗 Bind user
def bind_user(discord_id, ign, uid, guild, rank, joined):
    db.collection("users").document(discord_id).set({
        "ign": ign,
        "uid": uid,
        "guild": guild.upper(),
        "rank": rank,
        "joined": joined,
        "last_active": datetime.now().strftime("%d/%m/%Y")
    }, merge=True)

# 👤 Get user
def get_user(discord_id):
    doc = db.collection("users").document(discord_id).get()
    return doc.to_dict() if doc.exists else None

# 👥 Guild members
def get_guild_members(guild):
    docs = db.collection("users").where("guild", "==", guild.upper()).stream()
    
    members = []
    for doc in docs:
        data = doc.to_dict()
        data["discord_id"] = doc.id
        members.append(data)

    return members

# 📊 Guild list (from guilds collection)
def get_all_guilds():
    docs = db.collection("guilds").stream()
    return [doc.id for doc in docs]

# ➕ Add guild
def add_guild(guild_name):
    db.collection("guilds").document(guild_name.upper()).set({
        "name": guild_name.upper(),
        "created_at": datetime.now().strftime("%d/%m/%Y")
    })

# ❌ Remove guild (safe)
def delete_guild(guild_name):
    # remove members first
    docs = db.collection("users").where("guild", "==", guild_name.upper()).stream()

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "guild": "No Guild"
        })

    # delete guild
    db.collection("guilds").document(guild_name.upper()).delete()

# 🔄 Activity
def update_activity(discord_id):
    try:
        db.collection("users").document(discord_id).update({
            "last_active": datetime.now().strftime("%d/%m/%Y")
        })
    except:
        pass

# ✏️ Edit user (SAFE)
def edit_user(discord_id, ign=None, uid=None, guild=None, rank=None, joined=None):
    doc_ref = db.collection("users").document(discord_id)
    doc = doc_ref.get()

    if not doc.exists:
        return False

    update_data = {}

    if ign:
        update_data["ign"] = ign
    if uid:
        update_data["uid"] = uid
    if guild:
        update_data["guild"] = guild.upper()
    if rank:
        update_data["rank"] = rank
    if joined:
        update_data["joined"] = joined

    update_data["last_active"] = datetime.now().strftime("%d/%m/%Y")

    doc_ref.update(update_data)
    return True