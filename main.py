import discord
from discord.ext import commands
import os
import database
import requests

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()   # 🔥 GLOBAL SYNC
        print(f"✅ Synced {len(synced)} commands globally")
    except Exception as e:
        print(e)

    print(f"🔥 Bot ready: {bot.user}")

# 🔗 Bind (ONLY ONCE)
@bot.tree.command(name="bind", description="Link your Free Fire profile")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, rank: str, joined: str):

    existing = database.get_user(str(interaction.user.id))

    if existing:
        await interaction.response.send_message("❌ Already linked!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    database.bind_user(str(interaction.user.id), ign, uid, guild, rank, joined)
    await interaction.followup.send("✅ Profile linked!", ephemeral=True)

# 👤 Player Info
@bot.tree.command(name="player_info", description="Show profile")
async def player_info(interaction: discord.Interaction):

    await interaction.response.defer()
    data = database.get_user(str(interaction.user.id))

    if data:
        discord_id, ign, uid, guild, rank, joined, created_at = data

        embed = discord.Embed(
            title=f"{interaction.user.name}'s Profile",
            color=discord.Color.green()
        )

        embed.add_field(name="IGN", value=f"`{ign}`", inline=False)
        embed.add_field(name="UID", value=f"`{uid}`", inline=False)
        embed.add_field(name="Guild", value=f"{guild} ({rank})", inline=False)
        embed.add_field(name="Joined", value=joined, inline=False)

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Use /bind first")


@bot.tree.command(name="search", description="Search by UID")
async def search(interaction: discord.Interaction, uid: str):

    await interaction.response.defer()

    try:
        url = f"https://api.gametools.network/ff/info?uid={uid}"
        res = requests.get(url, timeout=10)  # 🔥 timeout add
        data = res.json()

        if "data" in data and data["data"]:
            player = data["data"]

            embed = discord.Embed(
                title=player.get("name", "Player"),
                color=discord.Color.blue()
            )

            embed.add_field(name="UID", value=uid, inline=False)
            embed.add_field(name="Level", value=player.get("level", "N/A"), inline=True)
            embed.add_field(name="Rank", value=player.get("rank", "N/A"), inline=True)

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Player not found")

    except Exception as e:
        await interaction.followup.send("❌ API Error / Server Down")
 

# 📊 Guild List
@bot.tree.command(name="guild_list")
async def guild_list(interaction: discord.Interaction):

    await interaction.response.defer()
    guilds = database.get_all_guilds()

    msg = "🏠 Guilds:\n\n"
    for g in guilds:
        msg += f"• {g[0]}\n"

    await interaction.followup.send(msg)

# 👥 Guild Members
@bot.tree.command(name="guild_members")
async def guild_members(interaction: discord.Interaction, guild: str):

    await interaction.response.defer()
    members = database.get_guild_members(guild)

    msg = f"👥 {guild} Members:\n\n"
    for m in members:
        msg += f"• {m[1]} ({m[4]})\n"

    await interaction.followup.send(msg)

# 🔐 Admin Update
@bot.tree.command(name="update_player")
async def update_player(interaction: discord.Interaction, user: discord.Member, ign: str, uid: str, guild: str, rank: str, joined: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()
    database.bind_user(str(user.id), ign, uid, guild, rank, joined)
    await interaction.followup.send(f"✅ {user.name} updated")

# 🔥 LAST LINE
bot.run(TOKEN)