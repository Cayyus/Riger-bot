from discord.ext import commands
from discord import app_commands, Interaction, Member
from discord.utils import get


class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = 'purge', description='Purge a specific number of messages in a channel')
    async def purge(self, interaction: Interaction, amount: int):
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount, before=interaction.created_at) 
        await interaction.followup.send(f"{amount} messages deleted.")
    
    @app_commands.command(name='kick', description='Kicks a member')
    async def kick(self, interaction: Interaction, target: Member):
        await target.kick()
        await interaction.response.send_message(f"{target.mention} has been kicked from this server.")
    
    @app_commands.command(name='ban', description='Ban someone from the server')
    async def ban(self, interaction: Interaction, target: Member, reason: str):
        await target.send(f'You have been banned from {interaction.guild.name} by {interaction.user.name} for {reason}.')
        await target.ban(reason=reason)
        await interaction.response.send_message(f'{target.mention} has been banned from this server.')
    
    @app_commands.command(name="unban", description="Unbans a member")
    async def unban(self, interaction: Interaction, id: str):
        member = await self.bot.fetch_user(id)
        await interaction.guild.unban(member)
        await interaction.response.send_message(f"{member} has been unbanned from this server.")
    
    @app_commands.command(name = 'timeout', description='Mute a member')
    async def timeout(self, interaction: Interaction, target: Member):
        guild = interaction.guild
        mute_role = get(guild.roles, name='Muted')
        await target.add_roles(mute_role)
        await interaction.response.send_message(f"Muted {target.mention}.")
        
async def setup(bot):
    await bot.add_cog(AutoModCog(bot))
