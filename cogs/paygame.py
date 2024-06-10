from discord.ext import commands
from discord import app_commands
from discord import Interaction
from utils.db.db_config import UserDB
from utils.paginators.leaderboard_paginator import LeaderboardPaginator

class PayGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='pay', description='Gives 100 coins')
    async def pay(self, interaction: Interaction):
        await interaction.response.defer()
        user = interaction.user
        username = user.name
        usr_id = user.id
        coins = 100

        db = UserDB(username, usr_id, coins)
        db_user = db.select_user()
        current_time = int(interaction.created_at.timestamp())

        if db_user:  # if user in db
            db_last_ran = db.get_last_played()
            timeout = int(db_last_ran) + 7200  # Add 2 hours to the last run time

            if current_time < timeout:
                await interaction.followup.send(f'Timeout! Please try again <t:{timeout}:R>.', ephemeral=True)
            else:
                db.update_coin_count(amount=coins)
                db.update_timestamp(current_time)
                await interaction.followup.send("Here's your coins! (+100 credit)")

        else:  # if user not in db
            db.insert_user()
            db.update_timestamp(current_time)
            await interaction.followup.send("Here are your coins, enjoy! (+100 credit)")
    
    @app_commands.command(name = 'leaderboard', description='See who has the most coins')
    async def leaderboard(self, interaction: Interaction):
        #format to put in : 
        """
        main list = []
        sublists = [[], []]

        [['James', 100], ['John', 200]]
        """

        await interaction.response.defer()
        data_list = []
        db = UserDB()

        sorted_users = db.get_coin_count_all()
        
        for name, coin in sorted_users.items():
            data_list.append([name, coin])

        data_list.sort(key=lambda x: x[1], reverse=True)
        
        paginator = LeaderboardPaginator(interaction, data_list)
        await paginator.show_page(1)

async def setup(bot):
    await bot.add_cog(PayGame(bot))
