from discord.ext import commands
from discord import app_commands, Interaction, Member, Permissions

from datetime import timedelta

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = 'purge', description='Purge a specific number of messages in a channel')
    async def purge(self, interaction: Interaction, amount: int):
        try:
            await interaction.response.defer()
            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.manage_messages:
                    await interaction.followup.send('You do not have permission to purge messages.')
                    return
                else:
                    await interaction.channel.purge(limit=amount, before=interaction.created_at) 
                    await interaction.followup.send(f"{amount} messages deleted.")
                    
        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send(f'Cannot purge messages, please check whether bot has `manage_messages` permission.')
    
    @app_commands.command(name='kick', description='Kicks a member')
    async def kick(self, interaction: Interaction, target: Member):
        try:
            await interaction.response.defer()
            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.kick_members:
                    await interaction.followup.send('You do not have permission to kick members.')
                    return
                else:
                    if target.name == interaction.user.name:
                        await interaction.followup.send("Woah, you can't kick yourself")
                        return
                    await target.kick()
                    await interaction.followup.send(f"{target.mention} has been kicked from this server.")
        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send(f'Cannot kick, either the bot does not have the necessary permission or the user ranks higher than the bot.')
            else:
                await interaction.followup.send('An error occured, try again.')
                print(e)
    
    @app_commands.command(name='ban', description='Ban someone from the server')
    async def ban(self, interaction: Interaction, target: Member, reason: str):
        try:
            await interaction.response.defer()
            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.ban_members:
                    await interaction.followup.send('You do not have permission to ban members.')
                else:
                    if target.bot:
                        await target.ban(reason=reason)
                        await interaction.followup.send(f'{target.mention} has been banned from this server.')
                    else:
                        if target.name == interaction.user.name:
                            await interaction.followup.send("Woah, you can't ban yourself")
                            return
                        await target.ban(reason=reason)
                        await interaction.followup.send(f'{target.mention} has been banned from this server.')
                        await target.send(f'You have been banned from {interaction.guild.name} by {interaction.user.name} for {reason}.')
        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send(f'Cannot ban, either the bot does not have the necessary permission or the user ranks higher than the bot.')
            else:
                await interaction.followup.send('An error occured, try again.')
                print(e)
    
    @app_commands.command(name="unban", description="Unbans a member")
    async def unban(self, interaction: Interaction, id: str):
        try:
            await interaction.response.defer()
            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.ban_members:
                    await interaction.followup.send('You do not have permission to unban members.')
                else:
                    member = await self.bot.fetch_user(id)
                    await interaction.guild.unban(member)
                    await interaction.followup.send(f"{member} has been unbanned from this server.")
        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send("Cannot unban, please check whether the bot has `ban_members` permission.")
            else:
                await interaction.followup.send('An error occured, try again.')
                print(e)
    
    @app_commands.command(name = 'timeout', description='Mute a member')
    async def timeout(self, interaction: Interaction, target: Member, duration_in_hours: int, reason:str=None):
        try:
            await interaction.response.defer()
            created = interaction.created_at
            duration = timedelta(hours=duration_in_hours)
            timeout_time = created + duration

            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.moderate_members:
                    await interaction.followup.send('You cannot timeout members.')
                else:
                    if target.is_timed_out():
                        await interaction.followup.send(f'{target.name} is already timed out.')
                        return 
                    else:
                        if target.name == interaction.user.name:
                            await interaction.followup.send("Woah, you can't timeout yourself.")
                            return
                        await target.timeout(timeout_time, reason=reason if reason is True else None)
                        await interaction.followup.send(f'{target.mention} is timed out.')
        
        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send('Cannot mute member, either the bot does not have the necessary permission or the user ranks higher than the bot.')
            else:
                await interaction.followup.send('An error occured, try again.')
                print(e)

    @app_commands.command(name='remove_timeout', description='Remove a timeout from a member')
    async def remove_timeout(self, interaction: Interaction, target: Member):
        try:
            await interaction.response.defer()
            perms = interaction.user._permissions
            perms = [perms]
            for perm in perms:
                permissions = Permissions(perm)
                if not permissions.moderate_members:
                    await interaction.followup.send('You cannot remove timeout from members.')
                else:
                    if not target.is_timed_out():
                        await interaction.followup.send(f'{target.name} is not timed out.')
                        return          
                    else:
                        await target.timeout(None)
                        await interaction.followup.send(f'{target.mention} is no longer timed out.')

        except Exception as e:
            if '50013' in str(e):
                await interaction.followup.send('Cannot remove timeout, either the bot does not have the necessary permission or the user ranks higher than the bot.')
            else:
                await interaction.followup.send('An error occured, try again.')
                print(e)
            
async def setup(bot):
    await bot.add_cog(AutoModCog(bot))
