import nextcord
from nextcord.ext import commands

class CogManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def unload(self, ctx, cog):
        try:
            self.bot.unload_extension(cog)
            await ctx.send(f"Unloaded {cog}")
        except Exception as e:
            await ctx.send(f"Error unloading {cog}: {e}")

    @commands.command()
    async def reload(self, ctx, cog):
        try:
            self.bot.reload_extension(cog)
            await ctx.send(f"Reloaded {cog}")
        except Exception as e:
            await ctx.send(f"Error reloading {cog}: {e}")

    @commands.command()
    async def load(self, ctx, cog):
        try:
            self.bot.load_extension(cog)
            await ctx.send(f"Loaded {cog}")
        except Exception as e:
            await ctx.send(f"Error loading {cog}: {e}")

def setup(bot):
    bot.add_cog(CogManagement(bot))
