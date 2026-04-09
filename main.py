import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
import database

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot online: {bot.user}")

# Guild add
@tree.command(name="guild_add")
async def guild_add(interaction: discord.Interaction, name: str):
    database.add_guild(name)
    await interaction.response.send_message(f"✅ Guild '{name}' added")

# Remove guild
@tree.command(name="remove_guild")
async def remove_guild(interaction: discord.Interaction, name: str):
    database.remove_guild(name)
    await interaction.response.send_message(f"❌ Guild '{name}' removed")

# Add player
@tree.command(name="add_player")
async def add_player(interaction: discord.Interaction, player: str, guild: str):
    if database.add_player(player, guild):
        await interaction.response.send_message(f"✅ Player '{player}' added to {guild}")
    else:
        await interaction.response.send_message("❌ Guild not found")

# Remove player
@tree.command(name="remove_player")
async def remove_player(interaction: discord.Interaction, player: str):
    database.remove_player(player)
    await interaction.response.send_message(f"❌ Player '{player}' removed")

# Player info
@tree.command(name="player_info")
async def player_info(interaction: discord.Interaction, player: str):
    data = database.get_player(player)
    if data:
        await interaction.response.send_message(f"👤 {data[0]} | Guild: {data[1]}")
    else:
        await interaction.response.send_message("❌ Player not found")

keep_alive()
bot.run(TOKEN)