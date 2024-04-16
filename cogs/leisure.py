from discord.ext import commands
from discord import app_commands, Interaction, File
from discord.errors import NotFound, HTTPException

from gtts import gTTS
import os

import httpx
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from io import BytesIO


FONT_BIG = ImageFont.truetype('OpenSans-CondensedSemiBoldItalic.ttf', 72)
TEXT_COLOR = 'white'


def make_quote_image(text, author_img):
    # Load the original image
    org_img = Image.open(BytesIO(author_img))

    # Increase the opacity of the image
    enhancer = ImageEnhance.Brightness(org_img)
    opacity_factor = 0.5  # Adjust this value as needed
    org_img = enhancer.enhance(opacity_factor)
    
    # Calculate the size of the text
    text_width, text_height = ImageDraw.Draw(org_img).textsize(text, font=FONT_BIG)
    
    # Calculate the new size of the image while maintaining aspect ratio
    aspect_ratio = org_img.width / org_img.height
    if text_width > org_img.width or text_height > org_img.height:
        if text_width / text_height > aspect_ratio:
            new_width = text_width
            new_height = int(text_width / aspect_ratio)
        else:
            new_height = text_height
            new_width = int(text_height * aspect_ratio)
    else:
        new_width, new_height = org_img.width, org_img.height
    
    # Resize the image
    resized_img = org_img.resize((new_width, new_height), Image.ANTIALIAS)
    
    # Create a new draw object
    draw = ImageDraw.Draw(resized_img)
    
   # Calculate the starting point for the text
    start_x = resized_img.width / 2 - text_width / 2
    start_y = resized_img.height / 2
    
    # Draw the text
    draw.text((start_x, start_y), text, fill=TEXT_COLOR, font=FONT_BIG)
    
    # Save the image to a BytesIO object
    image_bytes = BytesIO()
    resized_img.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return image_bytes


class LeisureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def sound_to_text(self, input):
        tts = gTTS(text=input, lang='en')
        filename = 'voice.mp3'
        tts.save(filename)
        return filename

    @app_commands.command(name='tts', description='Turn text into voice')
    async def tts(self, interaction: Interaction, text: str, dm: bool = False):
        await interaction.response.defer(ephemeral=True)
        file = self.sound_to_text(text)
        if dm:
            channel = await interaction.user.create_dm()
            await channel.send("Here's your file:", file=File(file))
            os.remove(file)
            await interaction.followup.send("Sent!", ephemeral=True)
        else:
            await interaction.followup.send("Here's your file:", file=File(file))
            os.remove(file)

    @app_commands.command(name='generate-quote', description='Quote someone')
    async def gen_quote(self, interaction: Interaction, message_id: str):
        await interaction.response.defer(ephemeral=True)
        msg = None
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
        except NotFound:
            await interaction.followup.send('Could not find message, ensure the command is run in the same channel as the message was sent in.', ephemeral=True)
        except HTTPException:
            await interaction.followup.send('Invalid ID, please make sure you have the correct message ID.', ephemeral=True)

        if msg is not None:
            text = msg.content
            author = msg.author.name
            author_avatar = msg.author.avatar.url
            await interaction.followup.send('Processing...', ephemeral=True)
            
            avatar_response = httpx.get(author_avatar)
            if avatar_response.status_code == 200:
                img = make_quote_image(text=text, author_img=avatar_response.content)
                await interaction.followup.send(file=File(img, f'{author}.png'), ephemeral=False)
            else:
                await interaction.followup.send('Failed to fetch user avatar.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(LeisureCog(bot))
