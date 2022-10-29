from discord.ext import commands

from .errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected


def voice_connected():
    def predicate(ctx: commands.Context):
        if not ctx.author.voice:
            raise NotConnectedToVoice("❌ You have to be in a voice channel to do this")

        return True

    return commands.check(predicate)


def voice_channel_player():
    def predicate(ctx: commands.Context):
        if not ctx.author.voice:
            raise NotConnectedToVoice("❌ You have to be in a voice channel to do this")

        if not ctx.voice_client:
            raise PlayerNotConnected("❌ I am not connected to any voice channel.")

        if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            raise MustBeSameChannel(
                "❌ You must be in the same voice channel as the bot."
            )

        return True

    return commands.check(predicate)
