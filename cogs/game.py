import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import check
import os
from dotenv import load_dotenv
from utils.util_db import *
from utils.utils_checks import *
from views import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class SayingsType(Enum):
    SNIPE = "snipe"
    DENY = "deny"
    SUBMIT = "submit"
    MULTIKILL = "multikill"

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snipe", description="Snipe a player!")
    @app_commands.describe(player="Select the player to snipe")
    @check(check_initialized)
    @check(check_safetime)
    async def snipe(self, interaction: discord.Interaction, player: discord.Member):
        """
        Command called when player wishes to submit a snipe of another player
        Game rules indicate an image must precede or follow this command featuring the snipe

        Args:
            player (discord.Member): The target being sniped

        Returns:
            Message in chat announcing the snipe
            Snipe is recorded into datafiles
        """
        
        guild_id = interaction.guild.id
        target_id = player.id
        sniper_id = interaction.user.id

        if target_id == sniper_id:
            await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
            return
        if not get_player(guild_id, sniper_id):
            await interaction.response.send_message("You are not in the game!", ephemeral=True)
            return

        if not get_player(guild_id, target_id):
            await interaction.response.send_message(f"{player.display_name} is not in the game!", ephemeral=True)
            return

        snipe_id = make_snipe(guild_id, sniper_id, target_id, interaction.channel_id) # Init snipe
        
        message = get_snipe_message(interaction.user, player, SayingsType.SUBMIT) #uses raw discord members for mention
        # print(message)
        await interaction.response.send_message(message)

        await send_snipe_confirmation(interaction, guild_id, player, snipe_id)

    # @app_commands.command(name="snipeception", description="Snipe a player while they are sniping another player")
    # @app_commands.describe(player="Select the player to snipeception")
    # @check(check_initialized)
    # @check(check_safetime)
    # async def snipeception(self, interaction: discord.Interaction, player: discord.Member):
    #     """
    #     Command called when player wishes to submit a snipe of another player
    #     Game rules indicate an image must precede or follow this command featuring the snipe

    #     Args:
    #         player (discord.Member): The target being sniped

    #     Returns:
    #         Message in chat announcing the snipe
    #         Snipe is recorded into datafiles
    #         TODO: Ephemeral message to the target requesting confirmation of snipe
    #     """
    #     guild_id = interaction.guild.id
    #     target_id = player.id
    #     sniper_id = interaction.user.id

    #     if target_id == sniper_id:
    #         await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
    #         return
    #     if not get_player(guild_id, sniper_id):
    #         await interaction.response.send_message("You are not in the game!", ephemeral=True)
    #         return

    #     if not get_player(guild_id, target_id):
    #         await interaction.response.send_message(f"{player.display_name} is not in the game!", ephemeral=True)
    #         return

    #     snipe_id = make_snipe(guild_id, sniper_id, target_id) # Init snipe
        
    #     message = get_snipe_message(interaction.user, player, SayingsType.SUBMIT) #uses raw discord members for mention
    #     # print(message)
    #     await interaction.response.send_message(message)

    #     await send_snipe_confirmation(interaction, guild_id, player, snipe_id)

        

async def send_snipe_confirmation(interaction: discord.Interaction, guild_id, target, snipe_id):
    while True:
        view = ConfirmSnipeView(guild_id, target)
        msg = await interaction.followup.send(
            f"{target.mention}, please confirm or deny the snipe",
            view=view
        )
        await view.wait()

        if view.confirmed is True:
            confirm_snipe(snipe_id)
            message = get_snipe_message(interaction.user, target, SayingsType.SNIPE)
            await interaction.followup.send(message)
            break
        
        elif view.confirmed is False:
            remove_snipe_by_id(snipe_id)
            message = get_snipe_message(interaction.user, target, SayingsType.DENY)
            await interaction.followup.send(message)
            break
        
        elif view.confirmed is None:
            try:
                await msg.delete()
            except discord.NotFound:
                pass
    return
            




def get_snipe_message(sniper, target, type: SayingsType):
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
    sayings = []
    match type:
        case SayingsType.SNIPE:
            sayings = [
                f"Boom! Headshot. {sniper_mention} sniped {target_mention}.",
                f"{sniper_mention} caught {target_mention} lackin'",
                f"{target_mention} never saw it coming. {sniper_mention} kills + 1",
                f"One shot, one kill. {sniper_mention} shot down {target_mention}.",
                f"{sniper_mention} just made {target_mention} their latest highlight reel.",
                
                f"Silently but deadly, {sniper_mention} took down {target_mention}.",
                f"{target_mention} just learned to check their six—thanks to {sniper_mention}.",
                f"Sneaky little snipe by {sniper_mention} on {target_mention}.",
                f"In the shadows, {sniper_mention} strikes. Farewell, {target_mention}.",
                f"{sniper_mention} says it's high noon. So long {target_mention}"
            ]
        
        case SayingsType.DENY:
            sayings = [
                f"Mission failed {sniper_mention}, we'll get em next time",
                f"{target_mention} lives to see another day",
                f"Recalibrate your sights {sniper_mention}, you failed the shot on {target_mention}",
                f"Not today {sniper_mention}, not today --{target_mention}",
                f"WOOOOOOSH! {sniper_mention} missed the shot on {target_mention}",
                f"{target_mention} detonated spike before {sniper_mention} could clutch the ace"
            ]
        
        case SayingsType.SUBMIT:
            sayings = [
                f"{sniper_mention} has {target_mention} in their sights",
                f"{target_mention}! {sniper_mention} on the rooftops!",
                f"President {target_mention}, get down! {sniper_mention} is approaching!",
                f"Shots fired at {target_mention} by {sniper_mention}",
            ]
        

    return random.choice(sayings)



        
async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))
