def sanitize(time_string):
	"""格式化运动员运动时间计时格式"""
	if '-' in time_string:
		splitter = '-'
	elif ':' in time_string:
		splitter = ':'
	else:
		return(time_string)
	(mins,secs) = time_string.split(splitter)
	return(mins + '.' + secs)

class AthleteList(list):
	"""运动员信息类，继承自list列表"""
	def __init__(self, a_name,a_dob=None,a_times=[]):
		list.__init__([])
		self.name = a_name
		self.dob = a_dob
		self.extend(a_times)

	def top3(self):
		return(sorted(set([sanitize(t) for t in self]))[0:3])