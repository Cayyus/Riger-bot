import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from paginator import ButtonPaginator
from staticvalues import timestamp_formatting

class RoleDump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='dump', description='List out members of specific roles')
    async def dump(self, interaction: Interaction, role: discord.Role, per_page: int = None):
        await interaction.response.defer()

        members = role.members
        embeds = []
        pages = 0

        if per_page is None:
            pages = 5
        else:
            pages = per_page

        for i in range(0, len(members), pages):
            member_slice = members[i:i + pages] #members sliced into group of 5

            embed = Embed(title=f'Members of {role.name}', colour=role.colour)

            for member in member_slice:
                name = member.name
                member_id = member.id
                member_info = f'{name} - {member_id}'
                embed.add_field(name="Member - ID", value=member_info, inline=False)
            embeds.append(embed)
        
        role_created = timestamp_formatting(role.created_at)
        total_members = len(role.members)
        role_id = role.id

        role_info = Embed(title=role.name, colour=role.colour)
        role_info.add_field(name = 'Role Created', value=role_created)
        role_info.add_field(name = 'Total Members', value=total_members)
        role_info.set_footer(text=f'Role ID: {role_id}')

        paginator = ButtonPaginator(pages=embeds, per_page=1)
        await interaction.followup.send(embed=role_info, view=paginator)

    
async def setup(bot):
    await bot.add_cog(RoleDump(bot))
