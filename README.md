# CloudBot-Plugins
James' plugins for [snoonetIRC's fork of CloudBot](https://github.com/snoonetIRC/CloudBot) (gonzobot branch.)

Plugin | Status | Description | Prerequisites
-------|--------|-------------|--------------
follow twitch|Stable|Follow specified channels & announce when they go live on IRC|[python-twitch-client](https://github.com/tsifrer/python-twitch-client)
follow twitter|Stable|Follow specified accounts & echo their tweets on IRC|[python-twitter](https://github.com/bear/python-twitter)
next launch|Devel|Responds with next rocket launch|[launchlibrary](https://pypi.org/project/python-launch-library/)
reddit news|Stable|Follows specified subreddits & echo when top post changes on IRC|[PRAW](https://praw.readthedocs.io)

## About
My cloudbot plugins will enable your bot to follow twitter users, twitch users, and reddit subreddits of your choosing, echoing new posts to your IRC channel in real time. It also is a useful tool for tracking future rocket launches.

This project was inspired by the MaxQ bot in #SpaceX on EsperNet. In 2017, I decided I wanted to recreate MaxQ's functionality for another channel on Freenode. When I first inquired about the MaxQ bot, its source code was not yet public. So, I started working on my own bot that would behave similarly.

My first attempt was a bot from scratch. While I did manage to make some progress, it was too difficult and clunky for other people to use. It soon became obvious that writing plugins for an existing bot platform would be superior to writing my own from scratch.

My initial belief was that periodic hooks were the key to emulating the MaxQ bot. I tried to find a popular bot ecosystem that supported periodic hooks. I tested a variety of bots, but none of the projects currently maintained had periodic hook support, including the original CloudBot project. After nearly giving up, I found a fork of [CloudBot by snoonetIRC](https://github.com/snoonetIRC/CloudBot). It is frequently updated, maintained, and best of all, written with periodic hook support.

Today, the [MaxQ bot's source code](https://github.com/jclishman/maxq-irc-bot) is public and available for you to use. It's a from-scratch bot that lacks the plug-and-play usability of CloudBot. No source code from that project has been used on this project. (In fact, I only looked through his code for the first time quite recently.)

Because I want to do things above and beyond the limited features of MaxQ, including utilize other CloudBot plugins, my plugin project will continue to be updated and maintained. Thanks for taking a look!

## Example Output
An example of what you can expect on your IRC channel (alt-l is the bot.)

```
00:34:21 alt-l | [Twitter] @Gtwy wrote: Does anybody seriously think the new 3-camera iPhone is
               | aesthetically pleasing?  (https://twitter.com/Gtwy/status/1175266879004237824)
13:09:45 alt-l | [Reddit] Trending on /r/netsec: GitHub - secrary/Andromeda: Andromeda - Interactive
               | Reverse Engineering Tool for Android Applications (https://redd.it/d7t41m)
19:14:28    wx | %nl
19:14:29 alt-l | H-IIB 304 | Kounotori 8 (HTV-8) - Osaki Y LP2, Tanegashima, Japan -
               | https://youtu.be/EqGcvxZRIzI - NET 2019-09-24 16:05:05+00:00 - T-16:50:36.011158
```

## How to use
Install all necessary prerequisites linked in the table above.

Copy plugin .py files into CloudBot's plugins directory.

Edit CloudBot's config.json file. Add read-only API keys for the services you intend to use.

```
    "api_keys": {
        "reddit_news_client_id": "",
        "reddit_news_client_secret": "",
        "twitch_client_id": "",
        "twitch_client_secret": "",
        "twitter_consumer_key": "",
        "twitter_consumer_secret": "",
        "twitter_access_token": "",
        "twitter_access_secret": ""
    },
```

At the bottom of your config, add a section named "james-plugins." Don't forget to add a comma after closing the logging block. It should look something like this. Adjust settings accordingly.

```
    },
    "james-plugins": {
        "reddit_news_subreddits": [
                "netsec",
		"ReverseEngineering",
		"malware",
		"blackhat"
        ],
        "reddit_news_output_server": "freenode",
        "reddit_news_output_channel":"#lowtech-dev"
        "follow_twitter_accounts": [
                "Gtwy",
                "hiredbeard",
                "fauxicles"
        ],
        "follow_twitter_output_server": "freenode",
        "follow_twitter_output_channel": "#lowtech-dev",
	"follow_twitch_channels": [
		"pcJIM",
		"javagoogles"
	],
	"follow_twitch_output_server": "freenode",
	"follow_twitch_output_channel": "#lowtech-dev"
    }
}
```

## Considerations
Service | Minimum Hook Interval | Maximum Hook Interval
--------|-----------------------|----------------------
reddit|60|Unlimited
twitter|60|Unlimited
twitch|30|Unlimited

Interval durations outside these ranges will exceed the API limits of each service resulting in your API key being rate limited and eventually blacklisted.

Only one twitter account is polled at each interval. Hence, the more people you follow, the more delayed their tweets will be.

Future versions will use a [different format for server and channel](https://github.com/gtwy/CloudBot-Plugins/issues/9) in config.json.

## Support
I'll do the best I can to answer questions/issues. Feel free to contact me here or on Twitter [@Gtwy](https://twitter.com/Gtwy).
