'''Brawlbot made by Brawlbox for The Brawl Box on discord
If you would like to use this bot, please make sure to credit Brawlbox'''

import discord
# import logging
from discord.ext import commands

f = open("token.txt", "r")
token = f.readline()
f.close()


# logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="helping @Brawlbox", type=discord.ActivityType.playing))

async def process_category(category):
    numempty = 0
    templatename = None
    for c in category.channels:
        if len(c.members) == 0:
            numempty += 1
        if c.name.endswith(" 1"):
            templatename = c.name[:-2]

    if numempty == 0:
        # Create a channel
        already = True
        n = 1
        while already:
            name = templatename + " " + str(n)
            already = False
            for c in category.channels:
                if c.name == name:
                    already = True
            n += 1
        await category.guild.create_voice_channel(name, category = category, user_limit=None)
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
    categorylist = ["GENERAL CHANNELS", "SUPPORTERS CHANNELS", "RACING GAMES", "SHOOTING GAMES", "HORROR GAMES", "FIGHTING GAMES", "SURVIVAL GAMES", "SANDBOX GAMES", "PLATFORMERS", "RHYTHM GAMES", "SPORTS GAMES", "PUZZLE GAMES", "TABLETOP GAMES"]
    if before is not None and before.channel is not None and before.channel.category is not None and before.channel.category.name in categorylist:
        await process_category(before.channel.category)
    if after is not None and after.channel is not None and after.channel.category is not None and after.channel.category.name in categorylist and (before is None or before.channel is None or before.channel.category != after.channel.category):
        await process_category(after.channel.category)

bot.run(token)