from slackclient import SlackClient


def create_client(bot_token, user_token):
    bot_client = SlackClient(bot_token)
    user_client = SlackClient(user_token)
    return bot_client, user_client
