import random
import discord
from discord import app_commands
from discord.ext import commands
import os
from util import *

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snipe", description="Snipe a player!")
    @app_commands.describe(player="Select the player to snipe")
    async def snipe(self, interaction: discord.Interaction, player: discord.Member):
        """
        Command called when player wishes to submit a snipe of another player
        Game rules indicate an image must precede or follow this command featuring the snipe

        Args:
            player (discord.Member): The target being sniped

        Returns:
            Message in chat announcing the snipe
            Snipe is recorded into datafiles
            TODO: Ephemeral message to the target requesting confirmation of snipe
        """
        guild_id = interaction.guild.id

        data = load_data(guild_id)
        target_id = str(player.id)
        sniper_id = str(interaction.user.id)

        if sniper_id not in data["users"]:
            await interaction.response.send_message("You are not in the game!", ephemeral=True)
            return

        if target_id not in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is not in the game!", ephemeral=True)
            return
        if target_id == sniper_id:
            await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
            return
        
        data["users"][sniper_id].snipes += 1
        data["users"][target_id].times_sniped += 1

        save_data(guild_id, data)

        message = get_snipe_message(interaction.user, player) #uses raw discord members since mention needs discord ids instead of strings
        print(message)
        await interaction.response.send_message(message)


def get_snipe_message(sniper, target):
    """
    Returns a randomly chosen snipe message using Discord mentions.

    Args:
        sniper (discord.Member): The player who performed the snipe.
        target (discord.Member): The player who got sniped.

    Returns:
        str: A message string including mentions.
    """
    sniper_mention = sniper.mention
    target_mention = target.mention

    sayings = [
        # Savage / Competitive
        f"Boom! Headshot. {sniper_mention} sniped {target_mention}.",
        f"{sniper_mention} caught {target_mention} lackin'",
        f"{target_mention} never saw it coming. {sniper_mention} kills + 1",
        f"One shot, one kill. {sniper_mention} shot down {target_mention}.",
        f"{sniper_mention} just made {target_mention} their latest highlight reel.",
        
        # Stealthy / Sneaky
        f"Silently and swiftly, {sniper_mention} took down {target_mention}.",
        f"{target_mention} just learned to check their six—thanks to {sniper_mention}.",
        f"Sneaky little snipe by {sniper_mention} on {target_mention}.",
        f"In the shadows, {sniper_mention} strikes. Farewell, {target_mention}.",
    ]

    return random.choice(sayings)



        
async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))