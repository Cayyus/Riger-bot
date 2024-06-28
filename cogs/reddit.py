from discord import app_commands, Interaction, Embed, ButtonStyle, File
from discord.ui import View, Button, button
from discord.ext import commands

import os
import asyncpraw
import asyncio
import random

from asyncprawcore.exceptions import NotFound

from dotenv import load_dotenv
from datetime import datetime


load_dotenv('tokens.env')

subreddits = ['pics', 'MadeMeSmile','funny','food','memes','interestingasfuck','Unexpected','Satisfyingasfuck'
              'science', 'worldnews', 'news', 'gaming', 'dataisbeautiful', 'mapporn', 'foodporn', 'enviroment',
              'Futurology', 'nextfuckinglevel', 'wholesomememes', 'YouShouldKnow']
time_filters = ['hour', 'month', 'day', 'week']
functions = ['new', 'hot', 'rising', 'random_rising', 'random', 'controversial']


class ButtonMenu(View):
    def __init__(self, sub):
        super().__init__()
        self.sub = sub

    @button(label=f'Get another submission from this subreddit', style=ButtonStyle.grey, emoji="🔄")
    async def repeat_another(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        embed = Embed()

        async with asyncpraw.Reddit(
                client_id=os.environ.get('REDDIT_CLIENT_ID'),
                client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
                user_agent=os.environ.get("REDDIT_USER_AGENT")
        ) as reddit:

            subreddit = await reddit.subreddit(self.sub, fetch=True)

            async for submission in subreddit.rising(limit=25):
                submissions = []
                submissions.append(submission)
            
            submission = random.choice(submissions)

            embed.title = submission.title
            embed.url = f"https://www.reddit.com/r/{self.sub}/comments/{submission.id}"
            embed.timestamp = datetime.fromtimestamp(submission.created_utc)

            if submission.over_18:
                embed.description = "⚠️ **WARNING! THIS POST MAY CONTAIN NSFW CONTENT, PLEASE PROCEED AT YOUR OWN DISCRETION!** ⚠️"
                embed.set_image(url=None)

            if "https://v.redd.it" in submission.url:
                embed.set_image(url=None)
            
            if "https://i.redd.it/" not in submission.url:
                embed.set_image(url=None)
        
            if submission.author is not None and submission.author.name is not None:
                embed.set_author(name=f'by u/{submission.author.name} in r/{self.sub}', url=f"https://www.reddit.com/r/{self.sub}", icon_url="https://www.iconpacks.net/icons/2/free-reddit-logo-icon-2436-thumb.png")
            else:
                embed.set_author(name=f"r/{self.sub}", url=f"https://www.reddit.com/r/{self.sub}", icon_url="https://www.iconpacks.net/icons/2/free-reddit-logo-icon-2436-thumb.png")

            embed.set_image(url=submission.url)
            
        
        await interaction.followup.send(embed=embed)

        sent_response = await interaction.original_response()
        await sent_response.add_reaction("👍")
        await sent_response.add_reaction("👎")


class RedditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = 'random_reddit', description='Gives a random post from a random choice of subreddits')
    async def random_reddit(self, interaction: Interaction):
        await interaction.response.defer()
        embed = Embed()

        def parse_embed(subr, submission):
            embed.title = submission.title
            embed.url = f"https://www.reddit.com/r/{subr}/comments/{submission.id}"
            embed.timestamp = datetime.fromtimestamp(submission.created_utc)
            embed.set_footer(text=f"Score: {submission.score} Comments: {submission.num_comments}")
            embed.set_image(url=submission.url)
            
            if submission.over_18:
                embed.description = "⚠️ **WARNING! THIS POST MAY CONTAIN NSFW CONTENT, PLEASE PROCEED AT YOUR OWN DISCRETION!** ⚠️"
                embed.set_image(url=None)
            
            if "https://v.redd.it/" in submission.url:
                vid = submission.url
                embed.set_image(url=None)
            
            if "https://i.redd.it/" not in submission.url:
                embed.set_image(url=None)
        
            if submission.author is not None and submission.author.name is not None:
                embed.set_author(name=f'by u/{submission.author.name} in r/{subr}', url=f"https://www.reddit.com/r/{subr}", icon_url="https://www.iconpacks.net/icons/2/free-reddit-logo-icon-2436-thumb.png")
            else:
                embed.set_author(name=f"r/{subr}", url=f"https://www.reddit.com/r/{subr}", icon_url="https://www.iconpacks.net/icons/2/free-reddit-logo-icon-2436-thumb.png")
            
            
        subr = random.choice(subreddits)
        function = random.choice(functions)
        async with asyncpraw.Reddit(
                client_id=os.environ.get('REDDIT_CLIENT_ID'),
                client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
                user_agent=os.environ.get("REDDIT_USER_AGENT")
        ) as reddit:
                
                subreddit = await reddit.subreddit(subr, fetch=True)
                submissions = []
                
                try:
                    if function == 'controversial':
                        async for submission in subreddit.controversial(time_filter=random.choice(time_filters), limit=25):
                            submissions.append(submission)
                        
                        submission = random.choice(submissions)
                        parse_embed(subr, submission)

                    elif function == 'new':
                        async for submission in subreddit.new(limit=25):
                            submissions.append(submission)
                        
                        submission = random.choice(submissions)
                        parse_embed(subr, submission)
                    
                    elif function == 'rising':
                        async for submission in subreddit.rising(limit=25):
                            submissions.append(submission)
                        
                        submission = random.choice(submissions)
                        parse_embed(subr, submission)
                    
                    elif function == 'random_rising':
                        async for submission in subreddit.controversial(limit=25):
                            submissions.append(submission)
                        
                        submission = random.choice(submissions)
                        parse_embed(subr, submission)

                    elif function == 'random':
                        async for submission in subreddit.controversial(limit=25):
                            if submission is None:
                                async for submission in subreddit.hot(limit=25):
                                    submissions.append(submission)
                                submission = random.choice(submissions)
                                parse_embed(subr, submission)
                            else:
                                parse_embed(subr, submission)
                    
                    elif function == 'hot':
                        async for submission in subreddit.controversial(limit=25):
                            submissions.append(submission) 
                        submission = random.choice(submissions)
                        parse_embed(subr, submission)

                except Exception as e:
                    print(e)
                    await interaction.followup.send("Error in command 'reddit'")
        
        view = ButtonMenu(subr)
        await interaction.followup.send(embed=embed, view=view)

        sent_response = await interaction.original_response()
        await sent_response.add_reaction("👍")
        await sent_response.add_reaction("👎")
        

async def setup(bot):
    await bot.add_cog(RedditCog(bot))

