# CloudBot-Plugins
James' plugins for [snoonetIRC's fork of CloudBot](https://github.com/snoonetIRC/CloudBot) (gonzobot branch.)

Plugin | Status | Description | Prerequisites
-------|--------|-------------|--------------
follow twitch|Stable|Follow specified channels & announce when they go live on IRC|[python-twitch-client](https://github.com/tsifrer/python-twitch-client)
follow twitter|Stable|Follow specified accounts & echo their tweets on IRC|[python-twitter](https://github.com/bear/python-twitter)
next launch|Devel|Responds with next rocket launch|[launchlibrary](https://pypi.org/project/python-launch-library/)
reddit news|Stable|Follows specified subreddits & echo when top post changes on IRC|[PRAW](https://praw.readthedocs.io)

## About
I am really impressed with the MaxQ bot in #SpaceX on EsperNet. The bot provides a feed to the channel with 1). tweets from people related to space, such as Elon Musk and NASA, 2). when the top post on reddit's /r/spacex changes, 3). information about the next rocket launch.

After spending some time there, I decided I wanted to recreate MaxQ's functionality for another channel on Freenode. When I first inquired about the MaxQ bot, in 2017, the source code was not public. So, I started working on my own bot that would behave similarly.

My first attempt was a bot from scratch. While I did manage to make some progress, it was too difficult and clunky for other people to use. It soon became obvious that writing plugins for an existing bot platform would be superior to writing my own from scratch.

My initial belief was that periodic hooks were the key to emulating the MaxQ bot. I tried to find a popular bot ecosystem that supported periodic hooks. I tested a variety of bots, but none of the projects currently maintained had periodic hook support, including the original CloudBot project. After nearly giving up, I found a fork of [CloudBot by snoonetIRC](https://github.com/snoonetIRC/CloudBot). It is frequently updated, maintained, and best of all, written with periodic hook support.

Today, the [MaxQ bot's source code](https://github.com/jclishman/maxq-irc-bot) is public and available for you to use. It's a from-scratch bot that lacks the plug-and-play usability of CloudBot. No source code from that project has been used on this project. (In fact, I only looked through his code for the first time quite recently.)

Because I want to do things above and beyond the limited features of MaxQ, including utilize other CloudBot plugins, my plugin project will continue to be updated and maintained. Thanks for checking it out!

## How to use
Install all necessary prerequisites linked in the table above.

Copy plugin .py files into CloudBot's plugins directory.

Edit CloudBot's config.json file. Add read-only API keys for the services you intend to use.

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

Future versions will use a different format for server and channel in config.json.

## Support
I'll do the best I can to answer questions/issues. Feel free to contact me here or on Twitter [@Gtwy](https://twitter.com/Gtwy).
