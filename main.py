import discord
from discord.ext import commands
from discord import app_commands
import os
import database

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot online: {bot.user}")

# 🔗 Bind command
@tree.command(name="bind", description="Link your Free Fire profile")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, rank: str, joined: str):

    await interaction.response.defer(ephemeral=True)

    database.bind_user(str(interaction.user.id), ign, uid, guild, rank, joined)

    await interaction.followup.send("✅ Profile linked successfully!", ephemeral=True)

# 👤 Player info (EMBED)
@tree.command(name="player_info", description="Show your profile")
async def player_info(interaction: discord.Interaction):

    await interaction.response.defer()

    data = database.get_user(str(interaction.user.id))

    if data:
        discord_id, ign, uid, guild, rank, joined, created_at = data

        embed = discord.Embed(
            title=f"{interaction.user.name}'s Free Fire Profile",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🎮 Free Fire Max Details",
            value=f"IGN: `{ign}`\nUID: `{uid}`",
            inline=False
        )

        embed.add_field(
            name="🏠 Guild Information",
            value=f"Guild: `{guild}`\nRank: `{rank}`\nJoined: `{joined}`",
            inline=False
        )

        embed.add_field(
            name="🔗 Discord ID",
            value=f"`{discord_id}`",
            inline=False
        )

        embed.set_footer(text=f"{rank} of {guild}")
        
        if interaction.user.avatar:
            embed.set_thumbnail(url=interaction.user.avatar.url)

        await interaction.followup.send(embed=embed)

    else:
        await interaction.followup.send("❌ No data found. Use /bind first.")

bot.run(TOKEN)
# 🔍 Search by UID
@tree.command(name="search", description="Search player by UID")
async def search(interaction: discord.Interaction, uid: str):
    await interaction.response.defer()

    data = database.get_user_by_uid(uid)

    if data:
        discord_id, ign, uid, guild, rank, joined, created_at = data

        embed = discord.Embed(title=f"{ign} Profile", color=discord.Color.blue())
        embed.add_field(name="UID", value=f"`{uid}`", inline=False)
        embed.add_field(name="Guild", value=f"{guild} ({rank})", inline=False)
        embed.add_field(name="Joined", value=joined, inline=False)

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Player not found")

# 📊 Guild list
@tree.command(name="guild_list", description="Show all guilds")
async def guild_list(interaction: discord.Interaction):
    await interaction.response.defer()

    guilds = database.get_all_guilds()

    if not guilds:
        await interaction.followup.send("❌ No guilds found")
        return

    msg = "🏠 Guild List:\n\n"
    for g in guilds:
        msg += f"• {g[0]}\n"

    await interaction.followup.send(msg)

# 👥 Guild members
@tree.command(name="guild_members", description="Show guild members")
async def guild_members(interaction: discord.Interaction, guild: str):
    await interaction.response.defer()

    members = database.get_guild_members(guild)

    if not members:
        await interaction.followup.send("❌ No members found")
        return

    msg = f"👥 Members of {guild}:\n\n"
    for m in members:
        msg += f"• {m[1]} ({m[4]})\n"

    await interaction.followup.send(msg)

# 🔐 Admin only update
ADMIN_ID =  1270326626302955520 # 🔥 yaha apna Discord ID daal

@tree.command(name="update_player", description="Admin update player")
async def update_player(interaction: discord.Interaction, user: discord.Member, ign: str, uid: str, guild: str, rank: str, joined: str):

    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("❌ Admin only command", ephemeral=True)
        return

    await interaction.response.defer()

    database.bind_user(str(user.id), ign, uid, guild, rank, joined)
    await interaction.followup.send(f"✅ {user.name} updated")
#bind
@tree.command(name="bind", description="Link your Free Fire profile")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, rank: str, joined: str):

    existing = database.get_user(str(interaction.user.id))

    # 🔒 Already bound check
    if existing:
        await interaction.response.send_message("❌ You already linked your profile! Contact admin to update.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    database.bind_user(str(interaction.user.id), ign, uid, guild, rank, joined)

    await interaction.followup.send("✅ Profile linked successfully!", ephemeral=True)