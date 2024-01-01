import discord 
from discord import app_commands, Interaction, ButtonStyle, Embed, Colour, FFmpegPCMAudio
from discord.ui import button, View
from discord.ext import commands
from youtube_dl import YoutubeDL
import logging

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio'}


class ButtonMenu(View):
    def __init__(self):
        super().__init__()

    @button(emoji="⏸️", style=ButtonStyle.blurple)
    async def pause(self, interaction: Interaction, button: button):
        await interaction.response.defer()
        voice_client = interaction.message.guild.voice_client
        if voice_client.is_playing():
            await interaction.followup.send("Paused", ephemeral=True)
            await voice_client.pause()
    
    @button(emoji="▶️", style=ButtonStyle.blurple)
    async def resume(self, interaction: Interaction, button: button):
        await interaction.response.defer()
        voice_client = interaction.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()

class MusicCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name='join', description='Make the bot join a voice channel')
    async def join_vc(self, interaction: Interaction):
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("`{}` is not connected to a voice channel".format(interaction.user.display_name))
            return
        else:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.followup.send("Bot is connected!")


    @app_commands.command(name='disconnect', description='Disconnect the bot from the voice channel')
    async def leave_vc(self, interaction: Interaction):
       await interaction.response.defer()
       voice_client = interaction.guild.voice_client
       if voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.followup.send("Bot Disconnected.")


    
    def play_next(self, interaction: Interaction):
        if len(self.song_queue) >= 1:
            song = self.song_queue.pop(0)

            guild = interaction.guild
            voice = guild.voice_client

            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(song, download=False)
                url2 = info['formats'][0]['url']
                song_title = info.get('title', None)

                voice.play(FFmpegPCMAudio(url2, **FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction))

                embed = Embed(title='Playing song', colour=Colour.dark_green())
                embed.add_field(name='Now Playing', value=song_title)

                view = ButtonMenu()
                asyncio.run_coroutine_threadsafe(interaction.followup.send(embed=embed, view=view), self.bot.loop)
    

    @app_commands.command(name='play', description='Play a song from Youtube')
    async def play(self, interaction: Interaction, song_url: str):
        await interaction.response.defer()
        self.song_queue.append(song_url)

        guild = interaction.guild
        voice = guild.voice_client

        if voice is None:
            await interaction.followup.send('Not connected to voice channel, use `/join` first.')
            return

        if not voice.is_playing():
            self.play_next(interaction)

        await interaction.followup.send("Song added to queue.")
    



async def setup(bot):
    await bot.add_cog(MusicCog(bot))
