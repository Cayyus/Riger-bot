import discord
import os
from discord.ext import commands
from credentials import TOKEN
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)

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
    await bot.start(TOKEN)

asyncio.run(main())
