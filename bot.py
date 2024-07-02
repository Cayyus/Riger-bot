import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)

load_dotenv('tokens.env')

@bot.command(name="sync")
async def sync(ctx):
    synced = await bot.tree.sync()
    logging.info(f"Synced {len(synced)} command(s).")

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load()
    await bot.start(os.environ.get('TOKEN'))

asyncio.run(main())

