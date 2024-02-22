from discord.ext import commands
from discord import app_commands
from discord import Interaction, Member, Embed
from db_config import UserDB
from tabulate import tabulate

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
            timeout = int(db_last_ran) + 10800  # Add 3 hours to the last run time

            if current_time < timeout:
                await interaction.followup.send(f'Timeout! Please try again <t:{timeout}:R>.')
            else:
                db.update_coin_count()
                db.update_timestamp(current_time)
                await interaction.followup.send("Here's your coins! (+100 credit)")

        else:  # if user not in db
            db.insert_user()
            db.update_timestamp(current_time)
            await interaction.followup.send("Here are your coins, enjoy! (+100 credit)")
    
    @app_commands.command(name = 'leaderboard', description='See who has the most coins')
    async def leaderboard(self, interaction: Interaction, rank: Member = None):
        db = UserDB()
        sorted_users = db.get_coin_count_all()
        sorted_users = sorted(sorted_users.items(), key=lambda x: x[1], reverse=True)

        # Prepare data for tabulate
        table_data = [[idx+1, user, str(coins)] for idx, (user, coins) in enumerate(sorted_users)]
        table_data.insert(0, ['#', 'Name', 'Coins']) # Insert headers

        # Generate table
        table = tabulate(table_data, headers='firstrow', tablefmt='pipe', numalign='right', stralign='center')
        
        embed = Embed(title = 'Econony Leaderboard')
        embed.add_field(name='', value=f'```{table}```')
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(PayGame(bot))
