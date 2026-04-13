import discord
from discord.ext import commands
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
        return "👤 Member"

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

# 🔥 MESSAGE HANDLER (Role + Activity)
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    database.update_activity(str(message.author.id))

    # 🔥 ROLE COMMAND (?FE01 @user)
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

    await bot.process_commands(message)

# 🔗 BIND
@bot.tree.command(name="bind", description="Link profile")
async def bind(interaction: discord.Interaction, ign: str, uid: str, guild: str, joined: str):

    if database.get_user(str(interaction.user.id)):
        await interaction.response.send_message("❌ Already linked!", ephemeral=True)
        return

    await interaction.response.defer()

    database.bind_user(
        str(interaction.user.id),
        ign,
        uid,
        guild.upper(),
        "👤 Member",
        joined
    )

    # 🔥 AUTO ROLE
    role = discord.utils.find(
        lambda r: guild.lower() in r.name.lower(),
        interaction.guild.roles
    )

    if role:
        await interaction.user.add_roles(role)

    await interaction.followup.send("✅ Profile linked + Role assigned")

# 👤 PROFILE
@bot.tree.command(name="profile", description="View profile")
async def profile(interaction: discord.Interaction, user: discord.Member = None):

    await interaction.response.defer()

    target = user or interaction.user
    data = database.get_user(str(target.id))

    if not data:
        await interaction.followup.send("❌ No profile found")
        return

    # 🔥 Fake animated bar
    def progress_bar(level):
        filled = "🟩" * (level // 10)
        empty = "⬛" * (10 - (level // 10))
        return filled + empty

    level = 50  # tu chahe to dynamic bana sakta
    bar = progress_bar(level)

    embed = discord.Embed(
        title=f"🔥 {target.name}'s Profile",
        description="━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🎮 PLAYER INFO",
        value=f"➤ IGN: `{data['ign']}`\n➤ UID: `{data['uid']}`",
        inline=False
    )

    embed.add_field(
        name="🏠 GUILD STATUS",
        value=f"➤ Guild: `{data['guild']}`\n➤ Rank: `{data['rank']}`",
        inline=False
    )

    embed.add_field(
        name="📊 PROGRESS",
        value=f"{bar}\nLevel: `{level}`",
        inline=False
    )

    embed.add_field(
        name="📅 JOINED",
        value=f"`{data['joined']}`",
        inline=True
    )

    embed.add_field(
        name="🟢 STATUS",
        value="`Active Player`",
        inline=True
    )

    embed.set_footer(text="✨ Created by Asraf")

    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)

    await interaction.followup.send(embed=embed)

# 🔍 SEARCH
@bot.tree.command(name="search_player", description="Search player by UID")
async def search_player(interaction: discord.Interaction, uid: str):

    await interaction.response.defer()

    # 🔥 STEP 1: TRY API
    try:
        url = f"https://free-ff-api-src-5plp.onrender.com/api/v1/account?region=IND&uid={uid}"
        res = requests.get(url, timeout=8)

        if res.status_code == 200:
            data = res.json()

            if "nickname" in data:
                name = data.get("nickname", "Unknown")
                level = data.get("level", 0)

                embed = discord.Embed(
                    title=f"🔥 {name} (LIVE)",
                    color=discord.Color.blue()
                )

                embed.add_field(name="UID", value=uid)
                embed.add_field(name="Level", value=level)
                embed.set_footer(text="🌐 Data from API")

                await interaction.followup.send(embed=embed)
                return

    except:
        pass  # API fail → next step

    # 🔥 STEP 2: CHECK DATABASE
    data = database.get_user_by_uid(uid)

    if data:
        embed = discord.Embed(
            title=f"👤 {data['ign']} (DATABASE)",
            color=discord.Color.green()
        )

        embed.add_field(name="UID", value=data['uid'])
        embed.add_field(name="Guild", value=data['guild'])
        embed.add_field(name="Rank", value=data['rank'])

        embed.set_footer(text="💾 Stored data")

        await interaction.followup.send(embed=embed)
        return

    # 🔥 STEP 3: NOT FOUND
    await interaction.followup.send(
        "❌ Player not found\n\n👉 Ask player to use `/bind` first"
    )

# 📊 GUILD LIST
@bot.tree.command(name="guild_list", description="Show all guilds")
async def guild_list(interaction: discord.Interaction):

    await interaction.response.defer()

    guilds = database.get_all_guilds()

    if not guilds:
        await interaction.followup.send("❌ No guilds found")
        return

    embed = discord.Embed(
        title="🏠 Guild Overview",
        color=discord.Color.blue()
    )

    for g in guilds:
        members = database.get_guild_members(g)

        m = sum(1 for x in members if x.get("rank") == "MEMBER")
        o = sum(1 for x in members if x.get("rank") == "OFFICER")
        a = sum(1 for x in members if x.get("rank") == "AGL")
        l = sum(1 for x in members if x.get("rank") == "LEADER")

        embed.add_field(
            name=f"🔹 {g}",
            value=f"👥 Members: {m}\n🛡 Officer: {o}\n⚔ AGL: {a}\n👑 Leader: {l}",
            inline=False
        )

    embed.set_footer(text="Created by Asraf 🔥")

    await interaction.followup.send(embed=embed)

# 👥 GUILD MEMBERS
@bot.tree.command(name="guild_members", description="Show guild members")
async def guild_members(interaction: discord.Interaction, guild: str):

    await interaction.response.defer()

    members = database.get_guild_members(guild.upper())

    if not members:
        await interaction.followup.send("❌ No members found")
        return

    embed = discord.Embed(
        title=f"👥 {guild.upper()} Members",
        description=f"Total Members: **{len(members)}**",
        color=discord.Color.blue()
    )

    text = ""
    for m in members:
        text += f"• <@{m.get('discord_id','')}>\n"
        text += f"IGN: `{m['ign']}` | UID: `{m['uid']}`\n"
        text += f"Rank: `{m['rank']}`\n\n"

    embed.description += "\n\n" + text[:4000]

    embed.set_footer(text="Created by Asraf 🔥")

    await interaction.followup.send(embed=embed)


# ➕ ADD GUILD
@bot.tree.command(name="add_guild", description="Add guild")
async def add_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    database.add_guild(guild_name)

    await interaction.followup.send(f"✅ Guild `{guild_name.upper()}` added")

# ❌ REMOVE GUILD
@bot.tree.command(name="remove_guild", description="Remove guild")
async def remove_guild(interaction: discord.Interaction, guild_name: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    database.delete_guild(guild_name)

    await interaction.followup.send(f"🗑 Guild `{guild_name.upper()}` removed")

# ❌ REMOVE MEMBER
@bot.tree.command(name="remove_member", description="Remove member")
async def remove_member(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    success = database.edit_user(str(user.id), guild="No Guild")

    if not success:
        await interaction.followup.send("❌ User not found")
        return

    await interaction.followup.send(f"✅ {user.name} removed")

# ✏️ EDIT PLAYER
@bot.tree.command(name="edit_player", description="Edit player")
async def edit_player(interaction: discord.Interaction, user: discord.Member, ign: str, uid: str, guild: str, rank: str, joined: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    await interaction.response.defer()

    success = database.edit_user(
        str(user.id),
        ign=ign,
        uid=uid,
        guild=guild,
        rank=rank,
        joined=joined
    )

    if not success:
        await interaction.followup.send("❌ User not found")
        return

    embed = discord.Embed(title="✅ Player Updated", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Guild", value=guild.upper())

    await interaction.followup.send(embed=embed)

#SET RANK
@bot.tree.command(name="set_rank")
async def set_rank(interaction: discord.Interaction, user: discord.Member, rank: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    database.edit_user(str(user.id), rank=rank.upper())

    await interaction.response.send_message(
        f"✅ {user.mention} is now {rank.upper()}"
    )

    # 🔥 DM MESSAGE (2nd screenshot style)
    try:
        embed = discord.Embed(
            title="🔔 Profile Updated",
            description=f"Your rank has been updated by an admin.",
            color=discord.Color.green()
        )

        embed.add_field(name="New Rank", value=f"`{rank}`")
        embed.set_footer(text="Created by Asraf 🔥")

        await user.send(embed=embed)
    except:
        pass

# 🔥 RUN
bot.run(TOKEN)