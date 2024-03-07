from discord.ext import commands
from discord import app_commands, ButtonStyle
from discord import Interaction, Embed, Button
from discord.ui import View, button
from db_config import UserDB
from tabulate import tabulate

class LeaderboardPaginator(View):
    def __init__(self, interaction: Interaction, data: list[list, list]) -> None:
        super().__init__(timeout=180.0)
        self.interaction = interaction
        self.embed = Embed(title='Leaderboard')
        self.data = data
        self.headers = ['Name', 'Coins']
        self.current_page = 1
        self.per_page = 10
        self.total_pages = (len(self.data) - 1) // self.per_page + 1
    
    async def format_page(self, page_num):
        start_index = (page_num - 1) * self.per_page
        end_index = min(page_num * self.per_page, len(self.data))
        page_data = self.data[start_index:end_index]

        formatted_table = tabulate(page_data, headers=self.headers, tablefmt='pipe')

        return f"```\n{formatted_table}\n```"
        
    async def show_page(self, page_num):
        self.previous_page.disabled = self.current_page == 1
        self.next_page.disabled = self.current_page == self.total_pages

        page_content = await self.format_page(page_num)
        self.embed.description = page_content
        await self.interaction.edit_original_response(embed=self.embed, view=self)

    @button(label='<', style=ButtonStyle.blurple)
    async def previous_page(self, interaction: Interaction, button: button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.show_page(self.current_page)
    
    @button(label='>', style=ButtonStyle.blurple)
    async def next_page(self, interaction: Interaction, button: button):
        await interaction.response.defer()
        self.current_page +=  1
        await self.show_page(self.current_page)


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
                db.update_coin_count()
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
