from discord import Interaction, Embed, ButtonStyle
from discord.ui import View, button
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
