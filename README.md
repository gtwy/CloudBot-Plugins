# CloudBot-Plugins
James' plugins for [snoonetIRC's fork of CloudBot](https://github.com/snoonetIRC/CloudBot) (gonzobot branch.)

Plugin | Status | Description | Prerequisites
-------|--------|-------------|--------------
follow twitch|Stable|Follow specified channels & announce when they go live on IRC|[python-twitch-client](https://github.com/tsifrer/python-twitch-client)
follow twitter|Stable|Follow specified accounts & echo their tweets on IRC|[python-twitter](https://github.com/bear/python-twitter)
next launch|Devel|Responds with next rocket launch|[launchlibrary](https://pypi.org/project/python-launch-library/)
reddit news|Stable|Follows specified subreddits & echo when top post changes on IRC|[PRAW](https://praw.readthedocs.io)

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
