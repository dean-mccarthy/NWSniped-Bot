import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))
APPLICATION_ID = os.getenv('APPLICATION_ID')


intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):
    async def setup_hook(self):
        # Load all cogs before on_ready
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Loaded extension: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

bot = MyBot(command_prefix='/', intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    guild = discord.Object(id=SERVER_ID)
    await bot.tree.sync()
    await bot.tree.sync(guild=guild)
    print("Synced commands:")
    for cmd in bot.tree.get_commands():
        print(f"- {cmd.name}")


async def main():
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())
