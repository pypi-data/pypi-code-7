# This package is used to cut the string which is having HTML tags.
# It does not count the HTML tags, it just count the string inside tags and
# keeps the tags as it is.

# ex: If the string is "welcome to <b>Python World</b> <br> Python is bla".
# And if we want to cut the string of 16 charaters then
# output will be "welcome to <b>Python</b>".

# Here while cutting the string it keeps the tags for the cutting string and
# skip the rest and without distorbing the div structure.

# USAGE1:
#  obj = HtmlCutString("welcome to <b>Python World</b> <br> Python is",16)
#  newCutString = obj.cut()

# USAGE2:
#  newCutString = cutHtmlString("welcome to <b>Python World</b> <br> Python is",16)

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString

class HtmlCutString(object):
	def __init__(self, string, limit, countType='c'):
		# Temparary node to parse the html tags in the string
		self.tempDiv = parseString('<div>' + string + '</div>')
		# while parsing text no of characters parsed
		self.count = 0
		self.countType = countType
		self.limit = limit

	def cut(self):
		impl = getDOMImplementation()
		newdoc = impl.createDocument(None, "some_tag", None)
		newDiv = newdoc.documentElement

		self.searchEnd(self.tempDiv, newDiv)
		# removeng some_tag that we added above
		newContent = newDiv.firstChild.toxml()
		# removing div tag that we added in the __init__
		return newContent[5:-6]

	def deleteChildren(self, node):
		while node.firstChild:
			self.deleteChildren(node.firstChild)
			node.removeChild(node.firstChild)

	def searchEnd(self, parseDiv, newParent):
		for element in parseDiv.childNodes:
			# not text node
			if element.nodeType != 3:
				newElement = element.cloneNode(True)
				newParent.appendChild(newElement)
				if len(element.childNodes) == 0:
					continue
				self.deleteChildren(newElement)
				res = self.searchEnd(element, newElement)
				if res:
					return res
				else:
					continue

			if self.countType == 'c':
				# the limit of the char count reached
				if len(element.nodeValue) + self.count >= self.limit:
					newElement = element.cloneNode(True)
					newElement.nodeValue = element.nodeValue[0:(self.limit - self.count)]
					newParent.appendChild(newElement)
					return True
			else:
				nodeValue_splitted = [i for i in element.nodeValue.split(' ') if i]
				# the limit of the word count reached
				if len(nodeValue_splitted) + self.count >= self.limit:
					newElement = element.cloneNode(True)
					start, end = 0, (self.limit - self.count)
					newElement.nodeValue = ' '.join(nodeValue_splitted[start:end])
					newParent.appendChild(newElement)
					return True

			newElement = element.cloneNode(True)
			newParent.appendChild(newElement)
			
			# counting characters
			if self.countType == 'c':
				self.count += len(element.nodeValue)
			# counting words
			else:
				self.count += len([i for i in element.nodeValue.split(' ') if i])

		return False

def cutHtmlString(string, limit, countType='c'):
	output = HtmlCutString(string, limit, countType)
	return output.cut()
