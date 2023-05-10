import asyncio
import json
import os

import nextcord
from nextcord.ext import commands
import openai

## !Fix not being able to disable the ban hammer

openai.api_key = os.getenv("OPENAI_API_KEY")


class BanHammer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/ban_hammer_settings.json"
        if not os.path.isfile(self.settings_file):
            with open(self.settings_file, "w") as f:
                json.dump({}, f)
        with open("data/ban_hammer_warns.json", "r") as f:
            self.warns = json.load(f)

    def _load_settings(self):
        with open(self.settings_file, "r") as f:
            return json.load(f)

    def _save_settings(self, settings):
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)

    def _save_warns(self):
        with open("data/ban_hammer_warns.json", "w") as f:
            json.dump(self.warns, f)

    async def is_ban_hammer_enabled(self, guild_id):
        settings = self._load_settings()
        return settings.get(str(guild_id), {}).get("enabled", False)

    async def warn_user(self, user, guild):
        user_id = str(user.id)
        if user_id not in self.warns:
            self.warns[user_id] = 0
        self.warns[user_id] += 1
        self._save_warns()

        if self.warns[user_id] >= 5:
            # Temporarily ban the user for 3 days
            await user.ban(
                reason="Inappropriate messages detected by Ban Hammer",
                delete_message_days=0,
            )
            await asyncio.sleep(3 * 24 * 60 * 60)  # Wait for 3 days
            await guild.unban(user)
            self.warns[user_id] = 0
            self._save_warns()
            return True
        return False

    @nextcord.slash_command(
        name="banhammer", description="Enable or disable the Ban Hammer"
    )
    @commands.has_permissions(administrator=True)
    async def banhammer(self, interaction: nextcord.Interaction):
        settings = self._load_settings()
        guild_id = str(interaction.guild.id)
        enabled = settings.get(guild_id, {}).get("enabled", False)

        if enabled:
            settings[guild_id]["enabled"] = False
            message = "Ban Hammer has been disabled."
        else:
            if guild_id not in settings:
                settings[guild_id] = {}
            settings[guild_id]["enabled"] = True
            message = "Ban Hammer has been enabled."

        self._save_settings(settings)
        await interaction.send(message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not await self.is_ban_hammer_enabled(message.guild.id):
            return

        try:
            response = openai.Moderation.create(input=message.content)
            flagged = response["results"][0]["flagged"]
        except Exception as e:
            print(f"Error while calling OpenAI API: {e}")
            return

        if flagged:
            banned = await self.warn_user(message.author, message.guild)
            if banned:
                await message.channel.send(
                    f"{message.author.name} has been temporarily banned for 3 days due to inappropriate messages.")
            else:
                        warning_embed = nextcord.Embed(
                        title="Warning", color=nextcord.Color.red()
                        )
                        warning_embed.add_field(name="User", value=message.author.mention)
                        warning_embed.add_field(
                        name="Warnings", value=f"{self.warns[str(message.author.id)]}/5"
                        )
                        warning_embed.set_footer(
                        text="Reaching 5 warnings will result in a temporary ban for 3 days."
                        )
                        await message.channel.send(embed=warning_embed)
            try:
                        await message.author.send(warning_embed)
            except nextcord.errors.Forbidden:
                        pass
                    
                     # Delete the inappropriate message
            await message.delete()

            # Log the removed message to a channel
            log_channel_id = 1086313113130909793  # Replace with the ID of the channel to log to
            log_channel = message.guild.get_channel(log_channel_id)
            if log_channel is not None:
                embed = nextcord.Embed(
                    title="Removed Message", color=nextcord.Color.red()
                )
                embed.add_field(name="Author", value=message.author.mention)
                embed.add_field(name="Channel", value=message.channel.mention)
                embed.add_field(
                    name="Message", value=message.content, inline=False
                )
                await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(BanHammer(bot))
    print("BanHammer Ready!")
    
    
# using this is awesosme