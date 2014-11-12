#
# Copyright 2014 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""Performs requests to the Google Maps Elevation API."""
from googlemaps import convert

def elevation(client, locations):
    """
    Provides elevation data for locations provided on the surface of the
    earth, including depth locations on the ocean floor (which return negative
    values)

    :param locations: A single latitude/longitude tuple or dict, or a list of
            latitude/longitude tuples or dicts from which you wish to calculate
            elevation data.
    :type locations: list or tuple

    :rtype: list of elevation data responses
    """
    params = {}
    if type(locations) is tuple:
        locations = [locations]

    params["locations"] = convert.join_list("|",
            [convert.latlng(k) for k in convert.as_list(locations)])

    return client._get("/maps/api/elevation/json", params)["results"]

def elevation_along_path(client, path, samples):
    """
    Provides elevation data sampled along a path on the surface of the earth.

    :param path: A encoded polyline string, or a list of
            latitude/longitude tuples from which you wish to calculate
            elevation data.
    :type path: str or list

    :param samples: The number of sample points along a path for which to
            return elevation data.
    :type samples: int

    :rtype: list of elevation data responses
    """

    if type(path) is str:
        path = "enc:%s" % path
    else:
        path = convert.join_list("|",
                [convert.latlng(k) for k in convert.as_list(path)])

    params = {
        "path": path,
        "samples": samples
    }

    return client._get("/maps/api/elevation/json", params)["results"]
