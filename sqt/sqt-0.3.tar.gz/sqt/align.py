from __future__ import print_function, division, absolute_import
try:
	from sqt._helpers import globalalign
except ImportError:
	import warnings
	warnings.warn("C module for speedups unavailable", ImportWarning)


class GlobalAlignment:
	"""A global alignment between two strings"""

	def __init__(self, s, t, semiglobal=False):
		if type(s) is str:
			s = s.encode('ascii')
		if type(t) is str:
			t = t.encode('ascii')
		flags = 15 if semiglobal else 0  # TODO this constant shouldn't be here
		(row1, row2, start1, stop1, start2, stop2, errors) = globalalign(s, t, flags)
		assert semiglobal or start1 == start2 == 0
		assert semiglobal or stop1 == len(s)
		assert semiglobal or stop2 == len(t)
		assert len(row1) == len(row2)
		self.row1 = row1.decode('ascii')
		self.row2 = row2.decode('ascii')
		self.start1 = start1
		self.stop1 = stop1
		self.start2 = start2
		self.stop2 = stop2
		self.errors = errors
		# Overlap start and stop in alignment coordinates.
		# row1[overlap_start:overlap_stop] is the overlapping alignment.
		self.overlap_start = max(start1, start2)
		self.overlap_stop = len(row1) - max(len(s) - stop1, len(t) - stop2)

	def _replace_gaps(self, row, gap_char):
		start = self.overlap_start
		stop = self.overlap_stop
		front = row[:start].replace('\0', ' ')
		middle = row[start:stop].replace('\0', gap_char)
		end = row[stop:].replace('\0', ' ')
		return front + middle + end

	def print(self, width=100, gap_char='-'):
		"""multi-line output and parameters, therefore not called __str__"""
		row1 = self._replace_gaps(self.row1, gap_char)
		row2 = self._replace_gaps(self.row2, gap_char)
		for i in range(0, len(row1), width):
			top = row1[i:i+width]
			bottom = row2[i:i+width]
			m = []
			for c, d in zip(top, bottom):
				if c == d:
					m.append('|')
				elif c == ' ' or d == ' ':
					m.append(' ')
				else:
					m.append('X')
			middle = ''.join(m)
			if i > 0:
				print()
			print(top)
			print(middle)
			print(bottom)

	def __str__(self):
		return 'GA(row1={}, row2={}, errors={})'.format(
			self.row1, self.row2, self.errors)


def edit_distance(s, t):
	"""
	Return the edit distance between the strings s and t.
	The edit distance is the sum of the numbers of insertions, deletions,
	and mismatches that is minimally necessary to transform one string
	into the other.
	"""
	m = len(s) # index: i
	n = len(t) # index: j

	# dynamic programming "table" (just a single column)
	# note that using an array('h', ...) here is not faster
	costs = list(range(m+1))

	# calculate alignment (using unit costs)
	prev = 0
	for j in range(1, n+1):
		prev = costs[0]
		costs[0] += 1
		for i in range(1, m+1):
			c = min(
				prev + int(s[i-1] != t[j-1]),
				costs[i] + 1,
				costs[i-1] + 1)
			prev = costs[i]
			costs[i] = c
	return costs[-1]


try:
	from sqt._helpers import edit_distance
except:
	pass
