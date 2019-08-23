import random
import string


def get_reactions(channel, message_ts, user_client):
    payload = dict(channel=channel, full=True, timestamp=message_ts)
    reactions_response = user_client.api_call("reactions.get", **payload)
    reactions = reactions_response.get("message").get("reactions")
    return reactions


def get_reaction_details(reaction_list, text):
    reaction_text = text.strip(":")
    for reaction in reaction_list:
        if reaction.get("name") == reaction_text:
            return reaction
    return None


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


def send_ephemeral_message(message, thread_ts, channel, user, bot_client):
    return bot_client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message,
        as_user=True,
        thread_ts=thread_ts,
    )


def send_message(message, user, bot_client):
    return bot_client.api_call(
        "chat.postMessage", channel=user, text=message, as_user=True
    )


def get_message_permalink(message_ts, channel, user_client):
    return user_client.api_call(
        "chat.getPermalink", channel=channel, message_ts=message_ts
    )


def generate_user_response(reaction_details, current_user, permalink, bot_client):
    reactors = reaction_details.get("users")
    reaction = reaction_details.get("name")
    count = reaction_details.get("count")

    msg = f""">>>Hello,

Here is the list of people who reacted with :{reaction}: on {permalink}.
There are {count} reactors with the :{reaction}: reaction:

"""

    for reactor in reactors:
        msg += f"<@{reactor}> "

    formatted_msg = msg.strip()
    return send_message(formatted_msg, current_user, bot_client)
