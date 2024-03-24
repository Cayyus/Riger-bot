from discord import app_commands, Interaction, ButtonStyle, Embed, Colour, FFmpegPCMAudio
from discord.ui import button, View
from discord.ext import commands

from youtube_dl import YoutubeDL
from asyncio import run_coroutine_threadsafe
from googleapiclient.discovery import build

from dotenv import load_dotenv
import os

load_dotenv('tokens.env')

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
        self.song_queue = []


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

    def play_next(self, interaction: Interaction) -> None:
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
                run_coroutine_threadsafe(interaction.followup.send(embed=embed, view=view), self.bot.loop)
    
    @app_commands.command(name = 'search_songs', description='Search songs on YouTube')
    async def search_songs(self, interaction: Interaction, query: str):
        await interaction.response.defer()
        if not interaction.user.voice:
            await interaction.followup.send("`{}` is not connected to a voice channel".format(interaction.user.display_name))
            return
        
        title_lst, channel_lst, link_lst = [], [], []
        embed = Embed(title = 'Results')

        youtube = build('youtube', 'v3', developerKey=os.environ.get('YT_API_KEY'))
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=10
        ).execute()

        # Iterate through each item in the search response
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                # Extract video details
                video_id = search_result['id']['videoId']
                video_title = search_result['snippet']['title']
                channel_name = search_result['snippet']['channelTitle']


                title_lst.append(video_title)
                channel_lst.append(channel_name)
                link_lst.append(f"https://www.youtube.com/watch?v={video_id}")

        
        for title, channel, vid_link in zip(title_lst, channel_lst, link_lst):
            embed.add_field(name='\u200b', value = f"{title} - {channel}\n{vid_link}")
        
        await interaction.followup.send(embed=embed)

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
        
