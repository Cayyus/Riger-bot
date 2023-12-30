import discord
from discord.ext import commands
from discord import app_commands
from discord import Colour, Interaction
from datetime import datetime
from db_config import UserDB

class PayGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = 'pay', description='Gives 100 coins')
    async def pay(self, interaction: Interaction):
        user = interaction.user
        username = user.name
        usr_id = user.id
        coins = 100
        last_ran = int(interaction.created_at.timestamp())

        db = UserDB(username, usr_id, coins, last_ran)
        db_user = db.select_user()

        if db_user: #if user in db
            db.update_coin_count()
            db.update_timestamp()
            await interaction.response.send_message("Here's your coins! (+100 credit)")

        else: #if user not in db
            db.insert_user()
            await interaction.response.send_message("Here are your coins, enjoy! (+100 credit)")
        
async def setup(bot):
    await bot.add_cog(PayGame(bot))