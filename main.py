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
    database.bind_user(str(interaction.user.id), ign, uid, guild, rank, joined)
    await interaction.response.send_message("✅ Profile linked successfully!", ephemeral=True)

# 👤 Player info (EMBED STYLE)
@tree.command(name="player_info", description="Show your profile")
async def player_info(interaction: discord.Interaction):
    data = database.get_user(str(interaction.user.id))

    if data:
        discord_id, ign, uid, guild, rank, joined = data

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
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else "")

        await interaction.response.send_message(embed=embed)

    else:
        await interaction.response.send_message("❌ No data found. Use /bind first.")

bot.run(TOKEN)