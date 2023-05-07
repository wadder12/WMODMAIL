import nextcord
from nextcord.ext import commands

class NoDirectVideo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_ids = [1098322179252297909] # Replace with the IDs of the channels you want to send notifications to
        self.allowed_ids = [9876543210] # Replace with the IDs of the users allowed to send videos without links

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message author is a bot or if the message is in a DM
        if message.author.bot or isinstance(message.channel, nextcord.DMChannel):
            return

        # Check if the message has any attachments
        if message.attachments:
            for attachment in message.attachments:
                # Check if the attachment is a video
                if attachment.content_type.startswith("video"):
                    # Check if the message author's ID is in the allowed IDs list
                    if message.author.id not in self.allowed_ids:
                        # Send an embed prompt for the user to upload the video to a file sharing service
                        embed = nextcord.Embed(title="Direct video upload not allowed", color=nextcord.Color.red())
                        embed.add_field(name="Reason", value="Direct video upload not allowed in this channel. Please upload your video to a file sharing service and provide the link instead.", inline=False)
                        await message.channel.send(embed=embed)
                        # Delete the user's message
                        deleted_message = message.content
                        await message.delete()
                        # Send a notification to all designated channels
                        for channel_id in self.channel_ids:
                            channel = self.bot.get_channel(channel_id)
                            embed = nextcord.Embed(title="Direct video upload deleted", color=nextcord.Color.red())
                            embed.add_field(name="Deleted message", value=deleted_message, inline=False)
                            embed.add_field(name="User", value=message.author.mention, inline=False)
                            embed.add_field(name="Reason", value="Direct video upload not allowed in this channel", inline=False)
                            embed.add_field(name="Uploaded video URL", value=attachment.url, inline=False)
                            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(NoDirectVideo(bot))



