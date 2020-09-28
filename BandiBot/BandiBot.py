import discord
import youtube_dl
import random
import audioread
import datetime
import asyncio
import nacl
import os
import time
from discord.ext import commands, tasks
from discord import FFmpegPCMAudio
from discord.voice_client import VoiceClient
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingPermissions
from discord.utils import get
from youtube_dl import YoutubeDL
from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.timestamp = data.get('timestamp')
        self.start_time = data.get('start_time ')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        try:
            loop = loop or asyncio.get_event_loop()
            try:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            except:
                await ctx.send('An error ocurred. Try again')
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]

            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        except:
            await ctx.send('An error ocurred. Try again')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def greet(self, ctx):
        """Greets you with a hello [Format: -greet]"""
        await ctx.send(f'Hello! I\'m BandiBot :smile:')

    @commands.command()
    async def join(self, ctx):
        """Makes BandiBot join your Voice Chat [Format: -join]""" 
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send('Joined :thumbsup:')
            rand = random.randint(1, 2)
            if rand == 1:
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("hello.mp3"))
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            else:
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("hi.mp3"))
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            await ctx.send('Already in a voice channel...')
        

    @commands.command()
    async def leave(self, ctx):
        """Disconnects BandiBot from voice chat [Format: -leave]"""
        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send('> Goodbye! :pleading_face:')
        else: 
            await ctx.send("> I'm not even in a voice channel :man_facepalming: ")

    @commands.command()
    async def disconnectall(self, ctx):
        """Disconnects BandiBot from voice chat [Format: -leave]"""
        member: discord.Member
        for y in ctx.author.voice.channel:
            await member.edit(voice_channel=None)

        if (ctx.voice_client):
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bye.mp3"))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('> Change da world. My final message. Goodbye')
            # time.sleep(14)
            await ctx.guild.voice_client.disconnect()
        else: 
            await ctx.send("> I'm not even in a voice channel :man_facepalming: ")

    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        """Kicks a user from any voice channel [Format: -kick + User]"""
        query = str(member)
        owncheck = str(ctx.author)
        if "bandia" in [y.name.lower() for y in ctx.message.author.roles] or owncheck == query:
            if query == "BandiBot#8841":
                await ctx.send('> What the hell are you doing? If you want me to leave use the -leave command.')
            elif owncheck == query:
                await member.edit(voice_channel=None)
                await ctx.send("> Okay, you got yourself kicked... Hope you are proud :neutral_face: ")
            else:
                await member.edit(voice_channel=None)
                await ctx.send('> Kicked ' + query[:-5] + "  :hammer: ")
        else:
            await ctx.send('> You don\'t have permission to do that...')
    @kick.error
    async def on_ready(self, ctx, query):
        if "bandia" in [y.name.lower() for y in ctx.message.author.roles]:
            await ctx.send("> That username isn't in your voice chat... (Remember that the query is case sensitive)")
        else:
            await ctx.send("> You don\'t have permission to do that...")

    @commands.command()
    async def move(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        """Moves user to another voice channel[Format: -move + Username + Channel]"""
        query = str(channel)
        username = str(member)
        owncheck = str(ctx.author)
        if "bandia" in [y.name.lower() for y in ctx.message.author.roles] or owncheck == query:
            if username == "BandiBot#8841":
                if (ctx.voice_client):
                    await ctx.send('> Okay... Moving myself to \"' + str(channel) + "\"")
                    await ctx.voice_client.disconnect()
                    await channel.connect()
                else:
                    await ctx.send("> I\'m not in a voice channel")
            elif owncheck == username:
                await member.move_to(channel)
                await ctx.send("> Okay... Moving you to \"" + str(channel) + "\"")
            else:
                if member in channel.members:
                    await ctx.send('> That user is already in that channel')
                else:
                    await member.move_to(channel)
                    await ctx.send("> Moving " + username[:-5] + " to \"" + str(channel) + "\"")               
        else:
            await ctx.send('> You don\'t have permission to do that...')
    @move.error
    async def on_ready(self, ctx, query):
        if "bandia" in [y.name.lower() for y in ctx.message.author.roles]:
            if "Member" in str(query) and "not found" in str(query):
                await ctx.send("> That username is not in any voice channel")
            elif "Channel" in str(query) and "not found." in str(query):
                await ctx.send("> That voice channel does not exist")
            else:
                await ctx.send("> That user is not in any voice channel")
        else:
            await ctx.send("> You don\'t have permission to do that...")

    @commands.command()
    async def goto(self, ctx, *, channel: discord.VoiceChannel):
        """Makes BandiBot go to a specific channel [Format: -goto + Channel]"""
        if (ctx.voice_client):
            await ctx.voice_client.disconnect()
            await channel.connect()
        else:
            await channel.connect()

    @commands.command()
    async def stream(self, ctx, *, query):

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def play(self, ctx, *, url):
        """Searches and plays a song from youtube [Format: -play + song]"""
        async with ctx.typing():
            global player
            global start 
            global current
            global TotalTime
            global PauseCurrent
            global PauseTime
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('> Playing from youtube: {}'.format(player.title))
            start = time.time()

    @commands.command()
    async def pause(self, ctx):
        """Pauses currently playing song [Format: -pause]"""
        try:
            SongPlaying = ctx.voice_client.is_playing()
            Paused = ctx.voice_client.is_paused()
            if Paused != True and SongPlaying == True:
                PauseCurrent = time.time()
                ctx.voice_client.pause()
                await ctx.send(str(PauseCurrent))
                await ctx.send("> The player is now paused")
            elif Paused == True and SongPlaying == False:
                await ctx.send("> The player is already paused.")
            else:
                await ctx.send("> No song is playing right now")   
        except:
            await ctx.send('> I\'m not connected to a voice channel')

    @commands.command()
    async def p(self, ctx):
        # try:
            PauseTime = PauseCurrent - start
            await ctx.send(str(PauseTime))   
        # except:
        #     await ctx.send("No pause time")

    @commands.command()
    async def np(self, ctx):
        try:
            SongPlaying = ctx.voice_client.is_playing()
            current = time.time()
            await ctx.send(str(PauseCurrent))
            if PauseCurrent == 0:
                TotalTime = int(current - start)
            else:
                PauseTime = current - PauseCurrent
                TotalTime = start - PauseTime
                await ctx.send(str(PauseTime))   
            await ctx.send('> Now Playing: {}'.format(player.title) + "\n > " + str(datetime.timedelta(seconds=TotalTime)) + " - " + str(datetime.timedelta(seconds=player.duration))) 
        except:
            await ctx.send('> Nothing\'s playing...')

    @commands.command()
    async def resume(self, ctx):
        """Resumes a paused song [Format: -resume]"""
        try:
            SongPlaying = ctx.voice_client.is_playing()
            Paused = ctx.voice_client.is_paused()
            if Paused == True and SongPlaying == False:
                ctx.voice_client.resume()
                await ctx.send('> Resuming song...')
            elif SongPlaying == False:
                await ctx.send('> There is no song to resume...')
            else:
                await ctx.send('> The player is not paused')
        except:
            await ctx.send('> I\'m not connected to a voice channel')

    @commands.command()
    async def stop(self, ctx):
        try:
            SongPlaying = ctx.voice_client.is_playing()
            Paused = ctx.voice_client.is_paused()
            if SongPlaying == True:
                ctx.voice_client.stop()
                await ctx.send('> Song stopped')
            else:
                if Paused == True:
                    ctx.voice_client.stop()
                    await ctx.send('> Song stopped')
                else:
                    await ctx.send('> There is no song to stop...')
        except:
            await ctx.send('> I\'m not connected to a voice channel')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes volume of the player [Format: -volume + percentage]"""
        if ctx.voice_client is None:
            return await ctx.send("What? Where?... You are not in a voice channel :confused: ")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Volume has been changed to {}%".format(volume))

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("> You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"),
                   description='Bandibot Help. All usernames and channels are case sensitive', case_insensitive=True)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))

bot.add_cog(Music(bot))
bot.run('NzUzODY1Njg3OTYwNjQ5NzQ5.X1saIg.MoZ4Fu-85OT_0PX51aaZZvVNrmY')