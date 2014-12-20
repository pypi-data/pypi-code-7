import requests 

class RawYTS:
	def __init__(self):
		pass

	def raw_upcoming(self):
		url = 'https://yts.re/api/upcoming.json'
		res = requests.get(url)
		dic = res.json()
		return dic

	def raw_torrents(self,limit=20,page=1,quality='ALL',rating=0,genre='ALL',sort='date'):
		url = 'https://yts.re/api/list.json'
		payload = {'limit':limit,'set':page,'quality':quality,'rating':rating,'genre':genre,'sort':sort}
		res = requests.get(url,params=payload)
		dic = res.json()
		return dic

	def raw_latest(self):
		url = 'https://yts.re/api/list.json'
		res = requests.get(url)
		dic = res.json()
		return dic

	def raw_search(self,movie):
		url = 'https://yts.re/api/list.json'
		res = requests.get(url,params={'keywords':movie})
		dic = res.json()
		return dic

	def raw_requests_confirmed(self):
		url = 'https://yts.re/api/requests.json'
		res = requests.get(url,params={'page':'confirmed'})
		dic = res.json()
		return dic




