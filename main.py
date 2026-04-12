import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
import database

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔥 AUTO RANK
def get_rank(level):
    try:
        level = int(level)
    except:
        return "Member"

    if level >= 70:
        return "🔥 Legend"
    elif level >= 50:
        return "💎 Elite"
    elif level >= 30:
        return "⚡ Pro"
    else:
        return "👤 Member"

# 🔥 READY
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"✅ Synced {len(synced)} commands")
    print(f"🔥 Bot ready: {bot.user}")

# 🔥 MESSAGE HANDLER (Activity + Roles)
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    database.update_activity(str(message.author.id))

    # 🔥 ROLE COMMANDS (?FE01 @user)
    if message.content.startswith("?"):
    parts = message.content.split()

    if len(parts) >= 2:
        role_name = parts[0][1:]
        member = message.mentions[0] if message.mentions else None

        if not member:
            await message.channel.send("❌ Mention user")
            return

        role = discord.utils.find(
            lambda r: role_name.lower() in r.name.lower(),
            message.guild.roles
        )

        if role:
            await member.add_roles(role)
            await message.channel.send(f"✅ {member.mention} got {role.name}")
        else:
            await message.channel.send("❌ Role not found")

# 🔗 BIND
@bot.tree.command(name="bind", description="Link profile")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, rank: str, joined: str):

    if database.get_user(str(interaction.user.id)):
        await interaction.response.send_message("❌ Already linked!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    database.bind_user(str(interaction.user.id), ign, uid, guild.upper(), rank, joined)

    await interaction.followup.send("✅ Profile linked!")

# 👤 PROFILE
@bot.tree.command(name="profile", description="View profile")
async def profile(interaction: discord.Interaction, user: discord.Member = None):

    await interaction.response.defer()

    target = user or interaction.user
    data = database.get_user(str(target.id))

    if not data:
        await interaction.followup.send("❌ No profile found")
        return

    embed = discord.Embed(
        title=f"{target.name}'s Free Fire Profile",
        color=discord.Color.green()
    )

    embed.description = f"🟢 | Member of **{data['guild']}**"

    embed.add_field(
        name="🎮 Free Fire Max Details",
        value=f"IGN: `{data['ign']}`\nUID: `{data['uid']}`",
        inline=False
    )

    embed.add_field(
        name="🏠 Guild Information",
        value=f"Guild: `{data['guild']}`\nRank: `{data['rank']}`\nJoined: `{data['joined']}`",
        inline=False
    )

    embed.add_field(
        name="🔗 Discord Info",
        value=f"ID: `{target.id}`",
        inline=False
    )

    embed.set_footer(text=f"Requested by {interaction.user.name}")

    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)

    await interaction.followup.send(embed=embed)
# 🔍 SEARCH
@bot.tree.command(name="search_player", description="Search UID")
async def search_player(interaction: discord.Interaction, uid: str):

    await interaction.response.defer()

    try:
        url = f"https://free-ff-api-src-5plp.onrender.com/api/v1/account?region=IND&uid={uid}"
        res = requests.get(url, timeout=8)
        data = res.json()

        if "nickname" in data:
            name = data.get("nickname", "Unknown")
            level = data.get("level", 0)
            rank = get_rank(level)

            database.bind_user(str(interaction.user.id), name, uid, "AUTO", rank, "Auto")

            embed = discord.Embed(title=f"🔥 {name}", color=discord.Color.blue())
            embed.add_field(name="UID", value=uid)
            embed.add_field(name="Level", value=level)
            embed.add_field(name="Rank", value=rank)

            await interaction.followup.send(embed=embed)
            return

    except:
        pass

    await interaction.followup.send("❌ Player not found")

# 📊 GUILD list
@bot.tree.command(name="guild_list", description="Show all guilds")
async def guild_list(interaction: discord.Interaction):

    await interaction.response.defer()

    guilds = database.get_all_guilds()

    if not guilds:
        await interaction.followup.send("❌ No guilds found")
        return

    embed = discord.Embed(
        title="🏠 Guild List",
        color=discord.Color.blue()
    )

    for g in guilds:
        members = len(database.get_guild_members(g))
        embed.add_field(
            name=f"🔹 {g}",
            value=f"Members: {members}",
            inline=False
        )

    await interaction.followup.send(embed=embed)


# 👥 GUILD MEMBERS
@bot.tree.command(name="guild_members")
async def guild_members(interaction: discord.Interaction, guild: str):
    members = database.get_guild_members(guild.upper())
    msg = "\n".join([f"• {m['ign']} ({m['rank']})" for m in members]) or "No members"
    await interaction.response.send_message(msg)

#add GUILD 
@bot.tree.command(name="add_guild", description="Add new guild")
async def add_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    # fake entry for guild
    database.bind_user(f"guild_{guild_name}", "-", "-", guild_name, "-", "-")

    await interaction.followup.send(f"✅ Guild `{guild_name}` added")

#REMOVE GUILD 
@bot.tree.command(name="remove_guild", description="Delete guild")
async def remove_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    members = database.get_guild_members(guild_name)

    for m in members:
        database.bind_user("deleted", "-", "-", "Removed", "-", "-")

    await interaction.followup.send(f"🗑 Guild `{guild_name}` removed")

#REMOVE MEMBERS 
@bot.tree.command(name="remove_member", description="Remove member from guild")
async def remove_member(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    data = database.get_user(str(user.id))

    if not data:
        await interaction.followup.send("❌ User not found")
        return

    database.bind_user(str(user.id), data["ign"], data["uid"], "No Guild", data["rank"], data["joined"])

    await interaction.followup.send(f"✅ {user.name} removed from guild")




# 🔥 RUN
bot.run(TOKEN)