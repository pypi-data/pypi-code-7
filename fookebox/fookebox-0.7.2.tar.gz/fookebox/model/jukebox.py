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

import random
import logging

from pylons import config, app_globals as g

from mpd import CommandError
from mpdconn import MPD, Genre, Artist, Track

log = logging.getLogger(__name__)

class QueueFull(Exception):
	pass

class Jukebox(object):
	client = None
	lastAutoQueued = -1

	def __init__(self, mpd=None):

		self._connect(mpd)

	def _connect(self, to=None):

		if to != None:
			self.client = to
			return

		mpd = MPD.get()
		self.client = mpd

	def reconnect(self):

		self.client.disconnect()
		log.info("Reconnecting...")
		self.client.connect()

	def timeLeft(self):

		with self.client:
			status = self.client.status()

		if 'time' not in status:
			return 0

		(timePlayed, timeTotal) = status.get('time', '').split(':')
		timeLeft = int(timeTotal) - int(timePlayed)
		return timeLeft

	def queue(self, file):

		log.info("Queued %s" % file)

		if self.getQueueLength() >= config.get('max_queue_length'):
			raise QueueFull()

		with self.client:
			self.client.add(file)
			self.client.play()

	def _autoQueueRandom(self):

		genre = config.get('auto_queue_genre')

		if genre:
			with self.client:
				songs = self.client.search('Genre', str(genre))
		else:
			with self.client:
				songs = self.client.listall()

		if len(songs) < 1:
			return

		file = []
		retries = 4

		while 'file' not in file and retries > 0:
			# we might have to try several times in case we get
			# a directory instead of a file
			index = random.randrange(len(songs))
			file = songs[index]
			retries -= 1

		self.queue(file['file'])

	def _autoQueuePlaylist(self, playlist):

		try:
			with self.client:
				self.client.load(playlist)
		except CommandError:
			log.error("Failed to load playlist")
			return

		if config.get('auto_queue_random'):
			with self.client:
				self.client.shuffle()
				playlist = self.client.playlist()
			song = playlist[0]
		else:
			with self.client:
				playlist = self.client.playlist()

			if len(playlist) < 1:
				return

			index = (Jukebox.lastAutoQueued + 1) % len(playlist)
			song = playlist[index]
			Jukebox.lastAutoQueued += 1

		with self.client:
			self.client.clear()

		self.queue(song[6:])

	def autoQueue(self):

		log.info("Auto-queuing")
		if not g.autoQueueLock.acquire(False):
			return

		playlist = config.get('auto_queue_playlist')
		if playlist == None:
			self._autoQueueRandom()
		else:
			self._autoQueuePlaylist(playlist)

		g.autoQueueLock.release()

	def search(self, where, what, forceSearch = False):

		act = self.client.search

		if config.get('find_over_search') and not forceSearch:
			act = self.client.find

		with self.client:
			result = act(where, what)

		return result

	def getPlaylist(self):

		with self.client:
			playlist = self.client.playlistinfo()
			status = self.client.status()

		index = int(status.get('song', 0))
		return playlist[index:]

	def getGenres(self):

		with self.client:
			genres = sorted(self.client.list('genre'))

		return [Genre(genre.decode('utf8')) for genre in genres]

	def getArtists(self):

		with self.client:
			artists = sorted(self.client.list('artist'))

		return [Artist(artist.decode('utf8')) for artist in artists]

	def isPlaying(self):

		with self.client:
			status = self.client.status()

		return status.get('state') == 'play'

	def getCurrentSong(self):

		with self.client:
			current = self.client.currentsong()

		if current == None:
			return None

		with self.client:
			status = self.client.status()

		if 'time' in status:
			time = status.get('time', '').split(':')[0]
		else:
			time = 0

		track = Track()
		track.load(current)
		track.timePassed = time

		return track

	def getQueueLength(self):

		with self.client:
			playlist = self.client.playlist()
			status = self.client.status()

		index = int(status.get('song', 0))

		return max(len(playlist) - 1 - index, 0)

	def remove(self, id):

		log.info("Removing playlist item #%d" % id)

		with self.client:
			status = self.client.status()

		index = int(status.get('song', 0))
		log.info('index=%d' % index)

		with self.client:
			self.client.delete(id + index)

	def play(self):

		with self.client:
			self.client.play()

	def pause(self):

		with self.client:
			self.client.pause()

	def previous(self):

		with self.client:
			self.client.previous()

	def next(self):

		# This is to prevent interruptions in the audio stream
		# See http://code.google.com/p/fookebox/issues/detail?id=6
		if self.getQueueLength() < 1 and config.get('auto_queue'):
			self.autoQueue()

		with self.client:
			self.client.next()

	def volumeDown(self):

		with self.client:
			status = self.client.status()
			volume = int(status.get('volume', 0))
			self.client.setvol(max(volume - 5, 0))

	def volumeUp(self):

		with self.client:
			status = self.client.status()
			volume = int(status.get('volume', 0))
			self.client.setvol(min(volume + 5, 100))

	def refreshDB(self):

		with self.client:
			self.client.update()
