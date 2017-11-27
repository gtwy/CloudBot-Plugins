# This script watches the subreddits of your choosing.
# When a new post reaches #1 on its subreddit, the bot will link it here.
#
# (Before running script, please see comments below)
#
# Thanks to linuxdaemon for some help with @hook.periodic & conn.message
from cloudbot import hook
from cloudbot.util import database
import praw


@hook.on_start()
def load_api(bot):
    global red_api

    # Create these 4 api keys in config.json before running
    r_client_id = bot.config.get("api_keys", {}).get("reddit_news_client_id", None)
    r_client_secret = bot.config.get("api_keys", {}).get("reddit_news_client_secret", None)
    r_username = bot.config.get("api_keys", {}).get("reddit_news_username", None)
    r_password = bot.config.get("api_keys", {}).get("reddit_news_password", None)

    # Change if you want
    r_user_agent = "linux:sh.blindfi.bot:v0.0.1 (by /u/PCGamerJim)"

    if not all((r_client_id, r_client_secret, r_username, r_password)):
        red_api = None
        return
    else:
        red_api = praw.Reddit(client_id=r_client_id, client_secret=r_client_secret, user_agent=r_user_agent, username=r_username, password=r_password)

@hook.periodic(1*60)
def reddit_news(bot):
    if red_api is None:
        print ("This command requires a reddit API key.")
    else:
        # Edit the next 3 variables to your preference. Network and channel should reflect config.json
        subreddits = ['netsec', 'ReverseEngineering', 'rootkit', 'blackhat', 'ProgrammerHumor']
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
                                with open('reddit.txt', 'r') as searchfile:
                                    for line in searchfile:
                                        if submission.id in line:
                                            submitted = True
                                if not submitted and out == '':
                                    out = u'Trending on /r/{}: {} (https://redd.it/{})'.format(subreddit, submission.title, submission.id)
                                    with open('reddit.txt', 'a') as file:
                                        file.writelines(submission.id + '\n')
                if out != '':
                    conn.message(channel, out)
