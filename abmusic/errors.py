from discord.ext.commands.errors import CheckFailure


class NotConnectedToVoice(CheckFailure):
    """❌ You have to be in a voice channel to do this"""

    pass


class PlayerNotConnected(CheckFailure):
    """❌ I am not connected to any voice channel."""

    pass


class MustBeSameChannel(CheckFailure):
    """❌ You must be in the same voice channel as the bot."""

    pass


class NothingIsPlaying(CheckFailure):
    """❌ There is nothing playing"""

    pass


class NotEnoughSong(CheckFailure):
    """❌ Not enough songs in queue"""

    pass


class InvalidLoopMode(CheckFailure):
    """❌ Invalid loop mode"""

    pass
