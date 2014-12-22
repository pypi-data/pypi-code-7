    # ..............................................................................
    # System
    # ..............................................................................

    def post_client_log(self, log_messages):
        """
        Start logging (experimental).

        Sample data input::

            [{
                "timestamp"  : "Time stamp in ISO 8601",
                "message" : "The message log by the developer",
                "connection" : {
                    "internet" : True,
                    "netScope" : "WAN",
                    "netType"  : "LTE"
                }
             },
             {
                ...
             }
            ]
        """
        log_message = json.dumps(log_messages)
        # https://api.relayr.io/client/log
        url = '{0}/client/log'.format(self.host)
        _, data = self.perform_request('POST', url, data=log_messages, headers=self.headers)
        return data
