"""
Twotter

A class for scraping position data for BAS Air Unit assets from Latitude
Technologies WebSentinel private JSON API.
"""
import requests
from contextlib import closing
try:
    import simplejson as json
except ImportError:
    import json
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime as dt, timezone as tz, timedelta as td
import sys

class Twotter:
    def __init__(self, conf_path='twotter.json'):
        self.conf_path = conf_path
        self.conf = None
        self.session = None
        self.raw_json = None
        self.last_dump = None
        self.last_pos = None
        self.last_time = None
        self.plot_pos = None
        self.plot_wpt = None
        self.blank_map = self._create_blank_map()
        self.map = None
        self.timestamp = dt.utcnow()
        self._load_config()

    def _load_config(self):
        with open(self.conf_path) as config:
            try:
                self.conf = json.load(config)
            except ValueError as e:
                sys.exit('Error: Bad config file: {}'.format(e))

    def _create_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.conf['headers'])

    def login(self):
        self._create_session()
        # Load index page to get JSESSIONID cookie
        try:
            # Use closing() to make the request as we only want the headers and
            # the cookies. We're not interested in downloading the body.
            with closing(self.session.get(self.conf['url']['index'], stream=True)) as r:
                pass
        except requests.exceptions.ConnectionError as e:
            raise Exception('Loading index page failed: {} {}'.format(e[0],e[1][1]))
        # Now actually login
        login_payload = {
            'j_username': self.conf['auth']['username'],
            'j_password': self.conf['auth']['password']
        }
        try:
            with closing(self.session.post(self.conf['url']['auth'], data=login_payload, stream=True)) as r:
                pass
        except requests.exceptions.ConnectionError as e:
            raise Exception('Login failed: {} {}'.format(e[0],e[1][1]))

    def _check_login(self):
        if not self.session.cookies:
            self._close_session()
            self.raw_json = None
            raise Exception('Session expired')
        if 'error' in self.raw_json:
            self._close_session()
            self.raw_json = None
            raise Exception('Session expired')

    def get_pos(self):
        last_period = self.timestamp - td(seconds=self.conf['period'])
        js_last_period = round(last_period.timestamp() * 1000)
        payload = {"get_positions": {"last_call_utc": js_last_period}}
        # Hacky way to pass request as WebSentinel client doesn't serialize JSON properly...
        plog_req = "{0}?get_positions=%7B%22last_call_utc%22%3A{1}%7D".format(self.conf['url']['api'], js_last_period)
        plog_resp = self.session.get(plog_req)
        self.raw_json = plog_resp.json(encoding='utf-8')

    def _close_session(self):
        self.session.close()

    def _mts2utc(self, timestamp):
        """Converts microsecond timestamp into UTC datetime object"""
        return dt.utcfromtimestamp(timestamp/1000).replace(tzinfo=tz.utc)

    def parse_json(self):
        positions = self.raw_json['get_positions']['positions']
        self.last_time = self._mts2utc(self.raw_json['get_positions']['call_time_utc'])
        #id vehicle_id utc device_id entered lat lng alt speed track hdop rc
        self.last_dump = [[
                e['id'],
                e['vehicle_id'],
                self._mts2utc(e['utc']),
                e['device_id'],
                self._mts2utc(e['entered']),
                e['lat'],
                e['lng'],
                e['alt'],
                e['speed'],
                e['track'],
                e['hdop'],
                e['rc']] for e in positions]
        self.last_dump.sort(key=lambda x: (x[1],x[2]), reverse=True)
        self.last_pos = {reg: next((x for x in self.last_dump if x[1] == i['id']), None) for reg, i in self.conf['aircraft'].items()}

    def save_raw_json(self):
        filename = '{0}{1}Z.json'.format(self.conf['output']['json_dir'], self.timestamp.format('YYYYMMDDTHHmmss'))
        try:
            with open(filename, mode='w') as output:
                json.dump(self.raw_json,
                            output,
                            encoding='utf-8',
                            sort_keys=True,
                            indent=2)
        except IOError as e:
            raise Exception('Error: Unable to write JSON output: {}'.format(e))

    def _create_blank_map(self):
        # Lambert conformal basemap
        # lat_1 is first standard parallel.
        # lat_2 is second standard parallel (defaults to lat_1).
        # lon_0,lat_0 is central point.
        # rsphere=(6378137.00,6356752.3142) specifies WGS4 ellipsoid
        # area_thresh=1000 means don't plot coastline features less
        # than 1000 km^2 in area.
        m = Basemap(width=5000000,
                    height=5000000,
                    rsphere=(6378137.00,6356752.3142),
                    resolution='h',
                    area_thresh=1000.,
                    projection='lcc',
                    lat_1=-67,
                    lat_0=-70,
                    lon_0=-68.)
        # Draw parallels and meridians.
        m.drawparallels(np.arange(-80.,81.,10.))
        m.drawmeridians(np.arange(-180.,181.,20.))
        m.shadedrelief()
        return m

    def _aircraft_symbol(self, angle):
        if (0 <= angle <= 45) or (315 < angle <= 360):
            return '^'
        elif 45 < angle <= 135:
            return '>'
        elif 135 < angle <= 225:
            return 'v'
        elif 225 < angle <= 315:
            return '<'
        else:
            return 'o'

    def plot_aircraft(self):
        m = self.blank_map
        # Draw aircraft
        for k,v in self.last_pos.items():
            try:
                m.plot(v[6],
                        v[5],
                        marker=self._aircraft_symbol(v[9]),
                        color=self.conf['aircraft'][k]['color'],
                        markersize=5,
                        label=k,
                        latlon=True
                        )
            except TypeError:
                pass #Skip any blank 'None' entries
        # Draw waypoints
        for point, pos in self.conf['waypoints'].items():
            m.plot(pos['lon'], pos['lat'], color="black", marker=".", markersize=3, latlon=True)
        plt.legend(loc=1, fontsize='small', numpoints=1, scatterpoints=1)
        plt.title("BAS Air Unit - {0}".format(self.last_time.strftime('%Y-%m-%d %H:%M %Z')))
        self.map = m

    def save_plot(self):
        plt.savefig(self.conf['output']['img'], bbox_inches='tight', dpi=1200)
        plt.close()
