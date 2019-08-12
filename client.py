import os

from dotenv import find_dotenv, load_dotenv
from slackclient import SlackClient

load_dotenv(find_dotenv())

bot_token = os.getenv("BOT_TOKEN")
access_token = os.getenv("ACCESS_TOKEN")

bot_client = SlackClient(bot_token)
oauth_access_client = SlackClient(access_token)
