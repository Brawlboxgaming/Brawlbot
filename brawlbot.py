'''Brawlbot made by Brawlbox
If you would like to use this code, please make sure to credit Brawlbox'''

import discord
from discord.ext import commands

f = open("token.txt", "r")
token = f.readline()
f.close()

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="helping 🥊Brawlbox🥊", type=discord.ActivityType.playing))

async def process_category(category):
    n = 1
    numempty = 0
    templatename = None
    for c in category.channels:
        if isinstance(c, discord.VoiceChannel):
            if len(c.members) == 0:
                numempty += 1
            endchars = (c.name[c.name.index(str(n)):])[1:]
            templatename = c.name[:-(len(endchars)+1)]
            n += 1

    if numempty == 0:
        # Create a channel
        already = True
        while already:
            name = templatename + str(n) + endchars
            for c in category.channels:
                if isinstance(c, discord.VoiceChannel):
                    user_limit = c.user_limit
                    break
            already = False
            for c in category.channels:
                if c.name == name:
                    already = True
            n += 1
        await category.guild.create_voice_channel(name, category = category, user_limit=user_limit)
    elif numempty > 1:
        # Delete empty channels apart from first
        first = True
        for c in category.channels:
            if not isinstance(c, discord.VoiceChannel) or len(c.members) > 0:
                continue
            if first:
                first = False
                continue
            await c.delete()

@bot.event
async def on_voice_state_update(member, before, after):
    f = open("categories.txt")
    categorylist = f.readlines()
    for i in range(len(categorylist)):
        if "\n" in categorylist[i]:
            categorylist[i] = str(categorylist[i][:-1])
    f.close()
    if before is not None and before.channel is not None and before.channel.category is not None and before.channel.category.name in categorylist:
        await process_category(before.channel.category)
    if after is not None and after.channel is not None and after.channel.category is not None and after.channel.category.name in categorylist and (before is None or before.channel is None or before.channel.category != after.channel.category):
        await process_category(after.channel.category)

bot.run(token)