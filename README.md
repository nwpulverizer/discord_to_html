# What does this bot do?

This bot joins guilds and, using slash commands, takes their forum channels and converts them into static HTML. This allows the content of Discord forums to be exported and viewed as a static website.

# Running the bot

1.  **Clone the repo and install dependencies:**
    ```shell
    git clone https://github.com/nwpulverizer/discord_to_html.git # Or your fork's URL
    cd discord_to_html
    pip install -r requirements.txt
    ```

2.  **Create a bot account and get your bot token.** See the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/discord.html) for details on creating a bot and obtaining a token.

3.  **Configure the bot token:**
    Create a `.env` file in the `src/` directory (alongside `main.py`). Add your bot token to this file like so:
    ```env
    BOT_KEY=YOUR_ACTUAL_BOT_TOKEN_HERE
    ```

4.  **Invite the bot to your server.** Your bot will need the `bot` scope. For permissions, it requires:
    *   `Read Messages/View Channels`: To see forum channels and their content.
    *   `Read Message History`: To fetch all messages in forum threads.
    *   `Application Commands`: To register and use slash commands.
    *   (Implicitly) `Send Messages`: To respond to commands.
    *   It's also recommended the bot has permissions to view archived threads if you want to include them.

5.  **Run the bot:**
    Navigate to the `src/` directory in your terminal and run:
    ```shell
    python main.py -d ../public/ -t ../templates
    ```
    *   `-d ../public/`: Specifies the output directory for the generated HTML files (relative to `src/`). Files will be placed in `public/public-{guild_id}/`.
    *   `-t ../templates/`: Specifies the directory containing the HTML templates (relative to `src/`).

6.  **Using the Bot:**
    Once the bot is running and connected to your server, users with Administrator permissions can use slash commands to archive forums. The bot no longer automatically processes all forums on startup.

# Commands

The following slash commands are available and require **Administrator** permissions:

*   **`/archive_all_forums`**
    *   **Description:** Archives all forum channels in the current server. It will create static HTML files for each forum and its posts.
    *   **Usage:** Simply type `/archive_all_forums` in any channel the bot can see.

*   **`/archive_forum [forum_channel]`**
    *   **Description:** Archives a specific forum channel in the current server.
    *   **Arguments:**
        *   `forum_channel` (Required): The forum channel you wish to archive. Discord will provide a selection list.
    *   **Usage:** Type `/archive_forum` and select the desired forum channel from the options.

Output files will be generated in the directory specified by the `-d` argument when starting the bot (e.g., `public/public-{guild_id}/`).

# Viewing Generated Files

A simple Python HTTP server is supplied in the base directory of the repo. If you would like to view your generated files locally, you can navigate to the root of the repository and run:
```shell
python server.py -d ./public/public-{guild_id}/
```
Replace `{guild_id}` with the actual ID of the guild whose files you want to view. Then open your browser to `http://localhost:8000`.

# Why

The point of this bot is to allow the content of help forums to be searchable on the internet. Discord is great for quick responses and fostering community, but there is no way to search all the help being given behind Discord's walls. This project aims to fix this.

# Roadmap

In no particular order, here are some things that I should improve.

- [x] Add reaction count to posts (Completed in previous work)
- [x] Show image attachments (Completed in previous work)
- [ ] Add sort by date or reaction count
- [x] Improve styling for posts (Completed in previous work)
- [ ] Add ability to update forum instead of just fully rewriting everytime.
- [x] Instead of running based on whenever the bot is turned on, create bot commands (Completed)
