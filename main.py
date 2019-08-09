from flask import Flask
from flask_api import FlaskAPI
from slackclient import SlackClient
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

app = FlaskAPI(__name__, instance_relative_config=False)


if __name__ == "__main__":
    app.run()
