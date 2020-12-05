# Minecraft Server Bot

Minecraft Server Bot is a python telegram bot that allow you to control your minecraft server remotely

<p align=center width=50%>
    <img src = https://i.imgur.com/MHvDRtN.jpeg/ width=70%>
    <img src = https://i.imgur.com/UvY6yQQ.jpeg/ width=70%>
</p>

## Set Up

This project use python3. First of all install all the dependencies in the requirements file using the command: ` pip3 install requirements`,
then rename the `config-sample.json` file in `config.json`.
In the config.json file configure the fields as:

-   **whitelist** : list of telegram username that are allowed to use the bot
-   **server-directory** : directory of the minecraft server
-   **jar-name** : name of the minecraft server jar
-   **bot-token** : token of the telegram bot
-   **args** : list of java arguments (e.g. -Xmx2G, -Xms2G)

Now you are ready to start the bot with the command `python3 bot.py`

## Commands

-   **start** or **s** : start the minecraft server
-   **stop** : stop the minecraft server
-   **output** or **o** : bot reply with the stdout of the server
-   **command** or **c** : take as argument a minecraft command and execute it (e.g /command say hello world)
-   **reload_config** : reload the config.json file (not restart the server)
-   **ping** : bot reply with pong message
