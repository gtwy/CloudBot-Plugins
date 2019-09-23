#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches Twitter feeds & posts the tweets to IRC
#
#   Requirements:
#      * python-twitter API      https://github.com/bear/python-twitter


from datetime import datetime
import time
import html
from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint
from cloudbot import hook
from cloudbot.util import database
import twitter

table = Table('follow_twitter',
        database.metadata,
        Column('twitterid', String(100)),
        Column('dateadded', DateTime),
        PrimaryKeyConstraint('twitterid','dateadded')
)

async def add_entry(async_call, db, twitterid, dateadded):
    query = table.insert().values(
            twitterid=twitterid,
            dateadded=dateadded
    )
    await async_call(db.execute, query)
    await async_call(db.commit)

@hook.on_start()
async def load_api(bot):
    global twitter_api

    # Get API keys from config.json
    consumer_key = bot.config.get('api_keys', {}).get('twitter_consumer_key', None)
    consumer_secret = bot.config.get('api_keys', {}).get('twitter_consumer_secret', None)
    oauth_token = bot.config.get('api_keys', {}).get('twitter_access_token', None)
    oauth_secret = bot.config.get('api_keys', {}).get('twitter_access_secret', None)

    if not all((consumer_key, consumer_secret, oauth_token, oauth_secret)):
        twitter_api = None
        return
    else:
        # NOTE: This is a different API than that used by CloudBot's twitter.py
        twitter_api = twitter.Api(consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=oauth_token,
                access_token_secret=oauth_secret,
                tweet_mode='extended'
        )

@hook.on_start()
async def load_cache(async_call, db):
    global follow_twitter_cache
    follow_twitter_cache = []

    for twitterid, dateadded in (await async_call(_load_cache_db, db)):
        follow_twitter_cache.append((twitterid, dateadded))

def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row['twitterid'], row['dateadded']) for row in query]

@hook.periodic(60) # Minimum is 60
async def follow_twitter(bot, async_call, db):
    dateadded = datetime.now()
    if twitter_api is None:
        print ('This command requires a Twitter API key.')
    else:
        twitter_users = bot.config.get('james-plugins', {}).get('follow_twitter_accounts', None)
        if not twitter_users:
            twitter_users = ['Gtwy', 'hiredbeard', 'fauxicles']
        network = bot.config.get('james-plugins', {}).get('follow_twitter_output_server', None)
        if not network:
            network = 'freenode'
        channel = bot.config.get('james-plugins', {}).get('follow_twitter_output_channel', None)
        if not channel:
            channel = '#lowtech-dev'
        # Stops plugin from crashing when network is offline
        if network in bot.connections:
            conn = bot.connections[network]
            if conn.ready:
		# Pull tweets from just one user per run to satisfy Twitter's draconian rate limit.
                if 'twitter_u' not in globals():
                    global twitter_u
                    twitter_u = 0
                twitter_user = twitter_users[twitter_u]
                intro = u'[Twitter] @{} wrote: '.format(twitter_user)
                tweets = twitter_api.GetUserTimeline(screen_name=twitter_user,
                                                        count=5, # post up to this many tweets per user
                                                        include_rts=False,
                                                        trim_user=True,
                                                        exclude_replies=True
                )
                # Iterates timeline backwards so tweets post in chronological order
                for tweet_i in range(len(tweets)-1,-1,-1):
                    # Check if tweet has been posted before
                    submitted = False
                    for result in follow_twitter_cache:
                        cacheid, cachedate = result
                        if tweets[tweet_i].id_str == cacheid:
                            submitted = True
                    if not submitted:
                        # Build the IRC message
                        text = html.unescape(tweets[tweet_i].full_text.replace('\n',' ').replace('  ',' ').rstrip())
                        url = u'https://twitter.com/{}/status/{}'.format(twitter_user,tweets[tweet_i].id_str)
                        out = u'{}{}  ({})'.format(intro,text,url)
                        # Send the message to IRC
                        conn.message(channel, out)
                        # Record that we posted this tweet
                        await add_entry(async_call, db, tweets[tweet_i].id_str, dateadded)
                        await load_cache(async_call, db)

		# Iterate to next user
                if twitter_u == len(twitter_users)-1:
                	twitter_u = 0
                else:
                	twitter_u += 1
