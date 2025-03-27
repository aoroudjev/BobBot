import asyncio
import os
import pprint
from collections import deque, defaultdict
from dataclasses import dataclass

import discord
from discord import VoiceClient, VoiceProtocol
from discord.ext import commands
from spotipy import Spotify, SpotifyClientCredentials

from yt_dlp import YoutubeDL

SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")

sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'noplaylist': False,
    'skip_download': True,
    'force_generic_extractor': False,
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
        self.queues = defaultdict(lambda: deque())

    def get_queue(self, guild_id: int) -> deque[SongInfo]:
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    @staticmethod
    def spotify_handler(link: str) -> list[str]:
        """Handle spotify link to resolve song(s)[playlist vs single song]"""
        if "track" in link:
            track = sp.track(link)
            return [f"{track['name']} {track['artists'][0]['name']}"]

        elif "playlist" in link:
            playlist = sp.playlist(link)
            tracks = playlist['tracks']['items']
            return [f"{t['track']['name']} {t['track']['artists'][0]['name']}" for t in tracks]
        return []

    async def stream_link(self, song_info: SongInfo, ctx: commands.Context):
        vc: VoiceClient = ctx.voice_client  # Abstract, ignore squiggle

        if len(vc.channel.members) > 1:  # 1 for self
            source = discord.FFmpegPCMAudio(song_info.stream_url,
                                            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            self.last_played = song_info
            vc.stop()
            vc.play(source, after=lambda error: self.bot.loop.create_task(self._stream_stopped(ctx, error)))
        else:
            await ctx.channel.send("No one in VC, leaving.")
            vc.stop()
            await vc.disconnect(force=False)

    @staticmethod
    def get_links(query_or_url: str) -> list[SongInfo]:
        """Obtains the first link from a YouTube search with given search"""
        results = []

        # Spotify support
        if query_or_url.lower().startswith("https://open.spotify.com"):
            queries = HeardleCog.spotify_handler(query_or_url)
            for q in queries:
                try:
                    with YoutubeDL(OPTS) as ydl:
                        info = ydl.extract_info(f"ytsearch1:{q}", download=False)
                        if 'entries' in info:
                            info = info['entries'][0]
                        results.append(SongInfo(info['url'], info['webpage_url'], info['title']))
                except:
                    continue
            return results

        # YouTube or search
        with YoutubeDL(OPTS) as ydl:
            info = ydl.extract_info(query_or_url, download=False)

            if 'entries' in info:
                    for entry in info['entries']:
                        try:
                            results.append(SongInfo(entry['url'], entry['webpage_url'], entry['title']))
                        except:
                            continue
            else:
                results.append(SongInfo(info['url'], info['webpage_url'], info['title']))

        return results

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

        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await self.play(ctx, *search)
        search_term = ' '.join(search)
        song_info = self.get_links(search_term)
        queue = self.get_queue(ctx.guild.id)
        queue += song_info
        await ctx.send(f"Queued {len(song_info)} songs.")

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

        queue = self.get_queue(ctx.guild.id)
        new_songs = self.get_links(' '.join(search))
        queue.extendleft(reversed(new_songs))
        await ctx.send(f"Playing {new_songs[0].title}")
        await self.stream_link(queue.popleft(), ctx)

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        """Leave the VC and pause playing"""
        await ctx.voice_client.disconnect(force=False)

    @commands.command()
    async def clear(self, ctx: commands.Context) -> None:
        """Clear the current queue"""
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        await ctx.channel.send("Queue cleared.")

    @commands.command()
    async def next(self, ctx: commands.Context) -> None:
        """Clear the current queue"""
        queue = self.get_queue(ctx.guild.id)
        if len(queue) > 0:
            await self.stream_link(queue.popleft(), ctx)
        else:
            await ctx.channel.send("Nothing in queue")

