from pyslaquery.utils import find_channel_id, filter_out_message_subtypes
from pyslaquery.connection import SlackAPIConnection
from pyslaquery.exception import SlackAPIError


class SlackBase(object):
    _slackconnection = None

    def __init__(self, token):
        self._slackconnection = SlackAPIConnection("https://slack.com/api", token)


class SlackQueryClient(SlackBase):
    def __init__(self, token):
        super(SlackQueryClient, self).__init__(token)

    def get_messages_for_channel(self, req_channel, no_subtypes=True, count=10, resolve_usernames=False, **params):
        """
        Fetches history of messages and events from a channel.
        Method: channels.history

        :param req_channel: Channel to get messages from.
        :param no_subtypes: Show only plain messages, no messages with subtypes.
        :param count: Limit number of showned messages
        :param params: extra parameters to send with the request to the Slack API.
        return: dict object of channels from the Slack API.
        """
        method = 'channels.history'

        # Search channel ID
        channel_id = find_channel_id(self.get_channel_list(), req_channel)

        # Check if the channel id is found and continue.
        if channel_id is not None:
            # Update params to the API.
            params.update({
                'channel': channel_id,
                'count': count
            })

            # Get Response.
            channel_response = self._slackconnection.create_post_request(method, params).json()

            # Filter out message with subtypes, if there are any.
            if no_subtypes is True:
                channel_response["messages"] = filter_out_message_subtypes(channel_response["messages"])
            # Resolve username ids to user NAMES.
            if resolve_usernames is True:
                for message in channel_response["messages"]:
                    message["user"] = self.get_user_info(message["user"])["name"]

            # Return response as a dict.
            return channel_response["messages"]

        # Exception handling.
        raise SlackAPIError("Could not find the channel specified.")

    def get_channel_list(self, **params):
        """
        Lists all channels in a Slack team.
        Method: channels.list

        return: dict object from the Slack API.
        """
        method = 'channels.list'

        # Get Response.
        response = self._slackconnection.create_get_request(method, params).json()

        # Exception handling.
        if response["ok"] is False:
            raise SlackAPIError(response["error"])

        # Return messages as a dict.
        return response["channels"]

    def get_channel_info(self, req_channel, **params):
        """
        Gets information about a channel.
        Method: channels.info

        :param params: extra parameters to send with the request to the Slack API.
        :return: dict object from the Slack API.
        """
        method = 'channels.info'

        # Update params to the API.
        params.update({
            'channel': req_channel
        })

        # Get Response.
        response = self._slackconnection.create_get_request(method, params).json()

        # Exception handling.
        if response["ok"] is False:
            raise SlackAPIError(response["error"])

        # Return messages as a dict.
        return response["channels"]

    def get_user_info(self, user_id, **params):
        """
        Gets information about a user.
        Method: users.info

        :param params: extra parameters to send with the request to the Slack API.
        :return: dict object from the Slack API.
        """
        method = 'users.info'

        # Update params to the API.
        params.update({
            'user': user_id
        })

        response = self._slackconnection.create_get_request(method, params).json()

        # Exception handling.
        if response["ok"] is False:
            raise SlackAPIError(response["error"])

        # Return messages as a dict.
        return response["user"]