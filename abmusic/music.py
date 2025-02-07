import asyncio

import async_timeout
import wavelink
from discord import ClientException
from discord.ext import commands
from wavelink import (LavalinkException, LoadTrackError, SoundCloudTrack,
                      YouTubeMusicTrack, YouTubePlaylist, YouTubeTrack)
from wavelink.ext import spotify
from wavelink.ext.spotify import SpotifyTrack

from ._classes import Provider
from .checks import voice_channel_player, voice_connected
from .errors import MustBeSameChannel
from .paginator import Paginator
from .player import DisPlayer


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.loop.create_task(self.start_nodes())

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    async def play_track(self, ctx: commands.Context, query: str, provider=None):
        player: DisPlayer = ctx.voice_client

        if ctx.author.voice.channel.id != player.channel.id:
            raise MustBeSameChannel(
                "❌ You must be in the same voice channel as the bot!"
            )

        track_providers = {
            "yt": YouTubeTrack,
            "ytpl": YouTubePlaylist,
            "ytmusic": YouTubeMusicTrack,
            "soundcloud": SoundCloudTrack,
            "spotify": SpotifyTrack,
        }

        query = query.strip("<>")
        msg = await ctx.send(f":mag_right: Searching for `{query}`")

        track_provider = provider if provider else player.track_provider

        if track_provider == "yt" and "playlist" in query:
            provider = "ytpl"

        provider: Provider = (
            track_providers.get(provider)
            if provider
            else track_providers.get(player.track_provider)
        )

        nodes = self.get_nodes()
        tracks = list()

        for node in nodes:
            try:
                with async_timeout.timeout(20):
                    tracks = await provider.search(query, node=node)
                    break
            except asyncio.TimeoutError:
                self.bot.dispatch("dismusic_node_fail", node)
                wavelink.NodePool._nodes.pop(node.identifier)
                continue
            except (LavalinkException, LoadTrackError):
                continue

        if not tracks:
            return await msg.edit("❌ No song/track found with given query.")

        if isinstance(tracks, YouTubePlaylist):
            tracks = tracks.tracks
            for track in tracks:
                await player.queue.put(track)

            await msg.edit(content=f"✅ Added `{len(tracks)}` songs to queue. ")
        else:
            track = tracks[0]

            await msg.edit(content=f"✅ Added `{track.title}` to queue. ")
            await player.queue.put(track)

        if not player.is_playing():
            await player.do_next()

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        spotify_credential = getattr(
            self.bot, "spotify_credentials", {"client_id": "", "client_secret": ""}
        )

        for config in self.bot.lavalink_nodes:
            try:
                node: wavelink.Node = await wavelink.NodePool.create_node(
                    bot=self.bot,
                    **config,
                    spotify_client=spotify.SpotifyClient(**spotify_credential),
                )
                print(f"[dismusic] INFO - Created node: {node.identifier}")
            except Exception:
                print(
                    f"[dismusic] ERROR - Failed to create node {config['host']}:{config['port']}"
                )


    @commands.command(aliases=["j", "connect"])
    @voice_connected()
    async def join(self, ctx: commands.Context):
        """Connect the player"""
        if ctx.voice_client:
            return

        msg = await ctx.send(f"✅ Connecting to **`{ctx.author.voice.channel}`**")

        try:
            player: DisPlayer = await ctx.author.voice.channel.connect(cls=DisPlayer)
            self.bot.dispatch("dismusic_player_connect", player)
        except (asyncio.TimeoutError, ClientException):
            return await msg.edit(content="❌ Failed to connect to voice channel.")

        player.bound_channel = ctx.channel
        player.bot = self.bot

        await msg.edit(content=f"Connected to **`{player.channel.name}`**")

    @commands.group(aliases=["p"], invoke_without_command=True)
    @voice_connected()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play or add song to queue (Defaults to YouTube)"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query)

    @commands.command(aliases=["v"])
    @voice_channel_player()
    async def volume(self, ctx: commands.Context, vol: int):
        """Set volume"""
        player: DisPlayer = ctx.voice_client

        if vol < 0:
            return await ctx.send("❌Volume can't be less than 0")

        if vol > 100:
            return await ctx.send("❌ Volume can't greater than 100")

        await player.set_volume(vol)
        await ctx.send(f":loud_sound: Volume set to {vol}")

    @commands.command(aliases=["disconnect", "dc", "leave", "st"])
    @voice_channel_player()
    async def stop(self, ctx: commands.Context):
        """Stop the player"""
        player: DisPlayer = ctx.voice_client

        await player.destroy()
        await ctx.send(":stop_button: Stopped the bot")
        self.bot.dispatch("dismusic_player_stop", player)

    @commands.command(aliases=["pa"])
    @voice_channel_player()
    async def pause(self, ctx: commands.Context):
        """Pause the player"""
        player: DisPlayer = ctx.voice_client

        if player.is_playing():
            if player.is_paused():
                return await ctx.send("❌ Bot is already paused.")

            await player.set_pause(pause=True)
            self.bot.dispatch("dismusic_player_pause", player)
            return await ctx.send(":pause_button: Paused")

        await ctx.send("❌ Bot is not playing anything.")

    @commands.command()
    @voice_channel_player()
    async def resume(self, ctx: commands.Context):
        """Resume the player"""
        player: DisPlayer = ctx.voice_client

        if player.is_playing():
            if not player.is_paused():
                return await ctx.send("❌ Player is already playing.")

            await player.set_pause(pause=False)
            self.bot.dispatch("dismusic_player_resume", player)
            return await ctx.send(":musical_note: Resumed")

        await ctx.send("❌ Player is not playing anything.")

    @commands.command(aliases=["s"])
    @voice_channel_player()
    async def skip(self, ctx: commands.Context):
        """Skip to next song in the queue."""
        player: DisPlayer = ctx.voice_client

        if player.loop == "CURRENT":
            player.loop = "NONE"

        await player.stop()

        self.bot.dispatch("dismusic_track_skip", player)
        await ctx.send(":track_next: Skipped")

    @commands.command(alises=["l"])
    @voice_channel_player()
    async def loop(self, ctx: commands.Context, loop_type: str = None):
        """Set loop to `NONE`, `CURRENT` or `PLAYLIST`"""
        player: DisPlayer = ctx.voice_client

        result = await player.set_loop(loop_type)
        await ctx.send(f"Loop has been set to {result} :repeat: ")

    @commands.command(aliases=["q"])
    @voice_channel_player()
    async def queue(self, ctx: commands.Context):
        """Player queue"""
        player: DisPlayer = ctx.voice_client

        if len(player.queue._queue) < 1:
            return await ctx.send("❌ Nothing is in the queue.")

        paginator = Paginator(ctx, player)
        await paginator.start()

    @commands.command(aliases=["np"])
    @voice_channel_player()
    async def nowplaying(self, ctx: commands.Context):
        """Currently playing song information"""
        player: DisPlayer = ctx.voice_client
        await player.invoke_player(ctx)
