import asyncio
import pprint
from collections import deque
from dataclasses import dataclass

import discord
from discord import VoiceClient, VoiceProtocol
from discord.ext import commands

from yt_dlp import YoutubeDL

OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
}


@dataclass
class SongInfo:
    stream_url: str
    webpage_url: str
    title: str


class HeardleCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.last_played = None
        self.in_game = False
        self.queues: dict[int, deque[SongInfo]] = {}

    def get_queue(self, guild_id: int) -> deque[SongInfo]:
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    @staticmethod
    def get_link(query_or_url: str) -> SongInfo:
        """Obtains the first link from a YouTube search with given search"""
        with (YoutubeDL(OPTS) as ydl):
            print(f"Searching for {query_or_url}")
            info = ydl.extract_info(query_or_url, download=False)

            if 'entries' in info:
                info = info['entries'][0]

            return SongInfo(info['url'], info['webpage_url'], info['title'])

    async def stream_link(self, song_info: SongInfo, ctx: commands.Context):
        # TODO: This is not leaving vc...
        vc: VoiceProtocol = ctx.voice_client
        if len(vc.channel.members) > 1:  # 1 for self
            source = discord.FFmpegPCMAudio(song_info.stream_url,
                                            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            self.last_played = song_info
            vc.play(source, after=lambda error: self.bot.loop.create_task(self._stream_stopped(ctx, error)))
        else:
            await ctx.channel.send("No one in VC, leaving.")
            vc.stop()
            await vc.disconnect()


    async def _stream_stopped(self, ctx, error: Exception | None = None):
        """Callback function for each end of song."""
        queue = self.get_queue(ctx.guild.id)
        if error:
            await ctx.channel.send(f"There was an error playing the song: {error}")
        if queue:
            next_song = queue.popleft()
            await self.stream_link(next_song, ctx)

    @commands.command()
    async def queue(self, ctx: commands.Context, *search: str):
        """Queue to the appropriate guild."""
        search_term = ' '.join(search)
        song_info = self.get_link(search_term)
        queue = self.get_queue(ctx.guild.id)
        queue.append(song_info)
        await ctx.send(f"Queued: {song_info.title}")

    @commands.command()
    async def heardle(self, ctx: commands.Context, *search: str):
        ...

    @commands.command()
    async def play(self, ctx: commands.Context, *search: str):
        """Play command for simple audio streaming immediately (skips queue)"""
        author_state = ctx.author.voice
        if author_state is None:
            await ctx.channel.send("You must be in a voice channel.")
            return

        if ctx.voice_client is None:
            await author_state.channel.connect()
        else:
            await ctx.voice_client.move_to(author_state.channel)

        song_info = self.get_link(' '.join(search))
        await ctx.channel.send(f"Playing {song_info.title}")
        await self.stream_link(song_info, ctx)

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        """Leave the VC and pause playing"""
        await ctx.voice_client.disconnect(force=False)

    @commands.command()
    async def clear(self, ctx: commands.Context) -> None:
        """Clear the current queue"""
        self.queue.clear()
        await ctx.channel.send("Queue cleared.")
