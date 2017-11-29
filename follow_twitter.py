#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches Twitter feeds & posts the tweets to IRC
#
#   Requirements:
#      * python-twitter API      https://github.com/bear/python-twitter


from datetime import datetime
import time
import asyncio
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

@hook.on_start()
def load_api(bot):
    global twitter_api

    # You need to have valid api keys in config.json
    consumer_key = bot.config.get("api_keys", {}).get("twitter_consumer_key", None)
    consumer_secret = bot.config.get("api_keys", {}).get("twitter_consumer_secret", None)
    oauth_token = bot.config.get("api_keys", {}).get("twitter_access_token", None)
    oauth_secret = bot.config.get("api_keys", {}).get("twitter_access_secret", None)

    if not all((consumer_key, consumer_secret, oauth_token, oauth_secret)):
        twitter_api = None
        return
    else:
        # NOTE: This is a different API than what twitter.py uses
        twitter_api = twitter.Api(consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=oauth_token,
                access_token_secret=oauth_secret
        )


@asyncio.coroutine
def add_entry(async, db, twitterid, dateadded):
    query = table.insert().values(
            twitterid=twitterid,
            dateadded=dateadded
    )
    yield from async(db.execute, query)
    yield from async(db.commit)

@asyncio.coroutine
@hook.on_start()
def load_cache(async, db):
    global follow_twitter_cache
    follow_twitter_cache = []

    for twitterid, dateadded in (yield from async(_load_cache_db, db)):
        follow_twitter_cache.append((twitterid, dateadded))

def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row["twitterid"], row["dateadded"]) for row in query]

@asyncio.coroutine
@hook.periodic(1*60) # Twitter only allows 15 API calls in 15 minutes. Each user counts as an API call. Keep that in mind.
def follow_twitter(bot, async, db):
    dateadded = datetime.now()
    if twitter_api is None:
        print ("This command requires a Twitter API key.")
    else:
        # Change twitter users, network and channel to match your desired settings
        # (Want multi channel or multi network? Code it and send a pull request!)
        twitter_users = ['Gtwy', 'dkalinosky', 'toshibatoast', 'borlandts', 'infaroot', 'RomanHeisenberg']
        network = 'blindfish'
        channel = '#fish'
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
                        text = tweets[tweet_i].text.replace('\n',' ').replace('  ',' ').rstrip()
                        url = u'https://twitter.com/{}/status/{}'.format(twitter_user,tweets[tweet_i].id_str)
                        out = u'{}{}  ({})'.format(intro,text,url)
                        # Send the message to IRC
                        conn.message(channel, out)
                        # Record that we posted this tweet
                        yield from add_entry(async, db, tweets[tweet_i].id_str, dateadded)
                        yield from load_cache(async, db)
                
		# Iterate to next user
                if twitter_u == len(twitter_users)-1:
                	twitter_u = 0
                else:
                	twitter_u += 1 
