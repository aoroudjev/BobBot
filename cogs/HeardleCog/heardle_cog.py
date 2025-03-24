from collections import deque

import discord
from discord import VoiceClient
from discord.ext import commands

from yt_dlp import YoutubeDL


class HeardleCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.last_played = None
        self.in_game = False
        self.queue = deque()

    def _start_stream(self):
        ...

    def _stream_stopped(self, ctx):
        print("Helo")

    @commands.command()
    async def heardle(self, ctx: commands.Context, *search: str):
        pass

    @commands.command()
    async def play(self, ctx: commands.Context, *search: str):
        """Play command for simple audio streaming"""
        # Stream setup
        info = self.get_link(''.join(search))
        source = discord.FFmpegPCMAudio(info['stream_url'],
                                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

        author_state = ctx.author.voice
        if author_state is None:
            await ctx.send("You must be in a voice channel.")

        vc = await author_state.channel.connect()

        vc.play(source, after=self._stream_stopped(ctx))

    @commands.command()
    async def leave(self, ctx: commands.Context) -> tuple[str, str]:
        ...

    def get_link(self, query_or_url: str):
        """Obtains the first link from a YouTube search with given search"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query_or_url, download=False)

            if 'entries' in info:
                info = info['entries'][0]

            return {
                'stream_url': info['url'],
                'webpage_url': info['webpage_url'],
                'title': info['title']
            }
