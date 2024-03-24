import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from utils.formatters import messages

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()
    
    @tasks.loop(minutes=30)
    async def change_status(self):
        """
        Change the bot's status periodically
        """

        await self.bot.wait_until_ready()

        status = next(messages)
        activity = discord.Activity(type=discord.ActivityType.watching, name=status)
        await self.bot.change_presence(activity=activity)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online!')

async def setup(bot):
    await bot.add_cog(EventsCog(bot))
