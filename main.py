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
            role_name = parts[0][1:].upper()
            member = message.mentions[0] if message.mentions else None

            if not member:
                await message.channel.send("❌ Mention user")
                return

            role = discord.utils.get(message.guild.roles, name=role_name)

            if role:
                await member.add_roles(role)
                await message.channel.send(f"✅ {member.mention} got {role_name}")
            else:
                await message.channel.send("❌ Role not found")

    await bot.process_commands(message)

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

    if data:
        embed = discord.Embed(title=f"🔥 {target.name}'s Profile", color=discord.Color.green())

        embed.add_field(name="IGN", value=data["ign"], inline=False)
        embed.add_field(name="UID", value=data["uid"], inline=False)
        embed.add_field(name="Guild", value=data["guild"], inline=True)
        embed.add_field(name="Rank", value=data["rank"], inline=True)
        embed.add_field(name="Last Active", value=data.get("last_active", "N/A"), inline=False)

        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ User not found")

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

# 📊 GUILD LIST
@bot.tree.command(name="guild_list")
async def guild_list(interaction: discord.Interaction):
    guilds = database.get_all_guilds()
    msg = "\n".join([f"• {g}" for g in guilds]) or "No guilds"
    await interaction.response.send_message(msg)

# 👥 GUILD MEMBERS
@bot.tree.command(name="guild_members")
async def guild_members(interaction: discord.Interaction, guild: str):
    members = database.get_guild_members(guild.upper())
    msg = "\n".join([f"• {m['ign']} ({m['rank']})" for m in members]) or "No members"
    await interaction.response.send_message(msg)

# 🔥 RUN
bot.run(TOKEN)