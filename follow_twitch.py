#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches Twitch channels & posts when they go live to IRC
#
#   Requirements:
#      * python-twitch-client    https://github.com/tsifrer/python-twitch-client


from cloudbot import hook
from twitch import TwitchClient

@hook.on_start()
def load_api(bot):
    global twitch_api

    # You need to have valid api keys in config.json. Client secret should contain "oauth:"
    twitch_client_id = bot.config.get("api_keys", {}).get("twitch_client_id", None)
    twitch_client_secret = bot.config.get("api_keys", {}).get("twitch_client_secret", None)

    if not all((twitch_client_id, twitch_client_secret)):
        twitch_api = None
        return
    else:
        twitch_api = TwitchClient(twitch_client_id, twitch_client_secret)

@hook.periodic(1*30)
def follow_twitter(bot, async, db):
    if twitch_api is None:
        print ("This command requires a Twitch API key.")
    else:
        # Change twitch channel names (Up to 25)
        twitch_channels = ['pcJIM', 'thederek412', 'toshibatoast', 'javagoogles', 'infaroot']
        # Change IRC network and channel name to match your server
        network = 'blindfish'
        channel = '#fish'
        # Stops plugin from crashing when IRC network is offline
        if network in bot.connections:
            conn = bot.connections[network]
            if conn.ready:
                live_now = []
                # Does the twitch id cache and live cache exist?
                if 'twitch_ids' not in globals():
                    global twitch_ids
                    global live_ids
                    twitch_ids = []
                    live_ids = []
                # Is the twitch cache current?
                if len(twitch_ids) != len(twitch_channels):
                    # Update cache
                    twitch_ids = []
                    for twitch_user in twitch_api.users.translate_usernames_to_ids(twitch_channels):
                        twitch_ids.append(twitch_user.id)
                # Download a list of everyone who is live
                for stream in twitch_api.streams.get_live_streams(','.join(twitch_ids)):
                    live_now.append(stream.channel.id)
                    if stream.channel.id not in live_ids:
                        live_ids.append(stream.channel.id)
                        # Post to channel that someone new has gone live
                        out = u'[Twitch] {} is live: [{} at {}p] {} ({})'.format(stream.channel.display_name, stream.channel.game, stream.video_height, stream.channel.status, stream.channel.url)
                        conn.message(channel, out)
                # Remove them from the live cache if they are no longer live
                for live_id in live_ids:
                    if live_id not in live_now:
                        live_ids.remove(live_id)
