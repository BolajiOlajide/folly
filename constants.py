REACTION_REGEX = r":\S*:"
USER_HANDLE_REGEX = r"<\S*>"
HELP_REGEX = r"^<\S*> help$"

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["wsgi"]},
}
