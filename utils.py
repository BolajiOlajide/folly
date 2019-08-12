import random
import string

from client import oauth_access_client, bot_client


def get_reactions(channel, message_ts):
    payload = dict(
        channel=channel,
        full=True,
        timestamp=message_ts
    )
    reactions_response = oauth_access_client.api_call("reactions.get", **payload)
    reactions = reactions_response.get("message").get("reactions")
    return reactions


def get_reaction_details(reaction_list, text):
    reaction_text = text.strip(":")
    for reaction in reaction_list:
        if (reaction.get("name") == reaction_text):
            return reaction
    return None


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def send_ephemeral_message(message, thread_ts, channel, user):
    return bot_client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message,
        as_user=True,
        thread_ts=thread_ts
    )


def upload_snippet(message, channel, thread_ts):
    return bot_client.api_call(
        "files.upload",
        content=message,
        filename=randomString(),
        thread_ts=thread_ts,
        channel=channel,
        filetype="text"
    )


def generate_user_response(reaction_details, channel, thread_ts):
    reactors = reaction_details.get("users")
    reaction = reaction_details.get("name")
    count = reaction_details.get("count")

    msg = f"""Hello,

Here is the list of people who reacted to the :{reaction}: you mentioned me on.
There are {count} reactors with the reaction specified.

"""

    for reactor in reactors:
        msg += f"<@{reactor}>, "

    formatted_msg = msg.strip().strip(",")
    return upload_snippet(formatted_msg, channel, thread_ts)
