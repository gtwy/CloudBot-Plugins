#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches Twitch channels & posts when they go live to IRC
#
#   Requirements:
#      * python-twitch-client    https://github.com/tsifrer/python-twitch-client


from cloudbot import hook
from twitch import TwitchClient

@hook.on_start()
async def load_api(bot):
    global twitch_api

    # Get API keys from config.json
    twitch_client_id = bot.config.get('api_keys', {}).get('twitch_client_id', None)
    twitch_client_secret = bot.config.get('api_keys', {}).get('twitch_client_secret', None)

    if 'oath:' not in twitch_client_secret:
        twitch_client_secret = 'oath:' + twitch_client_secret

    if not all((twitch_client_id, twitch_client_secret)):
        twitch_api = None
        return
    else:
        twitch_api = TwitchClient(twitch_client_id, twitch_client_secret)

@hook.periodic(1*30) # Minimum is 30
async def follow_twitch(bot, async_call, db):
    if twitch_api is None:
        print ('This command requires a Twitch API key.')
    else:
        twitch_channels = bot.config.get('james-plugins', {}).get('follow_twitch_channels', None)
        if not twitch_channels:
            twitch_channels = ['pcJIM', 'javagoogles']
        network = bot.config.get('james-plugins', {}).get('follow_twitch_output_server', None)
        if not network:
            network = 'freenode'
        channel = bot.config.get('james-plugins', {}).get('follow_twitch_output_channel', None)
        if not channel:
            channel = '#lowtech-dev'
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
                        out = u'[Twitch] {} is live: [{}] {} ({})'.format(stream.channel.display_name, stream.channel.game, stream.channel.status, stream.channel.url)
                        conn.message(channel, out)
                # Remove them from the live cache if they are no longer live
                for live_id in live_ids:
                    if live_id not in live_now:
                        live_ids.remove(live_id)
