"""
Credit of this section goes to
https://github.com/SamSanai/VoiceMaster-Discord-Bot
"""
import asyncio
from logging import getLogger
import sqlite3
import discord
from discord.ext import commands
from discord.ext.commands import Context

logger = getLogger(f"main.{__name__}")


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice = c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown = c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        """
                        May have to enable after load testing
                        Dont know how well this code works under a large set of users
                        """
                        # await member.send("Creating channels too quickly you've been put on a 15 second cooldown!")
                        # await asyncio.sleep(15)
                    c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting = c.fetchone()
                    c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting = c.fetchone()
                    if setting is None:
                        name = f"{member.name}'s channel"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name, category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True, read_messages=True)
                    await channel2.edit(name=name, user_limit=limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id, channelID))
                    conn.commit()

                    def check(a, b, c):
                        return len(channel2.members) == 0

                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except: # noqa
                # TODO Add exception handler here
                # IDK why OP has a bare except here but i dont like it
                pass
        conn.commit()
        conn.close()

    @commands.group()
    async def voice(self, context: Context):
        pass

    @voice.command()
    @commands.has_permissions(manage_messages=True)
    async def setup(self, context: Context):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        guildID = context.guild.id
        id = context.author.id
        if context.author.id == context.guild.owner.id or context.author.id == 151028268856770560:
            def check(m):
                return m.author.id == context.author.id

            await context.channel.send("**You have 60 seconds to answer each question!**")
            await context.channel.send(
                "**Enter the name of the category you wish to create the channels in:(e.g Voice Channels)**")
            try:
                category = await self.bot.wait_for('message', check=check, timeout=60.0)
                logger.debug(f"User({context.author}) has chosen to put their channel in {category}")
            except asyncio.TimeoutError:
                logger.debug(f"User({context.author}) took to long to respond")
                await context.channel.send('Took too long to answer!')
            else:
                new_cat = await context.guild.create_category_channel(category.content)
                await context.channel.send('**Enter the name of the voice channel: (e.g Join To Create)**')
                try:
                    channel = await self.bot.wait_for('message', check=check, timeout=60.0)
                    logger.debug(f"User({context.author}) has chosen to create the channel {channel}")
                except asyncio.TimeoutError:
                    logger.debug(f"User({context.author}) took to long to respond")
                    await context.channel.send('Took too long to answer!')
                else:
                    try:
                        channel = await context.guild.create_voice_channel(channel.content, category=new_cat)
                        c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
                        voice = c.fetchone()
                        if voice is None:
                            c.execute("INSERT INTO guild VALUES (?, ?, ?, ?)", (guildID, id, channel.id, new_cat.id))
                        else:
                            c.execute(
                                "UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",
                                (guildID, id, channel.id, new_cat.id, guildID))
                        await context.channel.send("**You are all setup and ready to go!**")
                        logger.debug(f"User {context.author} has successfully created the voice channel {channel}")
                    except: # noqa
                        logger.debug(f"User {context.author} did not enter names properly")
                        await context.channel.send("You didn't enter the names properly.\nUse `.voice setup` again!")
        else:
            await context.channel.send(f"{context.author.mention} only the owner of the server can setup the bot!")
            logger.debug(f"{context.author} attempted to but is unauthorized to create channels")
        conn.commit()
        conn.close()

    @commands.command()
    async def setlimit(self, context: Context, num: int):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        if context.author.id == context.guild.owner.id or context.author.id == 151028268856770560:
            c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (context.guild.id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)",
                          (context.guild.id, f"{context.author.name}'s channel", num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, context.guild.id))
            await context.send("You have changed the default channel limit for your server!")
            logger.debug(f"User {context.author} has changed the default channel limit of the server to {num}")
        else:
            logger.debug(f"{context.author} attempted to but is unauthorized to alter the channel limit of the server")
            await context.channel.send(f"{context.author.mention} only the owner of the server can setup the bot!")
        conn.commit()
        conn.close()

    @setup.error
    async def info_error(self, ctx: Context, error: Exception):
        print(error)

    @voice.command()
    async def lock(self, context: Context):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to lock a channel but they don't own one")
        else:
            channelID = voice[0]
            role = discord.utils.get(context.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False, read_messages=True)
            await context.channel.send(f'{context.author.mention} Voice chat locked! 🔒')
            logger.debug(f"{context.author} locked the channel {channel}")
        conn.commit()
        conn.close()

    @voice.command()
    async def unlock(self, context: Context):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to unlock a channel but they don't own one")
        else:
            channelID = voice[0]
            role = discord.utils.get(context.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True, read_messages=True)
            await context.channel.send(f'{context.author.mention} Voice chat unlocked! 🔓')
            logger.debug(f"{context.author} unlocked the channel {channel}")
        conn.commit()
        conn.close()

    @voice.command(aliases=["allow"])
    async def permit(self, context: Context, member: discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to give permission to a channel but they don't own one")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await context.channel.send(
                f'{context.author.mention} You have permited {member.name} to have access to the channel. ✅')
            logger.debug(f"{context.author} permitted {member.name} into the channel {channel}")
        conn.commit()
        conn.close()

    @voice.command(aliases=["deny"])
    async def reject(self, context: Context, member: discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        guildID = context.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to reject someone from a channel but they don't own one")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False, read_messages=True)
            await context.channel.send(
                f'{context.author.mention} You have rejected {member.name} from accessing the channel. ❌')
            logger.debug(f"{context.author} kicked/rejected {member.name} from the channel {channel}")
        conn.commit()
        conn.close()

    @voice.command()
    async def limit(self, context: Context, limit: int):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to limit a channel but they don't own one")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)
            await context.channel.send(f'{context.author.mention} You have set the channel limit to be ' + '{}!'.format(limit))
            logger.debug(f"{context.author} has the limit of channel {channel} to {limit}")
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id, f'{context.author.name}', limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))
        conn.commit()
        conn.close()

    @voice.command()
    async def name(self, context: Context, *, name):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await context.channel.send(f"{context.author.mention} You don't own a channel.")
            logger.debug(f"{context.author} attempted to name a channel but they don't own one")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name=name)
            await context.channel.send(f'{context.author.mention} You have changed the channel name to ' + '{}!'.format(name))
            logger.debug(f"{context.author} has changed the channel name {name}")
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id, name, 0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))
        conn.commit()
        conn.close()

    @voice.command()
    async def claim(self, context: Context):
        x = False
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        logger.debug("Established connection with voice database")
        channel = context.author.voice.channel
        if channel is None:
            await context.channel.send(f"{context.author.mention} you're not in a voice channel.")
            logger.debug(f"{context.author} attempted to claim a channel but they're not in one")
        else:
            id = context.author.id
            c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
            voice = c.fetchone()
            if voice is None:
                await context.channel.send(f"{context.author.mention} You can't own that channel!")
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = context.guild.get_member(voice[0])
                        await context.channel.send(
                            f"{context.author.mention} This channel is already owned by {owner.mention}!")
                        logger.debug(f"{context.author} attempted to claim the channel {channel}, which was already"
                                     f"owned by {owner}")
                        x = True
                if x is False:
                    await context.channel.send(f"{context.author.mention} You are now the owner of the channel!")
                    logger.debug(f"{context.author} claimed the channel {channel}")
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
            conn.commit()
            conn.close()


def setup(bot):
    bot.add_cog(voice(bot))
