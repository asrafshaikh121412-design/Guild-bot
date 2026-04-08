import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")

    @bot.command()
    async def ping(ctx):
        await ctx.send("🏓 Pong!")

        @bot.command()
        async def hello(ctx):
            await ctx.send(f"Hello {ctx.author.mention} 👋")

            @bot.command()
            async def helpme(ctx):
                await ctx.send("Commands: !ping, !hello")

                @bot.event
                async def on_command_error(ctx, error):
                    await ctx.send("❌ Error")

                    keep_alive()
                    bot.run(TOKEN)