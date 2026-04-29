import discord
from discord.ext import commands
import os, requests, time
import database

TOKEN = os.getenv("DISCORD_TOKEN")

# 🔥 INTENTS (FIXED)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

cooldown = {}

# 🔥 CLEAN RANK
def clean_rank(r):
    return r.upper().replace("👤","").replace("🔥","").replace("💎","").replace("⚡","").strip()

# 🔥 READY
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🔥 Bot Ready: {bot.user}")

# 🔥 AUTO PREFIX
@bot.event
async def on_member_join(member):
    try:
        name = member.name.upper().replace("FE", "").strip()
        await member.edit(nick=f"FE {name}")
    except Exception as e:
        print("Nickname error:", e)

# 🔥 ROLE SYSTEM
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    database.update_activity(str(message.author.id))

    now = time.time()

    if message.author.id in cooldown:
        if now - cooldown[message.author.id] < 5:
            return

    user_data = database.get_user(str(message.author.id))
    allowed = ["OFFICER","AGL","LEADER"]
    is_admin = message.author.guild_permissions.administrator

    if message.content.startswith("?"):

        if not is_admin:
            if not user_data or clean_rank(user_data.get("rank","")) not in allowed:
                await message.channel.send("❌ Only Officer / AGL / Leader")
                return

        parts = message.content.split()
        member = message.mentions[0] if message.mentions else None

        if not member:
            await message.channel.send("❌ Mention user")
            return

        cmd = parts[0][1:].strip()

        role_name = cmd.replace("remove","").strip()

        role = discord.utils.find(
            lambda r: r.name.lower() == role_name.lower(),
            message.guild.roles
        )

        if not role:
            await message.channel.send(f"❌ Role `{role_name}` not found")
            return

        if cmd.lower().startswith("remove"):
            await member.remove_roles(role)
            await message.channel.send(f"🗑 {member.mention} removed {role.name}")
        else:
            await member.add_roles(role)
            await message.channel.send(f"✅ {member.mention} got {role.name}")

        cooldown[message.author.id] = now

    await bot.process_commands(message)

# 🔗 BIND
@bot.tree.command(name="bind")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, joined: str):

    if database.get_user(str(interaction.user.id)):
        await interaction.response.send_message("❌ Already linked", ephemeral=True)
        return

    await interaction.response.defer()

    database.bind_user(str(interaction.user.id), ign, uid, guild.upper(), "👤 Member", joined)

    role = discord.utils.get(interaction.guild.roles, name=guild.upper())
    if role:
        await interaction.user.add_roles(role)

    await interaction.followup.send("✅ Linked + Role assigned")

# 👤 PROFILE
@bot.tree.command(name="profile")
async def profile(interaction: discord.Interaction, user: discord.Member = None):

    await interaction.response.defer()

    target = user or interaction.user
    data = database.get_user(str(target.id))

    if not data:
        await interaction.followup.send("❌ No profile")
        return

    embed = discord.Embed(title=f"🔥 {target.name}", color=discord.Color.green())

    embed.add_field(name="IGN", value=data["ign"])
    embed.add_field(name="UID", value=data["uid"])
    embed.add_field(name="Guild", value=data["guild"])
    embed.add_field(name="Rank", value=data["rank"])

    embed.set_footer(text="Created by Asraf")

    await interaction.followup.send(embed=embed)

# 🔍 SEARCH
@bot.tree.command(name="search_player")
async def search_player(interaction: discord.Interaction, uid: str):

    await interaction.response.defer()

    try:
        url = f"https://free-ff-api-src-5plp.onrender.com/api/v1/account?region=IND&uid={uid}"
        res = requests.get(url, timeout=8)

        if res.status_code == 200:
            data = res.json()
            if "nickname" in data:
                embed = discord.Embed(title=data["nickname"], color=discord.Color.blue())
                embed.add_field(name="UID", value=uid)
                embed.add_field(name="Level", value=data.get("level",0))
                await interaction.followup.send(embed=embed)
                return
    except:
        pass

    data = database.get_user_by_uid(uid)

    if data:
        embed = discord.Embed(title=data["ign"], color=discord.Color.green())
        embed.add_field(name="Guild", value=data["guild"])
        await interaction.followup.send(embed=embed)
        return

    await interaction.followup.send("❌ Player not found")

# 📊 GUILD LIST
@bot.tree.command(name="guild_list")
async def guild_list(interaction: discord.Interaction):

    await interaction.response.defer()

    guilds = database.get_all_guilds()

    embed = discord.Embed(title="🏠 Guild List", color=discord.Color.blue())

    for g in guilds:
        members = database.get_guild_members(g)

        m = sum(1 for x in members if clean_rank(x.get("rank",""))=="MEMBER")
        o = sum(1 for x in members if clean_rank(x.get("rank",""))=="OFFICER")
        a = sum(1 for x in members if clean_rank(x.get("rank",""))=="AGL")
        l = sum(1 for x in members if clean_rank(x.get("rank",""))=="LEADER")

        embed.add_field(
            name=g,
            value=f"👥 {m} | 🛡 {o} | ⚔ {a} | 👑 {l}",
            inline=False
        )

    await interaction.followup.send(embed=embed)

# 👥 GUILD MEMBERS
@bot.tree.command(name="guild_members")
async def guild_members(interaction: discord.Interaction, guild: str):

    await interaction.response.defer()

    members = database.get_guild_members(guild.upper())

    if not members:
        await interaction.followup.send("❌ No members")
        return

    text = ""

    for m in members:
        text += f"• <@{m.get('discord_id','')}>\n"
        text += f"IGN: {m['ign']} | Rank: {m['rank']}\n\n"

    embed = discord.Embed(
        title=f"{guild.upper()} Members",
        description=text[:4000],
        color=discord.Color.blue()
    )

    await interaction.followup.send(embed=embed)

# ➕ ADD GUILD
@bot.tree.command(name="add_guild")
async def add_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    database.add_guild(guild_name)

    await interaction.response.send_message(f"✅ {guild_name.upper()} added")

# ❌ REMOVE GUILD
@bot.tree.command(name="remove_guild")
async def remove_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    database.delete_guild(guild_name)

    await interaction.response.send_message(f"🗑 {guild_name.upper()} removed")

# ❌ REMOVE MEMBER
@bot.tree.command(name="remove_member")
async def remove_member(interaction: discord.Interaction, user: discord.Member):

    database.edit_user(str(user.id), guild="No Guild")

    await interaction.response.send_message(f"✅ Removed {user.name}")

# ✏️ EDIT PLAYER
@bot.tree.command(name="edit_player")
async def edit_player(interaction: discord.Interaction, user: discord.Member, ign: str, uid: str, guild: str, rank: str, joined: str):

    database.edit_user(str(user.id), ign=ign, uid=uid, guild=guild, rank=rank, joined=joined)

    await interaction.response.send_message("✅ Updated")

# 🏆 SET RANK
@bot.tree.command(name="set_rank")
async def set_rank(interaction: discord.Interaction, user: discord.Member, rank: str):

    database.edit_user(str(user.id), rank=rank.upper())

    await interaction.response.send_message(f"✅ {user.mention} is {rank}")

    try:
        await user.send(f"🔥 Your rank is now {rank}")
    except:
        pass

# 🔥 RUN
bot.run(TOKEN)