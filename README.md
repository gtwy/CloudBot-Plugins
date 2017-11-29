# CloudBot-Plugins
James' plugins for CloudBot.

## Prerequisites
* [CloudBot fork by snoonetIRC](https://github.com/snoonetIRC/CloudBot)
* [PRAW python library](https://praw.readthedocs.io)
* [Python Twitter library](https://github.com/bear/python-twitter)
* [Python Twitch Client library](https://github.com/tsifrer/python-twitch-client)

## What do these do?
I'll write a short wiki later with a better documentation of each file, but for now here's the gist of it.

Plugin | Status | Description | Prerequisites
-------|--------|-------------|--------------
reddit_news|Stable|Follows specified subreddits & echo when top post changes on IRC|PRAW
follow_twitter|Stable|Follow specified accounts & echo their tweets on IRC|python-twitter
follow_twitch|Devel|Follow specified channels & announce when they go live on IRC|python-twitch-client

## How to use
Link or copy these .py files into CloudBot's plugins directory. Vim each .py file for configuration options. With certain plugins, you must also add new API keys to CloudBot's config.json file.

## Support
I'll do the best I can to answer questions/issues. I've been on IRC for 15 years. I'll maintain these scripts for years, at least.
