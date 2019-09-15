#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches the Subreddits of your choosing.
#   When a new post reaches #1 on any given subreddit, the bot links to it
#
#   Requirements:
#      * PRAW Reddit API        https://praw.readthedocs.io

from datetime import datetime
import time
from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint
from cloudbot import hook
from cloudbot.util import database
import praw

table = Table('reddit_news',
        database.metadata,
        Column('redditid', String(10)),
        Column('subreddit', String(20)),
        Column('dateadded', DateTime),
        PrimaryKeyConstraint('redditid','subreddit','dateadded')
)

async def add_entry(async_call, db, redditid, subreddit, dateadded):
    query = table.insert().values(
            redditid=redditid,
            subreddit=subreddit,
            dateadded=dateadded
    )
    await async_call(db.execute, query)
    await async_call(db.commit)

@hook.on_start()
async def load_api(bot):
    global red_api

    # Gets API keys from config.json
    r_client_id = bot.config.get('api_keys', {}).get('reddit_news_client_id', None)
    r_client_secret = bot.config.get('api_keys', {}).get('reddit_news_client_secret', None)

    # Change if you want. Reddit requires a "valid user agent" and prohibits "spoofing"
    r_user_agent = 'linux:sh.blindfi.bot:v0.0.1 (by /u/PCGamerJim)'

    # Get hook time from config.json
    reddit_news_hook_time = bot.config.get('james-plugins', {}).get('reddit_news_hook_time', None)
    if not reddit_news_hook_time:
        reddit_news_hook_time = 5*60

    # Does the API key exist?
    if not all((r_client_id, r_client_secret)):
        red_api = None
        return
    else:
        red_api = praw.Reddit(client_id=r_client_id, client_secret=r_client_secret, user_agent=r_user_agent)


@hook.on_start()
async def load_cache(async_call, db):
    global reddit_news_cache
    reddit_news_cache = []

    for redditid, subreddit, dateadded in (await async_call(_load_cache_db, db)):
        reddit_news_cache.append((redditid, subreddit, dateadded))

def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row['redditid'], row['subreddit'], row['dateadded']) for row in query]

@hook.periodic(2 * 60) # Minimum is 60
async def reddit_news(bot, async_call, db):
    dateadded = datetime.now()
    if red_api is None:
        print ('This command requires a reddit API key.')
    else:
        subreddits = bot.config.get('james-plugins', {}).get('reddit_news_subreddits', None)
        if not subreddits:
            subreddits = ['netsec', 'ReverseEngineering', 'malware', 'blackhat', 'pwned']
        network = bot.config.get('james-plugins', {}).get('reddit_news_output_server', None)
        if not network:
            network = 'freenode'
        channel = bot.config.get('james-plugins', {}).get('reddit_news_output_channel', None)
        if not channel:
            channel = '#lowtech-dev'
        if network in bot.connections:
            conn = bot.connections[network]
            if conn.ready:
                out = ''
                for subreddit in subreddits:
                    submitted = False
                    if out == '':
                        for submission in red_api.subreddit(subreddit).hot(limit=3):
                            if not submission.stickied:
                                for result in reddit_news_cache:
                                    cacheid, cachesub, cachedate = result
                                    if submission.id == cacheid :
                                        submitted = True
                                if not submitted and out == '':
                                    out = u'[Reddit] Trending on /r/{}: {} (https://redd.it/{})'.format(subreddit, submission.title, submission.id)
                                    await add_entry(async_call, db, submission.id, subreddit, dateadded)
                                    await load_cache(async_call, db)
                                    conn.message(channel, out)
