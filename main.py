#!/usr/bin/env python3.7
import discord, os, asyncio
import websockets, logging
from discord.ext import commands
from discord.ext.commands.view import StringView
from discord.ext.commands.bot import _default as bot_default
from datetime import datetime

import common.utils as utils

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename=os.environ.get("LOG_FILE_PATH"), level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s")

def seraphim_prefixes(bot: commands.Bot, msg: discord.Message):
    mention_prefixes = [f"{bot.user.mention} ", f"<@!{bot.user.id}> "]

    try:
        custom_prefixes = bot.config[msg.guild.id]["prefixes"]
    except AttributeError:
        # prefix handling runs before command checks, so there's a chance there's no guild
        custom_prefixes = ["s!"]

    return mention_prefixes + custom_prefixes

def block_dms(ctx):
    return ctx.guild is not None

class SeraphimBot(commands.Bot):
    def __init__(self, command_prefix, help_command=bot_default, description=None, **options):
        super().__init__(command_prefix, help_command=help_command, description=description, **options)
        self._checks.append(block_dms)

    async def on_ready(self):
        if self.init_load == True:
            self.starboard = {}
            self.config = {}

            self.snipes = {
                "deletes": {},
                "edits": {}
            }

            self.star_queue = {}
            self.star_lock = False

            image_endings = ("jpg", "jpeg", "png", "gif", "webp")
            self.image_extensions = tuple(image_endings) # no idea why I have to do this

            application = await self.application_info()
            self.owner = application.owner

            self.load_extension("cogs.db_handler")
            while self.config == {}:
                await asyncio.sleep(0.1)

            cogs_list = utils.get_all_extensions(os.environ.get("DIRECTORY_OF_FILE"))

            for cog in cogs_list:
                if cog != "cogs.db_handler":
                    try:
                        self.load_extension(cog)
                    except commands.NoEntryPointError:
                        pass

        utcnow = datetime.utcnow()
        time_format = utcnow.strftime("%x %X UTC")

        connect_msg = f"Logged in at `{time_format}`!" if self.init_load == True else f"Reconnected at `{time_format}`!"
        await self.owner.send(connect_msg)

        self.init_load = False

        activity = discord.Activity(name = 'over a couple of servers', type = discord.ActivityType.watching)

        try:
            await self.change_presence(activity = activity)
        except websockets.ConnectionClosedOK:
            await utils.msg_to_owner(self, "Reconnecting...")

    async def on_resumed(self):
        activity = discord.Activity(name = 'over a couple of servers', type = discord.ActivityType.watching)
        await self.change_presence(activity = activity)

    async def on_error(self, event, *args, **kwargs):
        try:
            raise
        except BaseException as e:
            await utils.error_handle(bot, e)

    async def get_context(self, message, *, cls=commands.Context):
        """A simple extension of get_content. If it doesn't manage to get a command, it changes the string used
        to get the command from - to _ and retries. Convenient for the end user."""

        ctx = await super().get_context(message, cls=cls)
        if ctx.command == None and ctx.invoked_with != None:
            ctx.command = self.all_commands.get(ctx.invoked_with.replace("-", "_"))

        return ctx


bot = SeraphimBot(command_prefix=seraphim_prefixes, fetch_offline_members=True)

bot.init_load = True
bot.run(os.environ.get("MAIN_TOKEN"))