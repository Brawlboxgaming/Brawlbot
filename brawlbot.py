'''Brawlbot made by Brawlbox
If you would like to use this code, please make sure to credit Brawlbox'''

from __future__ import unicode_literals
import os
import subprocess
import re
import asyncio
from moviepy.editor import *
import youtube_dl as Youtube
import pydub

import discord
from discord.ext import commands
from discord.utils import get

f = open("token.txt", "r")
token = f.readline()
f.close()

bot = commands.Bot(command_prefix='box>')

queue = False
eventqueueopen = False
eventqueuelist = []
eventqueueembed = None
eventqueuedisplay = ""
eventqueuestart = False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="helping 🥊Brawlbox🥊", type=discord.ActivityType.playing))

@bot.command(name='h')
async def help_message(ctx):
    await ctx.channel.send(embed=discord.Embed(title="__**Help**__", description="""
        __**Commands**__

        box>wavtomp3 {Upload file}

        *This will convert the wav file you upload to an mp3 file.

        box>dlmp4 "[Youtube Link]"

        *This will download youtube videos and send them as mp4s for you to download.*

        box>dlmp3 "[Youtube Link]"

        *This will download youtube videos and send them as mp3s for you to download.*

        box>startevent "[Event Name]" [MembersCanType] [MembersCanSpeak] [Capacity] [NumberOfVCs] [EnableQueue]

        *This is how to create an event. The 2nd, 3rd, and 6th arguments can only be "True" or "False", and the 4th and 5th can only be a number. (Note: the square brackets are just for placeholders and do not need to be put in the command.)*

        box>endevent

        *When the event is over, this is used to clean up and delete the event channels.*

        box>openeventqueue

        *This opens the event queue and allows people to join the queue.*

        box>closeeventqueue

        *This closes the event queue and prevents people from joining the queue. This is the default.*

        box>starteventqueue

        *This starts keeping track of the queue and removes people when the "nexteventqueue" command is used.*

        box>stopeventqueue

        *This stops the event queue tracking.*

        box>nexteventqueue

        *This pings the next user on the queue and starts cleaning up the queue embed in the event queue channel.*

        **If you have any issues, please report them to <@105742694730457088>.**
        """, color=0xff0000)
        )

@bot.command(name='wavtomp3')
async def wav_to_mp3(ctx):
    title = ctx.message.attachments[0].filename[:-4]
    await ctx.message.attachments[0].save(f"{title}.wav")

    await asyncio.sleep(1)

    pydub.AudioSegment.from_mp3(f"{title}.wav").export(f"{title}.mp3", format="wav")
    if os.path.exists(f"{title}.wav"):
        os.remove(f"{title}.wav")

    os.system(f"sudo cp {title}.mp3 /var/www/html/")

    await ctx.message.author.send(f"http://brawlbox.xyz/{title}.mp3")

    await asyncio.sleep(5)

    if os.path.exists(f"{title}.mp3"):
        os.remove(f"{title}.mp3")

@bot.command(name='dlmp4')
async def mp4_get(ctx, YoutubeLink):
    Youtube.YoutubeDL().add_default_info_extractors()
    title = Youtube.YoutubeDL().extract_info(YoutubeLink, download=False)['title'].replace("(", "[").replace(")", "]").replace(" ", "_").replace("&", "and").replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
    outs = {
    'format':' bestvideo[ext=mp4]+bestaidop[ext=mp4]/mp4',
	'outtmpl': f'{title}.mp4'
    }
    with Youtube.YoutubeDL(outs) as ytdl:
	    ytdl.download([YoutubeLink])

    print(os.getcwd())
    
    os.system(f"sudo cp {title}.mp4 /var/www/html/")

    await ctx.message.author.send(f"http://brawlbox.xyz/{title}.mp4")

    await asyncio.sleep(5)
    
    if os.path.exists(f"{title}.mp4"):
        os.remove(f"{title}.mp4")

@bot.command(name='dlmp3')
async def mp3_get(ctx, YoutubeLink):
    Youtube.YoutubeDL().add_default_info_extractors()
    title = Youtube.YoutubeDL().extract_info(YoutubeLink, download=False)['title'].replace("(", "[").replace(")", "]").replace(" ", "_").replace("&", "and").replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
    outs = {
    'format':' bestvideo[ext=mp4]+bestaidop[ext=mp4]/mp4',
	'outtmpl': f'{title}.mp4'
    }
    with Youtube.YoutubeDL(outs) as ytdl:
	    ytdl.download([YoutubeLink])

    mp4_file = rf"{title}.mp4"
    mp3_file = rf"{title}.mp3"
    
    videoclip = VideoFileClip(mp4_file)
    audioclip = videoclip.audio
    audioclip.write_audiofile(mp3_file)
    
    audioclip.close()
    videoclip.close()
    
    if os.path.exists(mp4_file):
        os.remove(mp4_file)
        
    os.system(f"sudo cp {title}.mp3 /var/www/html/")

    await ctx.message.author.send(f"http://brawlbox.xyz/{title}.mp3")

    await asyncio.sleep(30)

    if os.path.exists(mp3_file):
        os.remove(mp3_file)

@bot.command(name='startevent')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def event_start(ctx, EventName, MembersCanType, MembersCanSpeak, Capacity, VCCount, EnableQueue):

    cancel = False
    global queue
    global eventqueueembed

    if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381 and ctx.channel.category.name != "EVENTS":
        cancel = True

    if MembersCanSpeak.lower() == "true":
        Speak = True
    elif MembersCanSpeak.lower() == "false":
        Speak = False
    else:
        cancel = True
        await ctx.send("Command could not be processed: Invalid 'MembersCanSpeak' argument")

    if MembersCanType.lower() == "true":
        Type = True
    elif MembersCanType.lower() == "false":
        Type = False
    else:
        cancel = True
        await ctx.send("Command could not be processed: Invalid 'MembersCanType' argument")
        
    if EnableQueue.lower() == "true":
        queue = True
    elif EnableQueue.lower() == "false":
        queue = False
    else:
        cancel = True
        await ctx.send("Command could not be processed: Invalid 'EnableQueue' argument")
    
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
        queueperms = {
        'send_messages': False
        }
        if queue:
            await ctx.guild.create_text_channel(EventName + " queue", category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**queueperms)})
            for channel in get(ctx.guild.categories, name="EVENTS").channels:
                if "queue" in channel.name:
                    eventqueueembed = await channel.send(embed=discord.Embed(title="__**Queue**__", description="**Queue Closed**", color=0xff0000))
        if VCCount == 1:
            await ctx.guild.create_text_channel(EventName, category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**textperms)})
            await ctx.guild.create_voice_channel(EventName.replace("-", " "), category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**voiceperms)}, user_limit = user_limit)
        else:
            for i in range(VCCount):
                await ctx.guild.create_text_channel(EventName + f"-{i+1}", category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**textperms)})
                await ctx.guild.create_voice_channel(EventName.replace("-", " ") + f" {i+1}", category=ctx.guild.categories[position], overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(**voiceperms)}, user_limit = user_limit)
        await ctx.guild.create_text_channel("staff-chat", category=ctx.guild.categories[position], overwrites = staffperms)

@bot.command(name='endevent')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def event_end(ctx):

    cancel = False
    global queue
    global eventqueueopen
    global eventqueuedisplay
    global eventqueuelist
    queue = False
    eventqueueopen = False
    eventqueuedisplay = ""
    eventqueuelist = []

    if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381 and ctx.channel.category.name != "EVENTS":
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

@bot.command(name='openeventqueue')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def open_queue(ctx):

    cancel = False
    global queue
    global eventqueuelist
    global eventqueueopen
    global eventqueueembed
    global eventqueuedisplay

    if queue:
        if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381 and ctx.channel.category.name != "EVENTS":
            cancel = True
        
        if eventqueueopen:
            await ctx.channel.send("Command could not be processed: Queue is already open")
            cancel = True

        if not cancel:
            for channel in ctx.channel.category.channels:
                if "queue" in channel.name:
                    if eventqueuelist != []:
                        eventqueuedisplay = ""
                        for member in eventqueuelist:
                            eventqueuedisplay += f"<@{member}>\n-----------------------------\n"
                        await eventqueueembed.edit(embed=discord.Embed(title="__**Queue**__", description=f"{eventqueuedisplay}", color=0xff0000))
                    else:
                        await eventqueueembed.edit(embed=discord.Embed(title="__**Queue**__", description="*Queue Empty*", color=0xff0000))
            await ctx.channel.send(f"The queue has now been opened. Ping <@{bot.user.id}> to join the queue.")
            eventqueueopen = True

    else:
        await ctx.channel.send("Command could not be processed: Queue is not available for this event")

@bot.command(name='closeeventqueue')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def close_queue(ctx):

    cancel = False
    global queue
    global eventqueueopen
    global eventqueuedisplay
    global eventqueueembed

    if queue:
        if ctx.channel.id != 805904615710523417 and ctx.channel.id != 805904638640783381 and ctx.channel.category.name != "EVENTS":
            cancel = True
        
        if not eventqueueopen:
            await ctx.channel.send("Command could not be processed: Queue is already closed.")
            cancel = True

        if not cancel:
            eventqueuedisplay += "**Queue Closed**"
            await eventqueueembed.edit(embed=discord.Embed(title="__**Queue**__", description=f"{eventqueuedisplay}", color=0xff0000))
            await ctx.channel.send("The queue is now closed.")
            eventqueueopen = False

    else:
        await ctx.channel.send("Command could not be processed: Queue is not available for this event")

@bot.command(name="starteventqueue")
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def start_queue(ctx):
    global queue
    global eventqueuestart
    global eventqueuelist

    if queue:
        if not eventqueuestart:
            if eventqueuelist != []:
                await ctx.channel.send(f"The first user is <@{eventqueuelist[0]}>")
                eventqueuestart = True
            else:
                await ctx.channel.send("Queue could not start: Queue is empty")
                eventqueuestart = False
        else:
            await ctx.channel.send("Queue could not start: Queue has already been started")

    else:
        await ctx.channel.send("Command could not be processed: Queue is not available for this event")

@bot.command(name="stopeventqueue")
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def start_queue(ctx):
    global queue
    global eventqueuestart

    if queue:
        if eventqueuestart:
            await ctx.channel.send("Queue has been stopped")
            eventqueuestart = False
        else:
            await ctx.channel.send("Queue could not stop: Queue has not been started yet")

    else:
        await ctx.channel.send("Command could not be processed: Queue is not available for this event")

@bot.command(name='nexteventqueue')
@commands.has_any_role("Event Hoster (NA)", "Event Hoster (EU)")
async def next_queue(ctx):
    global queue
    global eventqueueopen
    global eventqueuelist
    global eventqueuedisplay
    global eventqueuestart

    if queue:
        if eventqueuestart:
            eventqueuelist.pop(0)
            if eventqueuelist != []:
                eventqueuedisplay = ""
                for member in eventqueuelist:
                    eventqueuedisplay += f"<@{member}>\n----------------------------\n"
                if not eventqueueopen:
                    eventqueuedisplay += "**Queue Closed**"
                await ctx.channel.send(f"The next user is <@{eventqueuelist[0]}>")
            else:
                await ctx.channel.send("There is no next user")
                eventqueuedisplay = "*Queue Empty*"
                eventqueuedisplay += "\n----------------------------\n**Queue Closed**"
            await eventqueueembed.edit(embed=discord.Embed(title="__**Queue**__", description=f"{eventqueuedisplay}", color=0xff0000))
        else:
            await ctx.channel.send("Command could not be processed: The queue has not been started")

    else:
        await ctx.channel.send("Command could not be processed: Queue is not available for this event")

@bot.event
async def on_message(message):
    global eventqueueopen
    global eventqueueembed
    global eventqueuelist
    global eventqueuedisplay

    if eventqueueopen:
        if '@BrawlBot' in message.clean_content and queue and message.channel.category.name == "EVENTS":
            eventqueuedisplay = ""
            if f"{message.author.id}" not in eventqueuelist:
                eventqueuelist.append(f"{message.author.id}")
                for member in eventqueuelist:
                    eventqueuedisplay += f"<@{member}>\n----------------\n"
                await message.channel.send(f"<@{message.author.id}> was added to the queue")
                await eventqueueembed.edit(embed=discord.Embed(title="__**Queue**__", description=f"{eventqueuedisplay}", color=0xff0000))
            else:
                await message.channel.send("Could not add you to the queue: You are already in the queue")
    else:
        if f'<@!{bot.user.id}>' in message.content:
            await message.channel.send("Could not add you to the queue: The queue is closed")

    await bot.process_commands(message)

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

category_update_active = False

@bot.event
async def on_voice_state_update(member, before, after):
    global category_update_active
    while category_update_active:
        await asyncio.sleep(1)
    category_update_active = True
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
    category_update_active = False

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)

bot.run(token)