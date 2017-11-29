# CloudBot-Plugins
James' plugins for CloudBot. You must be running the [snoonetIRC fork of CloudBot](https://github.com/snoonetIRC/CloudBot) to run these plugins.

Plugin | Status | Description | Prerequisites
-------|--------|-------------|--------------
reddit_news|Stable|Follows specified subreddits & echo when top post changes on IRC|[PRAW](https://praw.readthedocs.io)
follow_twitter|Stable|Follow specified accounts & echo their tweets on IRC|[python-twitter](https://github.com/bear/python-twitter)
follow_twitch|Devel|Follow specified channels & announce when they go live on IRC|[python-twitch-client](https://github.com/tsifrer/python-twitch-client)

## How to use
Install all necessary prerequisites. Link or copy these .py files into CloudBot's plugins directory. Vim each .py file for configuration options. You must also add new API keys to CloudBot's config.json file.

## Support
I'll do the best I can to answer questions/issues. I've been on IRC for 15 years. I'll maintain these scripts for years.
