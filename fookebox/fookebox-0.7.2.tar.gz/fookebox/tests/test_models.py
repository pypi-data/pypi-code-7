import logging
import unittest

from mpd import CommandError
from pylons import config
from fookebox.model.jukebox import Jukebox, QueueFull
from fookebox.model.mpdconn import Track

log = logging.getLogger(__name__)

class FakeMPD(object):

	def __init__(self):

		self.db = []
		self.fillDB()
		self.stop()
		self.queue = []
		self._pos = 0
		self._consume = False

	def __enter__(self):
		pass

	def __exit__(self, _, __, ___):
		pass

	def fillDB(self):

		self.db.append({
			'file': 'song1',
			'time': '120',
			'album': 'Album 1',
			'title': 'Track 1',
			'track': '1',
			'genre': 'Genre 1',
			'artist': 'Artist 1',
			'date': '2005',
		})
		self.db.append({
			'file': 'song2',
			'artist': 'Artist 2',
			'title': 'Track 2',
		})
		self.db.append({
			'file': 'song3',
			'time': '144',
			'album': 'Album 1',
			'title': 'Track 2',
			'track': '2/4',
			'genre': 'Genre 1',
			'artist': 'Artist 1',
			'date': '2005',
		})
		self.db.append({
			'file': 'song4',
			'time': '123',
			'album': 'Album 2',
			'title': 'Track 3',
			'track': ['11', '12'],
			'genre': 'Genre 1',
			'artist': 'Artist 1',
			'date': '2005',
		})
		self.db.append({
			'file': 'song5',
			'time': '555',
			'album': 'Album 5',
			'title': 'Track 5',
			'genre': 'Genre 5',
			'artist': 'Artist 5',
			'date': '2005',
		})
		self.db.append({
			'file': 'song6',
			'time': '123',
			'album': 'Album 6',
			'title': 'Track 6',
			'track': ['55/12', '12'],
			'genre': 'Genre 6',
			'artist': 'Artist 6',
			'date': '2005',
		})

	def stop(self):

		self._status = {
			'playlistlength': '0',
			'playlist': '5',
			'state': 'stop',
			'volume': '100',
		}

	def play(self):

		if len(self.queue) > 0:
			self._status = {
				'playlistlength': '1',
				'playlist': '5',
				'state': 'play',
				'volume': '100',
			}

			song = self.queue[self._pos]
			if 'time' in song:
				self._status['time'] = '0:%s' % song['time']
			else:
				self._status['time'] = '0:0'

	def load(self, playlist):

		if playlist == 'test01':
			self.queue = [ 'file: song5', 'file: song5' ]
		else:
			raise CommandError

	def status(self):

		status = self._status
		status['song'] = self._pos
		return status

	def playDummy(self, index):

		self.queue = [self.db[index]]
		self._pos = 0
		self.play()

	def close(self):

		pass

	def disconnect(self):

		pass

	def skipTime(self, interval):

		(time, total) = self._status['time'].split(':')
		time = int(time)
		time = min(time + interval, int(total))
		self._status['time'] = "%s:%s" % (time, total)

	def add(self, file):

		log.info('Trying to add file "%s"' % file)

		for song in self.db:
			log.debug('Checking "%s"', song['file']);
			if song['file'] == file:
				self.queue.append(song)
				log.info('File queued')
				return

		log.error('File not found')

	def delete(self, index):

		self.queue.remove(self.queue[index])
		if self._pos > index:
			self._pos -= 1

		if len(self.queue) < 1:
			self.stop()

	def playlist(self):

		return [ x for x in self.queue]

	def playlistinfo(self):

		return self.queue

	def currentsong(self):

		song = self.queue[self._pos]

		if song != None:
			song['pos'] = self._pos

		return song

	def next(self):

		if self._consume:
			self.queue = self.queue[1:]
		else:
			self._pos += 1

	def search(self, field, value):

		result = []
		field = field.lower()

		for song in self.db:
			if field in song and value in song[field]:
				result.append(song)

		return result

	def find(self, field, value):

		result = []
		field = field.lower()

		for song in self.db:
			if field in song and value == song[field]:
				result.append(song)

		return result

	def list(self, attr):

		result = []

		for song in self.db:
			if attr in song:
				val = song[attr]

				if val not in result:
					result.append(val)

		return result

	def listall(self):

		return self.db

	def clear(self):

		self.queue = []
		self.pos = 0


class TestJukebox(unittest.TestCase):

	def setUp(self):

		self.mpd = FakeMPD()
		self.jukebox = Jukebox(self.mpd)
		config['max_queue_length'] = 3

	def test_timeLeft(self):

		self.assertEqual(0, self.jukebox.timeLeft())

		self.mpd.playDummy(0)
		self.mpd.skipTime(30)
		self.assertEqual(90, self.jukebox.timeLeft())

		self.mpd.playDummy(1)
		self.assertEqual(0, self.jukebox.timeLeft())

		self.mpd.skipTime(30)
		self.assertEqual(0, self.jukebox.timeLeft())

	def test_queue_starts_playback(self):

		self.assertFalse(self.jukebox.isPlaying())

		self.jukebox.queue(self.mpd.db[0]['file'])
		self.assertEqual(1, len(self.jukebox.getPlaylist()))
		self.assertTrue(self.jukebox.isPlaying())

		self.jukebox.queue(self.mpd.db[1]['file'])
		self.assertEqual(2, len(self.jukebox.getPlaylist()))
		self.assertTrue(self.jukebox.isPlaying())

	def test_queue_length_consume(self):

		self.mpd._consume = True
		config['max_queue_length'] = 2
		song1 = self.mpd.db[0]

		self.jukebox.queue(song1.get('file'))
		self.jukebox.queue(song1.get('file'))
		self.jukebox.queue(song1.get('file'))

		self.assertEqual(3, len(self.jukebox.getPlaylist()))

		with self.assertRaises(QueueFull):
			self.jukebox.queue(song1.get('file'))

		self.assertEqual(3, len(self.jukebox.getPlaylist()))

	def test_queue_length_no_consume(self):

		self.mpd._consume = True
		config['max_queue_length'] = 2
		song1 = self.mpd.db[0]

		self.jukebox.queue(song1.get('file'))
		self.jukebox.queue(song1.get('file'))
		self.jukebox.queue(song1.get('file'))

		self.assertEqual(3, len(self.jukebox.getPlaylist()))

		with self.assertRaises(QueueFull):
			self.jukebox.queue(song1.get('file'))

		self.assertEqual(3, len(self.jukebox.getPlaylist()))

	def test_autoQueueRandom(self):

		config['auto_queue_genre'] = None
		config['auto_queue_playlist'] = None

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.autoQueue()
		self.assertEqual(1, len(self.jukebox.getPlaylist()))

	def test_autoQueueGenre(self):

		config['auto_queue_genre'] = 'Genre 5'
		config['auto_queue_playlist'] = None

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.autoQueue()
		self.assertEqual(1, len(self.jukebox.getPlaylist()))

		track = self.jukebox.getCurrentSong()
		self.assertEqual(track.title, 'Track 5')

	def test_autoQueuePlaylist(self):

		config['auto_queue_genre'] = None
		config['auto_queue_playlist'] = 'test01'
		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.autoQueue()
		self.assertEqual(1, len(self.jukebox.getPlaylist()))

		config['auto_queue_playlist'] = 'test_does_not_exist'
		self.jukebox.autoQueue()

		self.assertEqual(1, len(self.jukebox.getPlaylist()))

	def test_searchGenre(self):

		config['find_over_search'] = False

		tracks = self.jukebox.search('genre', 'Genre 5')
		self.assertEqual(1, len(tracks));

		tracks = self.jukebox.search('Genre', 'Genre 5')
		self.assertEqual(1, len(tracks));

	def test_find_vs_search(self):

		config['find_over_search'] = False

		tracks = self.jukebox.search('genre', 'Genre')
		self.assertNotEqual(0, len(tracks))

		tracks = self.jukebox.search('genre', 'Genre 5')
		self.assertNotEqual(0, len(tracks))

		config['find_over_search'] = True

		tracks = self.jukebox.search('genre', 'Genre')
		self.assertEqual(0, len(tracks))

		tracks = self.jukebox.search('genre', 'Genre 5')
		self.assertNotEqual(0, len(tracks))

	def test_forceSearch(self):

		config['find_over_search'] = True

		tracks = self.jukebox.search('genre', 'Genre', forceSearch = True)
		self.assertNotEqual(0, len(tracks))

		tracks = self.jukebox.search('genre', 'Genre 5', forceSearch = True)
		self.assertNotEqual(0, len(tracks))

	def test_searchArtist(self):

		config['find_over_search'] = False

		tracks = self.jukebox.search('artist', 'Artist 1')
		self.assertEqual(3, len(tracks));

	def test_getPlaylist_consume(self):

		self.mpd._consume = True

		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]
		song3 = self.mpd.db[2]

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])
		self.jukebox.queue(song3['file'])

		playlist = self.jukebox.getPlaylist()
		log.info(playlist)

		self.assertEqual(3, len(playlist))
		self.assertEqual('Track 1', playlist[0].get('title'))

		self.jukebox.next()

		playlist = self.jukebox.getPlaylist()
		self.assertEqual(2, len(playlist))
		self.assertEqual('Track 2', playlist[0].get('title'))

	def test_getPlaylist_no_consume(self):

		self.mpd._consume = False

		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]
		song3 = self.mpd.db[2]

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])
		self.jukebox.queue(song3['file'])

		playlist = self.jukebox.getPlaylist()
		self.assertEqual(3, len(playlist))
		self.assertEqual('Track 1', playlist[0].get('title'))

		self.jukebox.next()

		playlist = self.jukebox.getPlaylist()
		self.assertEqual(2, len(playlist))
		self.assertEqual('Track 2', playlist[0].get('title'))

	def test_getGenres(self):

		genres = [x.name for x in self.jukebox.getGenres()]

		self.assertIn('Genre 1', genres)
		self.assertIn('Genre 5', genres)

	def test_getArtists(self):

		artists = [x.name for x in self.jukebox.getArtists()]

		self.assertIn('Artist 1', artists)
		self.assertIn('Artist 2', artists)
		self.assertIn('Artist 5', artists)

	def test_isPlaying(self):

		self.assertFalse(self.jukebox.isPlaying())
		self.jukebox.queue(self.mpd.db[0]['file'])
		self.assertTrue(self.jukebox.isPlaying())

	def test_getCurrentSong_consume(self):

		self.mpd._consume = True
		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])

		song = self.jukebox.getCurrentSong()
		self.assertEqual('Track 1', song.title)

		self.jukebox.next()
		song = self.jukebox.getCurrentSong()
		self.assertEqual('Track 2', song.title)

	def test_getCurrentSong_no_consume(self):

		self.mpd._consume = False
		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])

		song = self.jukebox.getCurrentSong()
		self.assertEqual('Track 1', song.title)

		self.jukebox.next()
		song = self.jukebox.getCurrentSong()
		self.assertEqual('Track 2', song.title)

	def test_getQueueLength(self):

		self.assertEqual(0, self.jukebox.getQueueLength())

		self.jukebox.queue(self.mpd.db[0]['file'])
		self.assertEqual(0, self.jukebox.getQueueLength())

		self.jukebox.queue(self.mpd.db[0]['file'])
		self.assertEqual(1, self.jukebox.getQueueLength())

		self.jukebox.queue(self.mpd.db[0]['file'])
		self.assertEqual(2, self.jukebox.getQueueLength())

	def test_remove(self):

		config['max_queue_length'] = 5

		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]
		song3 = self.mpd.db[2]
		song4 = self.mpd.db[2]
		song5 = self.mpd.db[2]

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])
		self.jukebox.queue(song3['file'])
		self.jukebox.queue(song4['file'])
		self.jukebox.queue(song5['file'])

		self.assertEqual(4, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song1, playlist[0])
		self.assertEqual(song2, playlist[1])
		self.assertEqual(song3, playlist[2])
		self.assertEqual(song4, playlist[3])
		self.assertEqual(song5, playlist[4])

		self.jukebox.remove(1)

		self.assertEqual(3, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song1, playlist[0])
		self.assertEqual(song3, playlist[1])

		self.jukebox.remove(0)

		self.assertEqual(2, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song3, playlist[0])

	def test_remove_consume(self):

		config['max_queue_length'] = 5
		self.mpd._consume = True

		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]
		song3 = self.mpd.db[2]
		song4 = self.mpd.db[2]
		song5 = self.mpd.db[2]

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])
		self.jukebox.queue(song3['file'])
		self.jukebox.queue(song4['file'])
		self.jukebox.queue(song5['file'])

		self.assertEqual(4, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song1, playlist[0])
		self.assertEqual(song2, playlist[1])
		self.assertEqual(song3, playlist[2])
		self.assertEqual(song4, playlist[3])
		self.assertEqual(song5, playlist[4])

		self.jukebox.next()
		self.jukebox.remove(1)

		self.assertEqual(2, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song2, playlist[0])
		self.assertEqual(song3, playlist[1])
		self.assertEqual(song5, playlist[2])

		self.jukebox.remove(0)

		self.assertEqual(1, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song5, playlist[0])

	def test_remove_no_consume(self):

		config['max_queue_length'] = 5
		self.mpd._consume = False

		song1 = self.mpd.db[0]
		song2 = self.mpd.db[1]
		song3 = self.mpd.db[2]
		song4 = self.mpd.db[2]
		song5 = self.mpd.db[2]

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song2['file'])
		self.jukebox.queue(song3['file'])
		self.jukebox.queue(song4['file'])
		self.jukebox.queue(song5['file'])

		self.assertEqual(4, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song1, playlist[0])
		self.assertEqual(song2, playlist[1])
		self.assertEqual(song3, playlist[2])
		self.assertEqual(song4, playlist[3])
		self.assertEqual(song5, playlist[4])

		self.jukebox.next()
		self.jukebox.remove(1)

		self.assertEqual(2, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song2, playlist[0])
		self.assertEqual(song3, playlist[1])
		self.assertEqual(song5, playlist[2])

		self.jukebox.remove(0)

		self.assertEqual(1, self.jukebox.getQueueLength())
		playlist = self.jukebox.getPlaylist()
		self.assertEqual(song5, playlist[0])

	def test_next_consume(self):

		song1 = self.mpd.db[0]
		self.mpd._consume = True

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song1['file'])

		self.assertEqual(2, self.jukebox.getQueueLength())

		self.jukebox.next()
		self.jukebox.next()

		self.assertEqual(0, self.jukebox.getQueueLength())

	def test_next_no_consume(self):

		song1 = self.mpd.db[0]
		self.mpd._consume = False

		self.assertEqual(0, len(self.jukebox.getPlaylist()))

		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song1['file'])
		self.jukebox.queue(song1['file'])

		self.assertEqual(2, self.jukebox.getQueueLength())

		self.jukebox.next()
		self.jukebox.next()

		self.assertEqual(0, self.jukebox.getQueueLength())

class TestTrack(unittest.TestCase):

	def setUp(self):

		self.mpd = FakeMPD()

	def test_trackNum(self):

		track = Track()
		track.load(self.mpd.db[0])
		assert track.track == 1

		track = Track()
		track.load(self.mpd.db[2])
		assert track.track == 2

		track = Track()
		track.load(self.mpd.db[3])
		assert track.track == 11

		track = Track()
		track.load(self.mpd.db[5])
		assert track.track == 55

class TestFakeMPD(unittest.TestCase):

	def setUp(self):

		self.mpd = FakeMPD()

	def test_consume(self):

		self.mpd._consume = True
		self.mpd.queue = [1,2,3]

		qlen = len(self.mpd.queue)
		self.mpd.next()

		self.assertEqual(qlen-1, len(self.mpd.queue))
		self.assertEqual(0, self.mpd._pos)

	def test_no_consume(self):

		self.mpd._consume = False
		self.mpd.queue = [1,2,3]

		qlen = len(self.mpd.queue)
		self.mpd.next()

		self.assertEqual(qlen, len(self.mpd.queue))
		self.assertEqual(1, self.mpd._pos)
