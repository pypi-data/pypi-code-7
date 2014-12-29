# -*- coding: utf-8 -*-
""" Main module.  """

__author__ = 'Rory McCann'
__email__ = 'rory@technomancy.org'

from ._version import __version__

USER_AGENT = "osm-find-first/{0}".format(__version__)

import requests
import csv
import argparse
import sys
from xml.etree import ElementTree
import logging
import time
import os

logger = logging.getLogger(__name__)


def is_int(x):
    """Return True iff this can be turned into an int."""
    try:
        int(x)
        return True
    except:
        return False


def is_osm_type(x):
    """Return True iff this is a valid 'osm_type'."""
    return x in ['node', 'way', 'relation']


def find_first(known_data, osm_objs):
    """
    Query OSM API for the objects in `osm_objs`.

    Keeps in mind `known_data`, and returns the combination of `known_data` and the results for `osm_objs`.
    """
    if len(osm_objs) == 0:
        return known_data

    # ensure it's correct format
    osm_objs = [{'osm_type': str(x['osm_type']), 'osm_id': str(x['osm_id'])}
                for x in osm_objs]

    known_data_indexed = dict(((x['osm_type'], x['osm_id']), x)
                              for x in known_data)
    missing_objs = [x for x in osm_objs if (
        x['osm_type'], x['osm_id']) not in known_data_indexed]

    num_objs = len(missing_objs)
    logger.info("Need to query OSM for %d objects", num_objs)
    # print "Need to query OSM for %d objects" % num_objs

    for idx, obj in enumerate(missing_objs):
        assert is_osm_type(obj['osm_type'])
        assert is_int(obj['osm_id'])
        url = "http://api.openstreetmap.org/api/0.6/{osm_type}/{osm_id}/1".format(
            **obj)
        response = requests.get(url, headers={'User-agent': USER_AGENT})
        time.sleep(0.1)
        parsed = ElementTree.fromstring(response.content)
        attrib = parsed[0].attrib

        osm_uid = attrib['uid']
        osm_user = attrib['user']
        osm_timestamp = attrib['timestamp']
        logger.debug("Obj %d of %d: Got details for %s %s",
                     idx + 1, num_objs, obj['osm_type'], obj['osm_id'])
        # print "Obj %d of %d: Got details for %s %s" % ( idx+1, num_objs,
        # obj['osm_type'], obj['osm_id'])

        known_data.append({'osm_id': obj['osm_id'], 'osm_type': obj[
                          'osm_type'], 'osm_uid': osm_uid, 'osm_user': osm_user, 'osm_timestamp': osm_timestamp})

    return known_data


def find_first_from_csvs(csv_known_filename, missing):
    """
    Read data from the CSV file `csv_known_filename`, and queries for missing (filename or list of dicts) and saves it to csv_known_filename.

    :returns: Whatever data we could downland
    :param str: csv
    """
    with open(csv_known_filename) as fp:
        csv_known_reader = csv.DictReader(fp)
        known_data = list(csv_known_reader)
        logger.info("Read %d OSM objects from file %s",
                    len(known_data), csv_known_filename)

    if isinstance(missing, basestring) and os.path.isfile(missing):
        missing_osm_objs = read_missing_from_csv(missing)
    else:
        missing_osm_objs = missing
    logger.info("There are %d OSM objects", len(missing_osm_objs))

    try:
        new_data = find_first(known_data, missing_osm_objs)
    except BaseException as ex:
        # print repr(ex)
        # Exception!
        new_data = known_data

    write_to_csv(csv_known_filename, new_data)
    return new_data


def write_to_csv(filename, result_data):
    """Write the result data to filename."""
    with open(filename, 'w') as fp:
        csv_writer = csv.DictWriter(
            fp, ['osm_type', 'osm_id', 'osm_user', 'osm_uid', 'osm_timestamp'], lineterminator='\n')
        csv_writer.writeheader()
        csv_writer.writerows(result_data)


def read_missing_from_csv(csv_filename):
    """Read & return missing data from filename."""
    with open(csv_filename) as fp:
        csv_reader = csv.DictReader(fp)
        missing = list(csv_reader)
    return missing


def main(argv):
    """Main method."""
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.setLevel(logging.DEBUG)

    find_first_from_csvs('ieadmins.csv', 'iemissing.csv')


if __name__ == '__main__':
    main(sys.argv[1:])
