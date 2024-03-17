from discord.ext import commands
from discord import app_commands, Interaction, File

from gtts import gTTS
import os

class LeisureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def sound_to_text(self, input):
        tts = gTTS(text=input, lang='en')
        filename = 'voice.mp3'
        tts.save(filename)
        return filename

    @app_commands.command(name='tts', description='Turn text into voice')
    async def tts(self, interaction: Interaction, text: str, dm: bool = False):
        await interaction.response.defer()
        file = self.sound_to_text(text)
        if dm:
            channel = await interaction.user.create_dm()
            await channel.send("Here's your file:", file=File(file))
            os.remove(file)
            await interaction.followup.send("Sent!", ephemeral=True)
        else:
            await interaction.followup.send("Here's your file:", file=File(file))
            os.remove(file)
    
async def setup(bot):
    await bot.add_cog(LeisureCog(bot))
