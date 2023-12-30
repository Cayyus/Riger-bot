import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class AutoRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='role', description='Gives a specified role to a member or multiple members')
    async def roles(self, interaction: discord.Interaction, role: discord.Role, members: str):
        await interaction.response.defer()
        await process_role_action(interaction, role, members, add=True)
        await interaction.followup.send('Done.')

    @app_commands.command(name='derole', description='Removes a specified role from a member or multiple members')
    async def derole(self, interaction: discord.Interaction, role: discord.Role, members: str):
        await interaction.response.defer()
        await process_role_action(interaction, role, members, add=False)
        await interaction.followup.send('Done.')

async def process_role_action(interaction, role, members, add=True):
    member_ids = extract_member_ids(members)
    guild = interaction.guild

    for member_id in member_ids:
        server_member = discord.utils.get(guild.members, id=member_id)

        if server_member is not None:
            if add:
                await server_member.add_roles(role)
            else:
                await server_member.remove_roles(role)
            await asyncio.sleep(1)  # Rate limit

def extract_member_ids(members):
    member = members.split(' ')
    split_1 = [mem.split('<@') for mem in member]  # Split into sublists
    refined_list = [[item.replace('>', '') for item in sublist] for sublist in split_1]  # Remove '>'
    flattened_list = [item for sublist in refined_list for item in sublist]  # Flatten the list
    member_ids = [int(item) for item in flattened_list if item.strip()]  # Extract member IDs
    return member_ids

async def setup(bot):
    await bot.add_cog(AutoRoleCog(bot))
