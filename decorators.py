import functools
import hmac
import os
import time

from flask import make_response, request

SIGNING_SECRET = os.getenv("SIGNING_SECRET")


def is_timestamp_invalid(timestamp):
    current_time = abs(time.time())
    MAX_TIME = 60 * 5  # 5 minutes

    return (current_time - int(timestamp)) > MAX_TIME


def calculate_signature(base_string):
    options = [SIGNING_SECRET, base_string]
    generated_hash = hmac.compute_hash_sha256(*options).hexdigest()
    return f"v0={generated_hash}"


def verify_request(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # print(dir(request), '\n\n')
        # print(request.values)
        signature = request.headers.get("X-Slack-Signature")
        timestamp = request.headers.get("X-Slack-Request-Timestamp")

        if is_timestamp_invalid(timestamp):
            return make_response("Invalid Request.", 400)

        request_body = request.get_data()
        base_string = f"v0:{timestamp}:{request_body}"
        calculated_signature = calculate_signature(base_string)

        if hmac.compare(calculated_signature, signature):
            return f(*args, **kwargs)
        return make_response("Invalid Request.", 400)

    return wrapped


def verify_request_depr(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        verification_token = request.data.get("token")
        VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

        if verification_token == VERIFICATION_TOKEN:
            return f(*args, **kwargs)
        return make_response("Invalid Request.", 400)

    return wrapped
