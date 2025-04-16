from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

async def setup(bot):  # <-- this must be async
    await bot.add_cog(Basic(bot))  # <-- now correctly awaited
