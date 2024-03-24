from discord.ext import commands
from discord import app_commands, Embed, Interaction, Member
from utils.formatters import timestamp_formatting, badge_name_id, status_emotes

class ServerProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='user', description='Profile of a user')
    async def user(self, interaction: Interaction, user: Member):
        badges = []
        userbadges = []

        user_id = user.id
        username = user.name
        display_name = user.global_name
        user_avatar = user.avatar
        joined_discord = user.created_at
        joined_server = user.joined_at
        userflags = user.public_flags.all()
        user_roles = user.roles
        roles = [role.id for role in user_roles]
        guild = interaction.guild
        member_obj = guild.get_member(user_id)
        status = member_obj.status

        status_name = str(status)
        if status_name in status_emotes:
            status_id = status_emotes[status_name]
            user_status = f"<:{status_name}:{status_id}>"
        
        for flag in userflags:
            badge = flag.name
            badges.append(badge)

        for badge in badges:
            if badge in badge_name_id:
                badge_name = badge
                badge_id = badge_name_id[badge]
                badge_string = f'<:{badge_name}:{badge_id}>'
                userbadges.append(badge_string)

        fmt_roles = [f'<@&{role}>' for role in roles[1:]] #formatted with correct discord code

        #checks
        if fmt_roles is not None:
            usr_roles = ' '.join(fmt_roles)
        else:
            usr_roles = None        
        
        if userbadges is not None:
            usr_badges = ''.join(userbadges)
        else:
            usr_badges = None
        

        fmt_discord_t = timestamp_formatting(joined_discord)
        fmt_server_t = timestamp_formatting(joined_server)

        embed_list = [
            ('Username', username),
            ('Display Name', display_name),
            ('Badges', usr_badges),
            ('Created Account', f"{fmt_discord_t}"),
            ('Joined This Server', f"{fmt_server_t}")
        ]

        embed = Embed(title=f"{user_status} {username.capitalize()}")

        for field in embed_list:
            embed.add_field(name=field[0], value=field[1], inline=True)
        
        embed.add_field(name='Roles', value=usr_roles)

        embed.set_thumbnail(url=user_avatar)
        embed.set_footer(text=f'User ID: {user_id}')

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name = 'server', description='Profile of this server')
    async def server(self, interaction: Interaction):
        statuses = []

        guild = interaction.guild
        guild_id = guild.id
        guild_name = guild.name
        server_owner = guild.owner.name
        total_members = guild.member_count
        status_count = guild.members
        emotes = len(guild.emojis)
        
        guild_avatar = guild.icon
        guild_created = guild.created_at
        guild_created_t = timestamp_formatting(guild_created)

        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        
        bot_count = len([i for i in guild.members if i.bot])

        for member in status_count:
            status = member.status.name
            statuses.append(status)
        
        online = statuses.count('online')
        offline = statuses.count('offline')
        dnd = statuses.count('dnd')
        idle = statuses.count('idle')

        members_lst = f"`{total_members}` Members\n`{bot_count}` Bots"
        statuses_lst = f"`{online}` Online\n`{idle}` Idle\n`{dnd}` DnD\n`{offline}` Offline"
        channels_lst = f"`{text_channels}` Text\n`{voice_channels}` Voice"
    
        embeds = [
            ('Owner', f"`{server_owner}`"),
            ('Members', members_lst),
            ('Member Statuses', statuses_lst),
            ('Emojis', f"`{emotes}`"),
            ('Channels', channels_lst),
            ('Created On', guild_created_t),
        ]

        embed = Embed(title=f"Overview of {guild_name}")
        for field in embeds:
            embed.add_field(name = field[0], value= field[1], inline=True)
        
        embed.set_thumbnail(url=guild_avatar)
        embed.set_footer(text=guild_id)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerProfile(bot))
