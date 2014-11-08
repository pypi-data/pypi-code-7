# fookebox, https://github.com/cockroach/fookebox
#
# Copyright (C) 2007-2014 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import base64
import logging
from mpd import MPDClient
from threading import Lock
from pylons.i18n.translation import _

from pylons import config, app_globals as g
from fookebox.model.albumart import AlbumArt

log = logging.getLogger(__name__)

class Genre(object):

	def __init__(self, name):
		self.name = name
		self.base64 = base64.urlsafe_b64encode(name.encode('utf8'))

class Artist(object):

	def __init__(self, name):
		self.name = name
		self.base64 = base64.urlsafe_b64encode(name.encode('utf8'))

class Album(object):

	def __init__(self, artist, albumName, disc=None):
		self.isCompilation = False

		if albumName == None:
			self.name = ''
		else:
			self.name = albumName

		if artist == None:
			self.artist = ''
		else:
			self.artist = artist

		self.disc = disc
		self.tracks = []

	def add(self, track):
		if track.artist != self.artist and not (
			track.artist.startswith(self.artist) or
			self.artist.startswith(track.artist)):

			self.isCompilation = True
			self.artist = _('Various Artists').decode('utf8')

		self.tracks.append(track)

	def load(self):

		mpd = MPD.get()

		with mpd:
			data = mpd.find(
				'Artist', self.artist.encode('utf8'),
				'Album', self.name.encode('utf8'))

		for file in data:
			track = Track()
			track.load(file)
			self.add(track)

	def hasCover(self):
		art = AlbumArt(self)
		return art.get() != None

	def getCoverURI(self):
		artist = base64.urlsafe_b64encode(self.artist.encode('utf8'))
		name = base64.urlsafe_b64encode(self.name.encode('utf8'))
		return "%s/%s" % (artist, name)

	def getPath(self):
		basepath = config.get('music_base_path')

		if basepath == None:
			return None

		if len(self.tracks) > 0:
			track = self.tracks[0]
		else:
			self.load()
			if len(self.tracks) < 1:
				return None

			track = self.tracks[0]

		fullpath = os.path.join(basepath, track.file)
		return os.path.dirname(fullpath)

	def key(self):
		return "%s-%s" % (self.artist, self.name)

class Track(object):

	NO_ARTIST = 'Unknown artist'
	NO_TITLE = 'Unnamed track'

	track = 0

	def load(self, song):
		def __set(key, default):
			val = song.get(key, default)

			if val is None:
				return val

			if isinstance(val, list):
				val = val[0]

			if isinstance(val, int):
				return val
			else:
				return val.decode('utf8')

		self.artist = __set('artist', Track.NO_ARTIST)
		self.title = __set('title', Track.NO_TITLE)
		self.file = __set('file', '')
		self.disc = __set('disc', 0)
		self.album = __set('album', None)
		self.queuePosition = int(__set('pos', 0))
		self.time = int(__set('time', 0))

		def parse_track_number(t):
			# possible formats:
			#  - '12'
			#  - '12/21'
			#  - ['12', '21']
			#  - ['12/21', '21']
			if '/' in t:
				tnum = t.split('/')[0]
				return int(tnum)
			elif isinstance(t, list):
				return parse_track_number(t[0])
			else:
				return int(t)

		if 'track' in song:
			self.track = parse_track_number(song['track'])

	def __str__(self):
		return "%s - %s" % (self.artist, self.title)

class LockableMPDClient(MPDClient):

	def __init__(self, host, port, password, use_unicode=False):
		super(LockableMPDClient, self).__init__()
		self.use_unicode = use_unicode
		self.host = host
		self.port = port
		self.password = password
		self._lock = Lock()
	def acquire(self):
		self._lock.acquire()
	def release(self):
		self._lock.release()
	def __enter__(self):
		self.acquire()
	def __exit__(self, type, value, traceback):
		self.release()
	def connect(self):
		super(LockableMPDClient, self).connect(self.host, self.port)
		if self.password:
			super(LockableMPDClient, self).password(self.password)

class MPD(object):

	@staticmethod
	def get():
		if g.mpd != None:
			return g.mpd

		host = config.get('mpd_host')
		port = config.get('mpd_port')
		password = config.get('mpd_pass')

		client = LockableMPDClient(host, port, password)
		client.connect()

		if config.get('consume'):
			client.consume(1)

		g.mpd = client
		return g.mpd
