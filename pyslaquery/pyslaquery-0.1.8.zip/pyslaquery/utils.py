def find_channel_id(channels, req_channel):
    """
    Find channel ID from a human readable name.
    :param req_channel: channel name
    :return: channel id string.
    """
    for channel in channels:
        if channel["name"] == req_channel:
            return channel["id"]


def filter_out_message_subtypes(messages):
    """
    Filter out all message that have subtype. Only plain messages by users are used.
    :param messages: total messages
    :return: list of messages
    """
    filtered_messages = []
    for message in messages:
        if "subtype" not in message:
            filtered_messages.append(message)
    return filtered_messages