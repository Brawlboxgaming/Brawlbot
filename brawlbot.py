'''Brawlbot made by Brawlbox
If you would like to use this code, please make sure to credit Brawlbox'''

from __future__ import unicode_literals
import os
import re
import asyncio
from discord.channel import VocalGuildChannel
from moviepy.editor import *
import youtube_dl as Youtube
import pydub

import discord
import discord.voice_client
from discord.ext import commands
from discord.utils import get

f = open("token.txt", "r")
token = f.readline()
f.close()

class VCQueue():

    def __init__(self, vcid, person, position, performing):
        self.vcid = vcid
        self.person = person
        self.position = position
        self.performing = performing

bot = commands.Bot(command_prefix='box>')

queue = False
eventqueueopen = False
eventqueuelist = []
eventqueueembed = None
eventqueuedisplay = ""
eventqueuestart = False
voice = None

performanceInfo = []

is_playing = False
is_paused = False
musicqueue = []
currentlyplaying = "*None*"
vc = "Music Box"
ydl_options = {'format': 'bestaudio', 'noplaylist': 'True'}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="Use box>h to display commands.", type=discord.ActivityType.playing))

@bot.command(name='h')
async def help_message(ctx):
    if ctx.channel.id == 805911876264525857 or ctx.channel.id == 806238209985085491 or ctx.channel.id == 845976543368445992:
        await ctx.channel.send(embed=discord.Embed(title="__**Help**__", description="""
            __**Commands**__

            ***Music***

            box>play {Link}

            *This will play the audio through discord with either a youtube or spotify link.*

            box>skip

            *This will skip the current song in the queue.*

            box>pause

            *This will pause the currently playing audio.*

            box>resume

            *This will continue the paused audio.*

            box>stop

            *This will stop the song currently playing.*

            ***Performance***

            box>join

            *Join the performance queue.*

            box>leave

            *Leave the performance queue.*

            box>start

            *Mutes everyone else so you can perform.*

            box>finish

            *Use when you have finished your performance.*

            ***Conversion and Downloading***

            box>wavtomp3 {Upload file}

            *This will convert the wav file you upload to an mp3 file.*

            box>dlmp4 "[Youtube Link]"

            *This will download youtube videos and send them as mp4s for you to download.*

            box>dlmp3 "[Youtube Link]"

            *This will download youtube videos and send them as mp3s for you to download.*

            **If you have any issues, please report them to <@105742694730457088>.**
            """, color=0xff0000)
            )
            
    elif ctx.channel.id == 805904615710523417 or ctx.channel.id == 805904638640783381:
        await ctx.channel.send(embed=discord.Embed(title="__**Help**__", description="""
            __**Commands**__

            ***Music***

            box>play {Link}

            *This will play the audio through discord with either a youtube or spotify link.*

            box>skip

            *This will skip the current song in the queue.*

            box>pause

            *This will pause the currently playing audio.*

            box>resume

            *This will continue the paused audio.*

            box>stop

            *This will stop the song currently playing.*

            ***Performance***

            box>join

            *Join the performance queue.*

            box>leave

            *Leave the performance queue.*

            box>start

            *Mutes everyone else so you can perform.*

            box>finish

            *Use when you have finished your performance.*

            ***Conversion and Downloading***

            box>wavtomp3 {Upload file}

            *This will convert the wav file you upload to an mp3 file.*

            box>dlmp4 "[Youtube Link]"

            *This will download youtube videos and send them as mp4s for you to download.*

            box>dlmp3 "[Youtube Link]"

            *This will download youtube videos and send them as mp3s for you to download.*

            ***Event Hosters Only***

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

            ***Moderators Only***

            box>clearqueue

            *This clears the queue for either a performance or music.

            box>skipqueue

            *This skips the next person in the queue/currently performing.

            **If you have any issues, please report them to <@105742694730457088>.**
            """, color=0xff0000)
            )

def search_yt(item):
    global ydl_options
    try:
        info = Youtube.YoutubeDL(ydl_options).extract_info("ytsearch:%s" % item, download=False)['entries'][0]
    except Exception:
        return False
    
    return {'source': info['formats'][0]['url'], 'title': info['title']}

async def play_music(ctx):
    global is_playing
    global musicqueue
    global voice
    global currentlyplaying
    channel = discord.utils.get(ctx.guild.channels, name='Music Box')
    if len(musicqueue) > 0:
        is_playing = True

        m_url = musicqueue[0][0]['source']

        try: 
            await channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        except: voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        currentlyplaying = musicqueue[0][0]['title']
        await ctx.send(f"Currently playing: {currentlyplaying}")
        musicqueue.pop(0)
        ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        voice.play(discord.FFmpegPCMAudio(rf"{m_url}", **ffmpeg_options), after=lambda e: play_music(ctx))
    while voice.is_playing() or is_paused:
        await asyncio.sleep(1)
    else:
        currentlyplaying = "*None*"
        if len(musicqueue) > 0:
            await play_music(ctx)
        is_playing = False
        await asyncio.sleep(15)
        while voice.is_playing():
            break
        else:
            voice.stop()
            await voice.disconnect()

@bot.command(name="join")
async def join(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            if len(performanceInfo) > int(ctx.author.voice.channel.name[-1])-1:
                for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                    if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person == ctx.author:
                        await ctx.channel.send("You are already in the queue.")
                        return False
        except:
            pass
        if len(performanceInfo) > int(ctx.author.voice.channel.name[-1])-1:
            performanceInfo[int(ctx.author.voice.channel.name[-1])-1].append(VCQueue(ctx.author.voice.channel.id, ctx.author, len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]), False))
            await ctx.channel.send(f"<@{ctx.author.id}> has joined the queue.")
        else:
            temp = []
            tempPosition = 0
            if len(performanceInfo) > 0:
                try:
                    tempPosition = len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])
                except:
                    pass
            temp.append(VCQueue(ctx.author.voice.channel.id, ctx.author, tempPosition, False))
            performanceInfo.append(temp)
            await ctx.channel.send(f"<@{ctx.author.id}> has joined the queue.")

@bot.command(name="leave")
async def leave(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            if len(performanceInfo) > int(ctx.author.voice.channel.name[-1])-1:
                for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                    if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person == ctx.author:
                        await ctx.channel.send(f"<@{ctx.author.id}> has left the queue")
                        if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                            for member in discord.utils.get(ctx.guild.channels, name=ctx.author.voice.channel.name).members:
                                if member.id != performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person.id:
                                    await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, speak=True)
                                    await member.move_to(discord.utils.get(ctx.guild.channels, name="Welcome to The Brawl Box"))
                                    await member.move_to(ctx.author.voice.channel)
                                else:
                                    await discord.utils.get(ctx.guild.roles, name=ctx.author.voice.channel.name).delete()
                        performanceInfo[int(ctx.author.voice.channel.name[-1])-1].pop(i)
                        return False
                await ctx.channel.send("You aren't in the queue.")
        except:
            pass

@bot.command(name="start")
async def start(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person == ctx.author:
                    if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                        await ctx.channel.send("You are already performing.")
                        return False
                elif performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                    await ctx.channel.send("Someone else is currently performing.")
                    return False
        except:
            pass
        try:
            if len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]) == 0:
                await ctx.channel.send("The queue is empty.")
        except:
            await ctx.channel.send("The queue is empty.")
        if len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]) != 0:
            if ctx.author.voice.channel.category.name != "PERFORMANCE":
                await ctx.channel.send("You need to be in a performance voice channel to use this command")
            if ctx.author == performanceInfo[int(ctx.author.voice.channel.name[-1])-1][0].person:
                performanceInfo[int(ctx.author.voice.channel.name[-1])-1][0].performing = True
                await ctx.channel.send(f"<@{ctx.author.id}> is now performing.")
                for member in discord.utils.get(ctx.guild.channels, name=ctx.author.voice.channel.name).members:
                    if member.id != ctx.author.id:
                        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, speak=False)
                        await member.move_to(discord.utils.get(ctx.guild.channels, name="Welcome to The Brawl Box"))
                        await member.move_to(ctx.author.voice.channel)
                    else:
                        await ctx.guild.create_role(name=ctx.author.voice.channel.name)
                        role = discord.utils.get(ctx.guild.roles, name=ctx.author.voice.channel.name)
                        await ctx.author.voice.channel.set_permissions(role, speak=True)
                        await member.add_roles(role)
            else:
                await ctx.channel.send("You are not next in the queue.")

@bot.command(name="finish")
async def finish(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            if len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]) == 0:
                await ctx.channel.send("The queue is empty.")
        except:
            await ctx.channel.send("The queue is empty.")
        try:
            for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person == ctx.author:
                    if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                        await ctx.channel.send(f"<@{ctx.author.id}> has finished performing.")
                        performanceInfo[int(ctx.author.voice.channel.name[-1])-1].pop(0)
                        for member in discord.utils.get(ctx.guild.channels, name=ctx.author.voice.channel.name).members:
                            if member.id != ctx.author.id:
                                await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, speak=True)
                                await member.move_to(discord.utils.get(ctx.guild.channels, name="Welcome to The Brawl Box"))
                                await member.move_to(ctx.author.voice.channel)
                            else:
                                await discord.utils.get(ctx.guild.roles, name=ctx.author.voice.channel.name).delete()
                        
                elif performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                    await ctx.channel.send("Someone else is currently performing.")
                    return False
        except:
            pass

@bot.command(name="skipqueue")
@commands.has_any_role("📦ModBox📦", "📦AdminBox📦", "📦DemiBox📦", "📦BoxGod📦")
async def skipqueue(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            if len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]) == 0:
                await ctx.channel.send("The queue is empty.")
        except:
            await ctx.channel.send("The queue is empty.")
        try:
            if len(performanceInfo) > int(ctx.author.voice.channel.name[-1])-1:
                for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                    await ctx.channel.send(f"<@{performanceInfo[int(ctx.author.voice.channel.name[-1])-1][0].person.id}> has been skipped.")
                    if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                        for member in discord.utils.get(ctx.guild.channels, name=ctx.author.voice.channel.name).members:
                            if member.id != performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person.id:
                                await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, speak=True)
                                currentVC = ctx.author.voice.channel
                                await member.move_to(discord.utils.get(ctx.guild.channels, name="Welcome to The Brawl Box"))
                                await member.move_to(currentVC)
                            else:
                                await discord.utils.get(ctx.guild.roles, name=ctx.author.voice.channel.name).delete()
                    performanceInfo[int(ctx.author.voice.channel.name[-1])-1].pop(0)
                    return False
        except:
            pass

@bot.command(name="clearqueue")
@commands.has_any_role("📦ModBox📦", "📦AdminBox📦", "📦DemiBox📦", "📦BoxGod📦")
async def clearqueue(ctx):
    if ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        try:
            if len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1]) == 0:
                await ctx.channel.send("The queue is empty.")
        except:
            await ctx.channel.send("The queue is empty.")
        
        if len(performanceInfo) > int(ctx.author.voice.channel.name[-1])-1:
            for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                    for member in discord.utils.get(ctx.guild.channels, name=ctx.author.voice.channel.name).members:
                        if member.id != performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person.id:
                            await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, speak=True)
                            currentVC = ctx.author.voice.channel
                            await member.move_to(discord.utils.get(ctx.guild.channels, name="Welcome to The Brawl Box"))
                            await member.move_to(currentVC)
                        else:
                            await discord.utils.get(ctx.guild.roles, name=ctx.author.voice.channel.name).delete()
                for i in range(len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                    performanceInfo[int(ctx.author.voice.channel.name[-1])-1].pop(0)
                await ctx.channel.send("The queue has been cleared.")
                return False

@bot.command(name="queue")
async def queue(ctx):
    if ctx.channel.id == 806238209985085491:
        global musicqueue
        global currentlyplaying
        retval = ""
        for i in range(0, len(musicqueue)):
            retval += "- " + musicqueue[i][0]['title'] + "\n"
        
        if retval != "":
            await ctx.channel.send(embed=discord.Embed(title="__**Queue**__", description=f"""
            __Currently Playing__
            - {currentlyplaying}

            __Up Next__
            {retval}
            """, color=0xff0000))
        else:
            await ctx.channel.send(embed=discord.Embed(title="__**Queue**__", description=f"""
            __Currently Playing__
            - {currentlyplaying}

            __Up Next__
            - *No music in the queue*
            """, color=0xff0000))
    elif ctx.channel.id == 845976543368445992:
        global performanceInfo
        if ctx.author.voice == None:
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        elif ctx.author.voice.channel.category.name != "PERFORMANCE":
            await ctx.channel.send("You need to be in a performance voice channel to use this command.")
            return False
        currentlyperforming_display = "*None*"
        retval = ""
        if len(performanceInfo) > 0:
            for i in range(0, len(performanceInfo[int(ctx.author.voice.channel.name[-1])-1])):
                if performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].performing:
                    currentlyperforming_display = f"<@{performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person.id}>"
                else:
                    retval += f"- <@{performanceInfo[int(ctx.author.voice.channel.name[-1])-1][i].person.id}>\n"
        
        if retval != "":
            await ctx.channel.send(embed=discord.Embed(title=f"__**Performance {ctx.author.voice.channel.name[-1]} Queue**__", description=f"""
            __Currently Performing__
            - {currentlyperforming_display}

            __Up Next__
            {retval}
            """, color=0xff0000))
        else:
            await ctx.channel.send(embed=discord.Embed(title=f"__**Performance {ctx.author.voice.channel.name[-1]} Queue**__", description=f"""
            __Currently Performing__
            - {currentlyperforming_display}

            __Up Next__
            - *No people in the queue*
            """, color=0xff0000))

@bot.command(name='play')
async def play(ctx, *args):
    if ctx.channel.id == 806238209985085491:
        global is_playing
        global musicqueue
        channel = discord.utils.get(ctx.guild.channels, name='Music Box')
        query = " ".join(args)

        song = search_yt(query)
        if type(song) == type(True):
            await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream.")
        else:
            await ctx.send("Song added to the queue")
            musicqueue.append([song, channel])

            if is_playing == False:
                await play_music(ctx)

@bot.command(name="stop")
async def skip(ctx):
    if ctx.channel.id == 806238209985085491:
        global musicqueue
        global is_playing
        global voice
        musicqueue = []
        is_playing = False
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()
        await ctx.send("Music stopped")

@bot.command(name="skip")
async def skip(ctx):
    if ctx.channel.id == 806238209985085491:
        global voice
        global musicqueue
        if len(musicqueue) > 0 or is_playing:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice.stop()
            await ctx.send("Music skipped")
        else:
            await ctx.send("There is no music to be skipped")


@bot.command(name="pause")
async def skip(ctx):
    if ctx.channel.id == 806238209985085491:
        global voice
        global is_paused
        is_paused = True
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.pause()
        await ctx.send("Music paused")

@bot.command(name="resume")
async def skip(ctx):
    if ctx.channel.id == 806238209985085491:
        global voice
        global is_paused
        is_paused = False
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.resume()
        await ctx.send("Music resumed")

@bot.command(name='wavtomp3')
async def wav_to_mp3(ctx):
    title = ctx.message.attachments[0].filename[:-4].replace("\"", "'").replace("(", "[").replace(")", "]")
    await ctx.message.attachments[0].save(rf"{title}.wav")

    await asyncio.sleep(1)

    pydub.AudioSegment.from_mp3(f"{title}.wav").export(rf"{title}.mp3", format="wav")
    if os.path.exists(rf"{title}.wav"):
        os.remove(rf"{title}.wav")

    os.system(rf'sudo cp "{title}.mp3" /var/www/brawlbox/')

    await ctx.message.author.send(f"http://brawlbox.xyz/{title}.mp3")

    await asyncio.sleep(5)

    if os.path.exists(rf"{title}.mp3"):
        os.remove(rf"{title}.mp3")

@bot.command(name='dlmp4')
async def mp4_get(ctx, YoutubeLink):
    Youtube.YoutubeDL().add_default_info_extractors()
    title = Youtube.YoutubeDL().extract_info(YoutubeLink, download=False)['title'].replace("\"", "'").replace("(", "[").replace(")", "]").replace(" ", "_").replace("&", "and").replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_").replace("#", "")
    outs = {
    'format':' bestvideo[ext=mp4]+bestaidop[ext=mp4]/mp4',
	'outtmpl': rf'{title}.mp4'
    }
    with Youtube.YoutubeDL(outs) as ytdl:
	    ytdl.download([YoutubeLink])

    print(os.getcwd())
    
    os.system(rf'sudo cp "{title}.mp4" /var/www/brawlbox/')

    await ctx.message.author.send(rf"http://brawlbox.xyz/{title}.mp4")

    await asyncio.sleep(5)
    
    if os.path.exists(rf"{title}.mp4"):
        os.remove(rf"{title}.mp4")

@bot.command(name='dlmp3')
async def mp3_get(ctx, YoutubeLink):
    Youtube.YoutubeDL().add_default_info_extractors()
    title = Youtube.YoutubeDL().extract_info(YoutubeLink, download=False)['title'].replace("\"", "'").replace("(", "[").replace(")", "]").replace(" ", "_").replace("&", "and").replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_").replace("#", "")
    outs = {
    'format':' bestvideo[ext=mp4]+bestaidop[ext=mp4]/mp4',
	'outtmpl': rf'{title}.mp4'
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
        
    os.system(rf'sudo cp "{title}.mp3" /var/www/brawlbox/')

    await ctx.message.author.send(rf"http://brawlbox.xyz/{title}.mp3")

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
    global performanceInfo
    global category_update_active
    if member.id == 105742694730457088 and member.voice != None and (member.voice.mute or member.voice.deaf):
        await member.edit(mute=False)
        await member.edit(deafen=False)
    if before.channel != None and before.channel.category.name == "PERFORMANCE":
        try:
            for i in range(len(before.channel.name[-1])):
                if performanceInfo[int(before.channel.name[-1])-1][i].person == member:
                    if performanceInfo[int(before.channel.name[-1])-1][i].performing:
                        await discord.utils.get(member.guild.roles, name=before.channel.name).delete()
                    performanceInfo[int(before.channel.name[-1])-1].pop(i)
                    await bot.get_channel(845976543368445992).send(f"<@{member.id}> has left the voice channel, so has been ejected from the queue.")
                    break
        except:
            pass
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
    print(error)

bot.run(token)
