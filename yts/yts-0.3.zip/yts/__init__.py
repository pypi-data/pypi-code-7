import requests
import webbrowser
import pprint
from rawyify import RawYTS


#YTS class deals with listing of 
class YTS:
	def __init__(self,username=None,password=None):
		self.username = username
		self.password = password
		self.ryts = RawYTS()
		if self.username != None:
			self.login(username,password)


	def login(self,username,password):
		url = 'https://yts.re/api/login.json'
		res = requests.get(url,params={'username':username,'password':password})
		dic = res.json()
		self.hash = dic['hash']
		self.uid = dic['userID']


	#Prints torrents on to the screen.Only should be used by other functions of class
	def print_torrents(self,dic):
		for i in dic['MovieList']:
			print '==============================================================\n'
			print '\t',i['MovieTitle'],'{movie ID: ',i['MovieID'],'}'
			print '\t','Rating: ',i['MovieRating']
			print '\t','Release Year: ',i['MovieYear']
			print '\t','Quality: ',i['Quality']
			print '\t','Size: ',i['Size']
			print '\t','Uploaded Date: ',i['DateUploaded']
			print '==============================================================\n'

	#Fetches torrents as per keyword arguments specified
	def torrents(self,limit=20,page=1,quality='ALL',rating=0,genre='ALL',sort='date'):
		url = 'https://yts.re/api/list.json'
		payload = {'limit':limit,'set':page,'quality':quality,'rating':rating,'genre':genre,'sort':sort}
		res = requests.get(url,params=payload)
		dic = res.json()
		self.print_torrents(dic)
	
	def comment(self,id,text):
		if self.username:
			url = 'https://yts.re/api/commentpost.json'
			params = {'hash':self.hash,'movieid':id,'text':text}
			res = requests.post(url,data=params)
			print 'Posted comment successfully'
		else:
			print 'Please login to post comment!'

	def request(self,movie):
		if self.username:
			url = 'https://yts.re/api/makerequest.json'
			params = {'hash':self.hash,'request':movie}
			res = requests.post(url,data=params)
			print 'Requested movie successfully'
		else:
			print 'Please login to request a movie!'


	#Fetches top 20 latest movie torrents from web
	def latest(self):
		url = 'https://yts.re/api/list.json'
		res = requests.get(url)
		dic = res.json()
		self.print_torrents(dic)

	def upcoming(self):
		url = 'https://yts.re/api/upcoming.json'
		res = requests.get(url)
		dic = res.json()
		for i in dic:
			print '%s  by \t%s\n'%(i['MovieTitle'],i['Uploader'])

	def download(self,id):
		url = 'https://yts.re/api/movie.json'
		res = requests.get(url,params={'id':id})
		dic = res.json()
		webbrowser.open(dic['TorrentMagnetUrl'])

	def search(self,movie):
		url = 'https://yts.re/api/list.json'
		res = requests.get(url,params={'keywords':movie})
		dic = res.json()
		self.print_torrents(dic)

	def requests_confirmed(self):
		url = 'https://yts.re/api/requests.json'
		res = requests.get(url,params={'page':'confirmed'})
		dic = res.json()
		for i in dic['RequestList']:
			print i['Username'],':\t',i['MovieTitle'].encode('utf-8')

	def raw_upcoming(self):
		return self.ryts.raw_upcoming()

	def raw_torrents(self,limit=20,page=1,quality='ALL',rating=0,genre='ALL',sort='date'):
		return self.ryts.raw_torrents(limit=limit,page=page,quality=quality,rating=rating,genre=genre,sort=sort)

	def raw_latest(self):
		return self.ryts.raw_latest()

	def raw_search(self,movie):
		return self.ryts.raw_search(movie)

	def raw_requests_confirmed(self):
		return self.ryts.raw_requests_confirmed()




#Movie class that has lot of meta information like cast,rating etc
class Movie:
	def __init__(self,id):
		self.id = id
		self.url = 'https://yts.re/api/movie.json'
		self.res =  requests.get(self.url,params={'id':self.id})
		self.dic = self.res.json()

	def print_torrents(self,dic):
		for i in dic['MovieList']:
			print '==============================================================\n'
			print '\t',i['MovieTitle'],'{movie ID: ',i['MovieID'],'}'
			print '\t','Rating: ',i['MovieRating']
			print '\t','Release Year: ',i['MovieYear']
			print '\t','Quality: ',i['Quality']
			print '\t','Size: ',i['Size']
			print '\t','Uploaded Date: ',i['DateUploaded']
			print '==============================================================\n'

	def movie(self):
		self.print_torrents({'MovieList':[self.dic]})

	def imdb(self):
		webbrowser.open(self.dic['ImdbLink'])

	def trailer(self):
		webbrowser.open(self.dic['YoutubeTrailerUrl'])

	def seeds(self):
		return self.dic['TorrentSeeds']

	def cast(self):
		print '*************Cast Overview*****************'
		for i in self.dic['CastList']:
			print 'actor: ',i['ActorName'],'\t role: ',i['CharacterName']

	def genres(self):
		return [self.dic[i] for i in self.dic.keys() if 'Genre' in i]

	def description(self):
		print self.dic['LongDescription']

	def download(self):
		webbrowser.open(self.dic['TorrentMagnetUrl'])

	def raw_movie(self):
		return self.dic


#m = Movie(6581)
#m.seeds()

#y = YTS()

#y.request('home alone')

#y.torrents(limit=50,page=2,quality='720p',movie='matrix')
#y.search('matrix')
#webbrowser.open(y.torrents()['MovieList'][0]['TorrentMagnetUrl'])