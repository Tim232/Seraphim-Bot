#!/usr/bin/env python3.7
from discord.ext import commands
import discord, time, importlib, collections

import common.utils as utils

class NormCMDs(commands.Cog, name="Normal"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pings the bot. Great way of finding out if the bot’s working correctly, but otherwise has no real use."""

        start_time = time.perf_counter()
        ping_discord = round((self.bot.latency * 1000), 2)

        mes = await ctx.send(f"Pong!\n`{ping_discord}` ms from Discord.\nCalculating personal ping...")
        
        end_time = time.perf_counter()
        ping_personal = round(((end_time - start_time) * 1000), 2)
        
        await mes.edit(content=f"Pong!\n`{ping_discord}` ms from Discord.\n`{ping_personal}` ms personally.")
    
    @commands.command()
    async def reverse(self, ctx, *, content):
        """Reverses the content given. Only will ping what you can ping."""

        if len(content) < 1950:
            allowed_mentions = utils.generate_mentions(ctx)
            await ctx.send(f"{ctx.author.mention}: {content[::-1]}", allowed_mentions=allowed_mentions)
        else:
            await ctx.send(f"{ctx.author.mention}, that message is too long!")

    @commands.command()
    async def about(self, ctx):
        """Gives information about the bot."""

        msg_list = collections.deque() # is this pointless? yeah, mostly (there's a slight performance boost), but why not

        msg_list.append("Hi! I'm Seraphim, Sonic49's personal bot!")
        msg_list.append("I was created initially as a starboard bot as other starboard bots had poor uptime, " +
        "but I've since been expanded to other functions, too.")
        msg_list.append("I tend to have features that are either done poorly by other bots, or features of bots " +
        "that tend to be offline/unresponsive for a decent amount of time.")
        msg_list.append("You cannot invite me to your server normally. Usually, Sonic49 invites me to one of his servers on his own, " +
        "but you might be able to convince him, although unlikely, to get me on your server.") 

        about_embed = discord.Embed(
            title = "About", 
            colour = discord.Colour(0x4378fc), 
            description = "\n\n".join(msg_list)
        )
        about_embed.set_author(
            name=f"{self.bot.user.name}", 
            icon_url=f"{str(ctx.guild.me.avatar_url_as(format=None,static_format='jpg', size=128))}"
        )

        source_list = collections.deque()
        source_list.append("My source code is [here!](https://github.com/Sonic4999/Seraphim-Bot)")
        source_list.append("This code might not be the best code out there, but you may have some use for it.")

        about_embed.add_field(
            name = "Source Code",
            value = "\n".join(source_list),
            inline = False
        )

        await ctx.send(embed=about_embed)

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Sorry, you cannot invite me currently. Usually, Sonic49 invites me to one of his servers on his own, " +
        "but you might be able to convince him, although unlikely, to get me on your server.")

    @commands.group(invoke_without_command=True, aliases=["prefix"], ignore_extra=False)
    async def prefixes(self, ctx):
        """A way of getting all of the prefixes for this server. You can also add and remove prefixes via this command."""
        prefixes = [f'"{p}"' for p in self.bot.config[ctx.guild.id]["prefixes"]]
        await ctx.send(f"My prefixes for this server are: `{', '.join(prefixes)}`, but you can also mention me.")

    @prefixes.command(ignore_extra=False)
    @commands.check(utils.proper_permissions)
    async def add(self, ctx, prefix):
        """Addes the prefix to the bot for the server this command is used in, allowing it to be used for commands of the bot.
        If it's more than one word or has a space at the end, surround the prefix with quotes so it doesn't get lost."""

        if len(self.bot.config[ctx.guild.id]["prefixes"]) >= 10:
            raise utils.CustomCheckFailure("You have too many prefixes! You can only have up to 10 prefixes.")

        if not prefix in self.bot.config[ctx.guild.id]["prefixes"]:
            self.bot.config[ctx.guild.id]["prefixes"].append(prefix)
            await ctx.send(f"Added `{prefix}`!")
        else:
            raise commands.BadArgument("The server already has this prefix!")

    @prefixes.command(ignore_extra=False, aliases=["delete"])
    @commands.check(utils.proper_permissions)
    async def remove(self, ctx, prefix):
        """Deletes a prefix from the bot from the server this command is used in. The prefix must have existed in the first place.
        If it's more than one word or has a space at the end, surround the prefix with quotes so it doesn't get lost."""

        try:
            self.bot.config[ctx.guild.id]["prefixes"].remove(prefix)
            await ctx.send(f"Removed `{prefix}`!")
        except ValueError:
            raise commands.BadArgument("The server doesn't have that prefix, so I can't delete it!")

def setup(bot):
    importlib.reload(utils)
    bot.add_cog(NormCMDs(bot))