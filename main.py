import os
import re
from logging.config import dictConfig

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from flask_api import FlaskAPI

from client import bot_client
from utils import get_reactions, get_reaction_details, send_ephemeral_message, generate_user_response, get_message_permalink
from constants import REACTION_REGEX, LOGGING_CONFIG

load_dotenv(find_dotenv())

dictConfig(LOGGING_CONFIG)
app = FlaskAPI(__name__, instance_relative_config=False)

environment = os.getenv("ENV", "development")
is_debug = environment == "development"


@app.route("/bot", methods=["POST"])
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
        reaction_text = event.get("text").strip().split(">")

        if edited:
            return "", 200

        if not thread_ts:
            msg = ">Folly can't be used outside a thread."
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        if not len(reaction_text):
            msg = ">No reaction supplied!"
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        reaction = reaction_text[1].strip()
        is_valid_reaction = re.match(REACTION_REGEX, reaction)
        if not is_valid_reaction:
            msg = "Not a valid reaction."
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        reaction_list = get_reactions(channel, thread_ts)

        reaction_details = get_reaction_details(reaction_list, reaction)

        if not reaction_details:
            msg = "Reaction doesn't exist on post!"
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        permalink_response = get_message_permalink(thread_ts, channel)
        permalink = permalink_response.get("permalink")
        response = generate_user_response(reaction_details, current_user, permalink)

        return "", 200
    except Exception as e:
        app.logger.error(e.args[0])
        return "", 400


if __name__ == "__main__":
    app.logger.info("Starting Folly!")
    app.run(debug=is_debug)
