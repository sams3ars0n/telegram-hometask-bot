# Telegram Hometask Group Bot

## Description

It's open-source project written in Python using Pyrogram library.

It's used to help students to easily write down their homework and then see it in a form pleasant to the eye.

You must use it only in a Telegram group.

## Usage

Create a bot with [Bot Father](https://t.me/BotFather). It will send you your bot's token. Fill it in the `bot_token` field in `config.ini` file (or set an environment vatiable BOT_TOKEN).

Go to https://my.telegram.org/apps, log in and get `api_id` and `api_hash` of your account. Fill it in the `api_id` and `api_hash` fields in `config.ini` file (or set environment vatiables API_ID and API_HASH).

Go to [userinfobot](https://t.me/userinfobot) and get id of your account. Fill it in the `OWNER_ID` field in `config.ini` file (or set an environment vatiable OWNER_ID).

Make sure you have installed Python 3.6+ with pip. Then go to terminal and run `pip3 install -r requirements.txt` to install all requirements for bot.

Run `python3 main.py`. Go to the bot you created in Telegram and write `/help` command. You will see all commands available for you as owner. Write `/help` command in a group to see commands available in group.

Don't forget to uncomment all lines in `config.ini` if you are using it for setting bot variables.

## Docker

For those who use Docker to run the bot, you already have Dockerfile in the repository.
For bot configuration you can use either `config.ini` or environment variables.

If you don't wanna use `config.ini` you can set environment variables: go to Dockerfile, uncomment lines with those variables and fill the variables in. 
Also, you can pass them when running a container with `-e` option.

Then build an image:

`docker build -t telegram-hometask-bot-image .`

And run a container:

`docker run -d --name telegram-hometask-bot telegram-hometask-bot-image`

You can also use a Docker Volume or mount a directory on host to the path where database is being saved (/usr/src/app/database) to docker container with `-v` option.