import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from utils.utils_checks import *
from utils.util_db import get_unconfirmed_snipes
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from cogs.game import send_snipe_confirmation

sys.stdout.reconfigure(line_buffering=True)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
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
        
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord, error: app_commands.AppCommandError):
        # print(f"[Error] Command: {interaction.command.name}, User: {interaction.user}, Guild: {interaction.guild}")
        if isinstance(error, (GameNotInitialized, MissingControlRole, NowSafeTime, app_commands.CheckFailure)):
            await safe_send(interaction, str(error))
            return
        else:
            await safe_send(interaction, str(error))

bot = MyBot(command_prefix='/', intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    print("Synced commands:")
    for cmd in bot.tree.get_commands():
        print(f"- {cmd.name}")

    await restart_unconfirmed_snipes()


@bot.event
async def on_guild_join(guild: discord.Guild):
    role = await make_role(guild)
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(f"Thanks for inviting UBC ACA Sniped Bot! Use `/initgame` to get started.\n Please give the role {role.mention} to all game moderators")
        return

    # Fallback: try to find another text channel with permission
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(f"Thanks for inviting UBC ACA Sniped Bot! Use `/initgame` to get started.\n Please give the role {role.mention} to all game moderators")
            break


async def restart_unconfirmed_snipes():
    snipes = get_unconfirmed_snipes()
    count = len(snipes)
    for snipe_id, snipe in snipes:
        if not snipe.channel:
            print(f"Skipping snipe {snipe_id}: no channel available")
            count -= 1 
            continue

        channel = bot.get_channel(snipe.channel)
        if not channel:
            print(f"Skipping snipe {snipe_id}: channel {snipe.channel} not found (probably left guild)")
            count -= 1 
            continue

        try:
            sniper = await bot.fetch_user(snipe.sniper_id)
            target = await bot.fetch_user(snipe.target_id)
        except Exception as e:
            print(f"[restart_unconfirmed_snipes] Failed to fetch users for snipe {snipe_id}: {e}")
            continue

        asyncio.create_task(
            send_snipe_confirmation(channel, snipe.guild_id, target, sniper, snipe_id),
            name=f"snipe-confirm-{snipe_id}"
        )
    print(f"[restart_unconfirmed_snipes] Restarted {count} unconfirmed snipes")

    return



async def main():
    async with bot:
        await bot.start(TOKEN)



#Testing for server health
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"ok")

def start_health_server():
    port = int(os.getenv("PORT", "8080"))
    httpd = HTTPServer(("0.0.0.0", port), HealthHandler)
    httpd.serve_forever()

threading.Thread(target=start_health_server, daemon=True).start()



asyncio.run(main())
