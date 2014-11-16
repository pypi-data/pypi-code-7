import feedparser, sys

cric = feedparser.parse('http://static.cricinfo.com/rss/livescores.xml')
try:
    match = int(sys.argv[1])
except:
    pass

try:
    print [match],cric['entries'][match-1]['description']
except:
    for i in range(0,len(cric)):
        print [i+1], cric['entries'][i]['description']
