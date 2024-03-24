from __future__ import annotations
from typing import Dict, Optional, List, Any, TYPE_CHECKING

from discord import Embed, ButtonStyle, utils, Interaction
from discord.ui import View, button, Button, Modal
from discord.ext.commands import Context
import discord
import asyncio

if TYPE_CHECKING:
    from discord import Message

class CustomPage(Modal, title='Pick a page'):
    PAGE_NUMBER = None

    num = discord.ui.TextInput(
        label='Enter a page',
        placeholder='Number (eg 5)',
    )

    async def on_submit(self, interaction: Interaction):
        CustomPage.PAGE_NUMBER = self.num.value
        await super().on_submit(interaction)
        await interaction.response.defer()
        self.stop()
        

class Paginator(View):
    
    message: Optional[Message] = None

    def __init__(
        self,
        pages: List[Any],
        *,
        ctx: Optional[Context] = None,
        interaction: Optional[Interaction] = None,
        timeout: Optional[float] = 180.0,
        delete_message_after: bool = False,
        per_page: int = 1,
    ):
        super().__init__(timeout=timeout)
        self.delete_message_after: bool = delete_message_after
        self.current_page: int = -1

        self.ctx: Optional[Context] = ctx
        self.interaction: Optional[Interaction] = interaction
        self.per_page: int = per_page
        self.pages: Any = pages
        total_pages, left_over = divmod(len(self.pages), self.per_page)
        if left_over:
            total_pages += 1

        self.max_pages: int = total_pages

    def stop(self) -> None:
        self.message = None
        self.ctx = None
        self.interaction = None

        super().stop()

    def get_page(self, page_number: int) -> Any:
        if page_number < 0 or page_number >= self.max_pages:
            self.current_page = 0
            return self.pages[self.current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        else:
            base = page_number * self.per_page
            return self.pages[base : base + self.per_page]

    def update_footer(self):
        return f"Page {self.current_page + 1}/{self.max_pages}"

    def format_page(self, page: Any) -> Any:
        page_content = page

        if isinstance(page, Embed):
            embed = page
        elif isinstance(page, list) and all(isinstance(embed, Embed) for embed in page):
            embed = page[0]  # Use the first embed in the list as a base
        elif isinstance(page, dict):
            return page 
        else:
            embed = Embed(description=str(page_content))
        embed.set_footer(text=self.update_footer())

        return embed

    async def get_page_kwargs(self, page: Any) -> Dict[str, Any]:
        formatted_page = await utils.maybe_coroutine(self.format_page, page)

        kwargs = {"content": None, "embeds": [], "view": self}
        if isinstance(formatted_page, str):
            kwargs["content"] = formatted_page
        elif isinstance(formatted_page, Embed):
            kwargs["embeds"] = [formatted_page]
        elif isinstance(formatted_page, list) and all(isinstance(embed, Embed) for embed in formatted_page):
            kwargs["embeds"] = formatted_page
        elif isinstance(formatted_page, dict):
            return formatted_page

        return kwargs

    async def update_page(self, interaction: Interaction) -> None:
        if self.message is None:
            self.message = interaction.message

        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        self.previous_page.disabled = self.current_page <= 0
        self.next_page.disabled = self.current_page >= self.max_pages - 1

        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.edit_message(**kwargs)

    @button(label="Previous Page", style=ButtonStyle.blurple, emoji="◀️")
    async def previous_page(self, interaction: Interaction, button: Button) -> None:
        self.current_page -= 1
        await self.update_page(interaction)

    @button(label="Next Page", style=ButtonStyle.blurple, emoji="▶️")
    async def next_page(self, interaction: Interaction, button: Button) -> None:
        self.current_page += 1
        await self.update_page(interaction)
    
    @button(label='Pick a page', style=ButtonStyle.blurple, emoji='🔍')
    async def pickpage(self, interaction: Interaction, button: Button):
        modal = CustomPage()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if CustomPage.PAGE_NUMBER is not None:
            page = int(CustomPage.PAGE_NUMBER) - 1 
            if 0 <= page < self.max_pages:
                self.current_page = page
                
                if self.current_page > self.max_pages:
                    await interaction.response.send_message('This page does not exist', ephemeral=True)
                else:
                    await self.update_page(interaction)
    
    @button(label="Last Page", style=ButtonStyle.blurple, emoji="⏭")
    async def skip_to_last_page(self, interaction: Interaction, button: Button) -> None:
        self.current_page = self.max_pages - 1
        await self.update_page(interaction)
    
