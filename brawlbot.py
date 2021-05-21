'''Brawlbot made by Brawlbox
If you would like to use this code, please make sure to credit Brawlbox'''

import discord
from discord.ext import commands
from discord.utils import get

import re

f = open("token.txt", "r")
token = f.readline()
f.close()

bot = commands.Bot(command_prefix='box>')

@bot.command(name='eventstart')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def event_start(ctx, EventName, MembersCanType, MuteMembers, Capacity, VCCount):
    guild = ctx.message.guild

    cancel = False

    if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381:
        cancel = True
    if MuteMembers == "True" or MuteMembers == "true":
        Speak = False
    elif MuteMembers == "False" or MuteMembers == "false":
        Speak = True
    else:
        cancel = True
        await ctx.send("Command could not be processed: Invalid 'MuteMembers' argument")

    if MembersCanType == "True" or MembersCanType == "true":
        Type = True
    elif MembersCanType == "False" or MembersCanType == "false":
        Type = False
    else:
        cancel = True
        await ctx.send("Command could not be processed: Invalid 'MembersCanType' argument")
    
    try:
        user_limit = int(Capacity)
    except:
        await ctx.send("Command could not be processed: Invalid 'Capacity' argument")
        cancel = True

    try:
        VCCount = int(VCCount)
    except:
        await ctx.send("Command could not be processed: Invalid 'VCCount' argument")
        cancel = True

    if VCCount == 0:
        await ctx.send("Command could not be processed: 'VCCount' cannot be 0")
        cancel = True

    if get(ctx.guild.categories, name="EVENTS") != None:
        await ctx.send("Command could not be processed: There is already an event currently being held")
        cancel = True

    if not cancel:
        position = 1
        await ctx.guild.create_category("EVENTS", position = position-1)
        staffperms = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        get(ctx.guild.roles, name="📦ModBox📦"): discord.PermissionOverwrite(view_channel=True),
        get(ctx.guild.roles, name="📦TrialBox📦"): discord.PermissionOverwrite(view_channel=True)
        }
        textperms = {
        'send_messages': Type}
        voiceperms = {
        'speak': Speak}
        if VCCount == 1:
            await ctx.guild.create_text_channel(EventName, category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**textperms)})
            await ctx.guild.create_voice_channel(EventName.replace("-", " "), category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**voiceperms)}, user_limit = user_limit)
        else:
            for i in range(VCCount):
                await ctx.guild.create_text_channel(EventName + f"-{i+1}", category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**textperms)})
                await ctx.guild.create_voice_channel(EventName.replace("-", " ") + f" {i+1}", category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**voiceperms)}, user_limit = user_limit)
        await ctx.guild.create_text_channel("staff-chat", category=ctx.guild.categories[position], overwrites = staffperms)
@bot.command(name='eventend')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def event_end(ctx):
    guild = ctx.message.guild

    cancel = False

    if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381:
        cancel = True

    if get(ctx.guild.categories, name="EVENTS") == None:
        await ctx.send("Command could not be processed: There is no event to end")
        cancel = True
        
    if not cancel:
        for channel in get(ctx.guild.categories, name="EVENTS").channels:
            if isinstance(channel, discord.VoiceChannel):
                if len(channel.members) != 0:
                    for member in channel.members:
                        await member.move_to(get(ctx.guild.channels, name="Chill Box 1"))
            await channel.delete()
        await get(ctx.guild.categories, name="EVENTS").delete()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="helping 🥊Brawlbox🥊", type=discord.ActivityType.playing))

@bot.event
async def process_category(category):
    n = 1
    numempty = 0
    templatename = None
    endchars = None
    for c in category.channels:
        if isinstance(c, discord.VoiceChannel):
            if len(c.members) == 0:
                numempty += 1
            match = re.match(r"(.*)\d+(.*)", c.name)
            if match:
                templatename = match.group(1)
                endchars = match.group(2)
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
    eventMoving = False
    for guild in bot.guilds:
        if get(member.guild.categories, name="EVENTS") != None:
            for channel in get(member.guild.categories, name="EVENTS").channels:
                if isinstance(channel, discord.VoiceChannel):
                    if len(channel.members) >= 1:
                        eventMoving = False
                        break
                    else:
                        eventMoving = True
                else:
                    break
    if not eventMoving:
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

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)

bot.run(token)