import os
import re
from logging.config import dictConfig

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_api import FlaskAPI
from flask_pymongo import PyMongo
from slackclient import SlackClient
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from client import create_client
from constants import HELP_REGEX, LOGGING_CONFIG, REACTION_REGEX
from decorators import verify_request, verify_request_depr
from utils import (generate_user_response, get_message_permalink,
                   get_reaction_details, get_reactions, send_ephemeral_message)


load_dotenv(find_dotenv())

environment = os.getenv("ENV", "development")
is_debug = environment == "development"
SENTRY_DSN = os.getenv("SENTRY_DSN")

if (environment == "production"):
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()])

dictConfig(LOGGING_CONFIG)
app = FlaskAPI(__name__, instance_relative_config=False)
app.config["MONGO_URI"] = os.getenv("MONGODB_URI")
mongo = PyMongo(app)

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")

help_message = """To use folly, simply mention @folly and the reaction you'd love to grab.

*Example:*
> @folly 🍭
"""


@app.route("/bot", methods=["POST"])
@verify_request_depr
def bot():
    try:
        request_type = request.data.get("type")

        if request_type == "url_verification":
            challenge = request.data.get("challenge")
            return challenge

        event = request.data.get("event")
        event_type = event.get("type")

        if event_type != "app_mention":
            return "", 200

        current_user = event.get("user")
        edited = event.get("edited")
        thread_ts = event.get("thread_ts")
        channel = event.get("channel")
        reaction_text = event.get("text").strip()

        if edited:
            return "", 200

        team_id = request.data.get("team_id")
        team_query = {"team_id": team_id}
        team_details = mongo.db.teams.find_one(team_query)

        bot_token = team_details.get('bot_token')
        user_token = team_details.get('user_token')
        bot_client, user_client = create_client(bot_token, user_token)

        if not thread_ts:
            msg = "Folly can't be used outside a thread. \n"
            msg += help_message
            send_ephemeral_message(msg, thread_ts, channel, current_user, bot_client)
            return "", 200

        if re.search(HELP_REGEX, reaction_text):
            send_ephemeral_message(help_message, thread_ts, channel, current_user, bot_client)
            return "", 200

        reactions = re.findall(REACTION_REGEX, reaction_text)

        if not reactions:
            msg = "No reaction in text.\n"
            msg += help_message
            send_ephemeral_message(msg, thread_ts, channel, current_user, bot_client)
            return "", 200

        reaction_list = get_reactions(channel, thread_ts, user_client)

        reaction_details = get_reaction_details(reaction_list, reactions[0])

        if not reaction_details:
            msg = "Reaction doesn't exist on post! Kindly supply a reaction that is used on the initial message."
            send_ephemeral_message(msg, thread_ts, channel, current_user, bot_client)
            return "", 200

        permalink_response = get_message_permalink(thread_ts, channel, user_client)
        permalink = permalink_response.get("permalink")
        response = generate_user_response(reaction_details, current_user, permalink, bot_client)

        return "", 200
    except Exception as e:
        app.logger.exception(e)
        return "", 400


@app.route("/status")
def status():
    try:
        code = request.args.get("code")

        temp_client = SlackClient("")

        # Request the auth tokens from Slack
        auth_response = temp_client.api_call(
            "oauth.access",
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            code=code
        )

        ok = auth_response.get("ok")

        if not ok:
            print('\n\n', auth_response, '\n\n')
            error_message = "Error connecting to Slack!"
            return render_template("error.html", error_message=error_message)

        team_id = auth_response['team_id']
        team_name = auth_response['team_name']
        options = dict(
            user_token = auth_response['access_token'],
            bot_token = auth_response['bot']['bot_access_token'],
            team_id=team_id,
            team_name=team_name
        )

        existing_team_query = {"team_name": team_name, "team_id": team_id}
        existing_team_collection = mongo.db.teams.find(existing_team_query)

        if not existing_team_collection.count():
            mongo.db.teams.insert_one(options)

        return render_template("success.html", team_name=team_name)
    except Exception as e:
        app.logger.exception(e)
        return render_template("error.html", )


@app.route("/")
def home():
    redirect_url = "https://folly.herokuapp.com" if (environment == "production") else "http://localhost:5000"
    slack_url = f"https://slack.com/oauth/authorize?client_id=80830268038.729230020614&scope=reactions:read,channels:history,groups:history,bot&redirect_uri={redirect_url}/status"
    return render_template("index.html", slack_url=slack_url)


if __name__ == "__main__":
    app.logger.info("Starting Folly!")
    app.run(debug=is_debug)
