#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   This script watches the Subreddits of your choosing.
#   When a new post reaches #1 on any given subreddit, the bot links to it
#
#   Requirements:
#      * PRAW Reddit API        https://praw.readthedocs.io

from datetime import datetime
import time
import asyncio
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

@hook.on_start()
def load_api(bot):
    global red_api
    
    # Create 4 new api keys in config.json to match those below this line
    r_client_id = bot.config.get("api_keys", {}).get("reddit_news_client_id", None)
    r_client_secret = bot.config.get("api_keys", {}).get("reddit_news_client_secret", None)
    
    # Change if you want. Reddit requires a "valid user agent" and prohibits "spoofing"
    r_user_agent = "linux:sh.blindfi.bot:v0.0.1 (by /u/PCGamerJim)"

    if not all((r_client_id, r_client_secret)):
        red_api = None
        return
    else:
        red_api = praw.Reddit(client_id=r_client_id, client_secret=r_client_secret, user_agent=r_user_agent) 

@asyncio.coroutine
def add_entry(async, db, redditid, subreddit, dateadded):
    query = table.insert().values(
            redditid=redditid,
            subreddit=subreddit,
            dateadded=dateadded
    )
    yield from async(db.execute, query)
    yield from async(db.commit)

@asyncio.coroutine
@hook.on_start()
def load_cache(async, db):
    global reddit_news_cache
    reddit_news_cache = []

    for redditid, subreddit, dateadded in (yield from async(_load_cache_db, db)):
        reddit_news_cache.append((redditid, subreddit, dateadded))

def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row["redditid"], row["subreddit"], row["dateadded"]) for row in query]

@asyncio.coroutine
@hook.periodic(1*60)
def reddit_news(bot, async, db):
    dateadded = datetime.now()
    if red_api is None:
        print ("This command requires a reddit API key.")
    else:
        # Change subreddits, network and channel to match your desired settings
        # (Want multi channel or multi network? Code it and send a pull request!)
        subreddits = ['netsec', 'ReverseEngineering', 'malware', 'blackhat', 'pwned']
        network = 'blindfish'
        channel = '#fish'
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
                                    yield from add_entry(async, db, submission.id, subreddit, dateadded)
                                    yield from load_cache(async, db)
                                    conn.message(channel, out)
