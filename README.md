# dismusic

Music cog for discord bots. Supports YouTube, YoutubeMusic, SoundCloud and Spotify.

# Installation

```sh
pip install git+https://github.com/RobbyV2/abmusic
```

# Usage

```python
from discord.ext import commands

bot = commands.Bot(command_prefix='.')

bot.lavalink_nodes = [
    {"host": "losingtime.dpaste.org", "port": 2124, "password": "SleepingOnTrains"},
    # Can have multiple nodes here
]


bot.load_extension('dismusic')
bot.run('TOKEN')
```

# Commands

**join** - `Connect to vc` \
**stop** - `Disconnect from vc`

**play** - `Play a song or playlist` \
**pause** - `Pause player` \
**resume** - `Resume player`

**nowplaying** - `Now playing` \
**queue** - `See queue` \
**volume** - `Set volume` \
**loop** - `Loop song/playlist`

> Filter commands coming soon.

# Events

Events that this library dispatches

```py
on_dismusic_player_connect(player):
    # When player connects to a voice channel

on_dismusic_player_stop(player):
    # When player gets disconnected

on_dismusic_track_start(player, track):
    # When a song start playing

on_dismusic_track_end(player, track):
    # When a song finished

on_dismusic_track_exception(player, track):
    # When song stops due to any exception

on_dismusic_track_stuck(player, track):
    # When a song gets stuck

on_dismusic_player_pause(player):
    # When player gets paused

on_dismusic_player_resume(player):
    # When player gets resumed

on_dismusic_player_seek(player, previous_position, current_position):
    # When player seeks
```

# Lavalink Configs
Find configs here [https://lavalink.darrennathanael.com/](https://lavalink.darrennathanael.com/)

[Join Discord](https://discord.gg/7SaE8v2) For any kind of help
