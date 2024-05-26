# What does this bot do?

This bot joins guilds and takes all of their forum channels and converts them into static html. What you do with these html pages is up to you at this point.

# Running the bot

1. Clone the repo and install dependencies:

```shell
git clone git@github.com:nwpulverizer/discord_to_html.git
pip install -r requirements.txt
```

2. Create a bot account and get your bot token. See [discord.py docs](https://discordpy.readthedocs.io/en/stable/discord.html) for details.

3. Write your bot token into a .env file in the src/ directory in the repo under the variable BOT_KEY.

4. Invite the bot to your server. Refer to the documentation linked above. It will need the bot scope and Read Message History and Read Messages/View Channels permissions.

5. Run the bot:

```shell
python main.py -d ../public/ -t ../templates
```

6. Once the bot connects, it will generate html files for each server it has joined. This will be output into the -d directory supplied under public-{guildid}/. A simple server is supplied in the base directory of the repo if you would like to view your generated files you can do so with:

```shell
python server.py -d ./public/public-{guild_id}/
```

# Why

The point of this bot is to allow the content of help forums to be searchable on the internet. Discord is great for quick responses and fostering community,
but there is no way to search all the help being given behind discord's walls. This project aims to fix this.

# Roadmap 
 - [ ] Add reaction count to posts
 -  [ ] Show image attatchments 
-  [ ] Add sort by date or reaction count
-  [ ] Improve styling for posts  
