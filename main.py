import os
import re
from logging.config import dictConfig

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_api import FlaskAPI
from flask_pymongo import PyMongo

from client import bot_client
from constants import LOGGING_CONFIG, REACTION_REGEX
from utils import (generate_user_response, get_message_permalink,
                   get_reaction_details, get_reactions, send_ephemeral_message)

load_dotenv(find_dotenv())

dictConfig(LOGGING_CONFIG)
app = FlaskAPI(__name__, instance_relative_config=False)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
db = PyMongo(app)

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
        reaction_text = event.get("text").strip()

        if edited:
            return "", 200

        if not thread_ts:
            msg = ">Folly can't be used outside a thread."
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        reaction_gen = re.finditer(REACTION_REGEX, reaction_text)

        try:
            reaction = next(reaction_gen)
        except StopIteration:
            reaction = None

        if not reaction:
            msg = """>>>Not a valid reaction.
Kindly supply a valid reaction and I'll do my job. 😄
Example: ```@folly 😃```
"""
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        reaction_list = get_reactions(channel, thread_ts)

        reaction_details = get_reaction_details(reaction_list, reaction)

        if not reaction_details:
            msg = "Reaction doesn't exist on post! Kindly supply a reaction that as been used on the parent message."
            send_ephemeral_message(msg, thread_ts, channel, current_user)
            return "", 200

        permalink_response = get_message_permalink(thread_ts, channel)
        permalink = permalink_response.get("permalink")
        response = generate_user_response(reaction_details, current_user, permalink)

        return "", 200
    except Exception as e:
        app.logger.exception(e)
        return "", 400


@app.route("/status")
def status():
    return render_template("index.html")


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.logger.info("Starting Folly!")
    app.run(debug=is_debug)
