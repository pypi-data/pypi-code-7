import requests
import json
import datetime
import random
import string


class Api(object):

    """ Base API class
    >>> api = Api()
    >>> s = api.air_search(origin="SFO", destination="LAX",\
     departure_date="2015-09-14")
    >>> "airSearchRsp" in s
    True
    """

    def __init__(self):
        self._session = requests.Session()

        self._session.headers = {
            "User-Agent":
            "Priceline 12.1 rv:121000051 (iPhone; iPhone OS 8.1.2; en_US)",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

    def _validate_date(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

    def air_search(self, origin, destination, departure_date):
        # TODO: check airport codes
        assert(len(origin) == len(destination) == 3)
        self._validate_date(departure_date)

        with open("priceline/air_search_oneway.json") as data:
            payload = json.load(data)
            trip = payload["airSearchReq"]["trip"]
            payload['airSearchReq']['requestId'] = ''.join(
                random.SystemRandom().choice(string.ascii_lowercase +
                                             string.ascii_uppercase +
                                             string.digits) for _ in range(20))

            trip.append(
                {
                    "slice": [
                        {
                            "origins": [
                                {
                                    "type": "AIRPORT",
                                    "location": origin
                                }
                            ],
                            "id": 1,
                            "destinations": [
                                {
                                    "type": "AIRPORT",
                                    "location": destination
                                }
                            ],
                            "departDate": departure_date
                        }
                    ]
                })

        r = self._session.post(
            "https://www.priceline.com/pws/v0/fly/c/airSearch",
            data=json.dumps(payload))
        r.raise_for_status()

        return r.json()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
