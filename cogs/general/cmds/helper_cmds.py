from discord.ext import commands
import discord, importlib, typing

import common.utils as utils
import common.image_utils as image_utils

class HelperCMDs(commands.Cog, name = "Helper"):
    """A series of commands made for tasks that are usually difficult to do, especially on mobile."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(utils.proper_permissions)
    async def add_emoji(self, ctx, emoji_name, url: typing.Optional[image_utils.URLToImage]):
        """Adds the image or URL given as an emoji to this server.
        It must be an image of type GIF, JPG, or PNG. It must also be under 256 KB.
        The name must be at least 2 characters.
        Useful if you're on iOS and transparency gets the best of you or if you want to add an emoji from a URL."""

        if len(emoji_name) < 2:
            await ctx.send("Emoji name must at least 2 characters!")
            return

        if url == None:
            if ctx.message.attachments:
                image_endings = ("jpg", "jpeg", "png", "gif")
                image_extensions = tuple(image_endings) # no idea why I have to do this

                if ctx.message.attachments[0].proxy_url.endswith(image_extensions):
                    url = ctx.message.attachments[0].proxy_url
                else:
                    raise commands.BadArgument("Attachment provided is not a valid image.")
            else:
                raise commands.BadArgument("No URL or image given!")

        assert url != None

        emoji_count = len(ctx.guild.emojis)
        if emoji_count >= ctx.guild.emoji_limit:
            await ctx.send("This guild has no more emoji slots!")
            return

        emoji_data = await image_utils.get_file_bytes(url, 262143) # 256 KB - 1
        if emoji_data == None:
            await ctx.send("This emoji is over 256 KB! Please try compressing the image and try again.")
            return

        try:
            emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=emoji_data, reason=f"Created by {str(ctx.author)}")
        except discord.HTTPException as e:
            await ctx.send(
                    "".join(("I was unable to add this emoji! This might ",
                "due to me not having the permissions or the name being improper in some way.\n",
                f"Error: {e}"))
            )
            return

        await ctx.send(f"Added {str(emoji)}!")

def setup(bot):
    importlib.reload(utils)
    importlib.reload(image_utils)
    
    bot.add_cog(HelperCMDs(bot))