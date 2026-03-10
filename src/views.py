import discord
from discord.ui import View, Button

class ConfirmDeleteView(View):
    def __init__(self, timeout=30):
        super().__init__(timeout=timeout)
        self.confirmed = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.confirmed = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="✅ Confirmed.", view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.confirmed = False
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="❌ Cancelled.", view=self)
        self.stop()


class ConfirmSnipeView(View):
    def __init__(self, guild_id: int, target: discord.Member, timeout=7200):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.target = target
        self.confirmed = None


    async def interaction_check(self, interaction: discord.Interaction) -> bool: # Prevents other users from confirming/denying snipe
        """Only allow the target to press buttons."""
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the targeted player can confirm or reject this snipe.",
                ephemeral=True
            )
            return False
        return True
    

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        for item in self.children:
            item.disabled = True
        self.confirmed = True
        await interaction.response.edit_message(content="✅ Snipe Confirmed.", view=self)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: Button):
        for item in self.children:
            item.disabled = True
        self.confirmed = False
        await interaction.response.edit_message(content="❌ Snipe Denied.", view=self)
        self.stop()

        