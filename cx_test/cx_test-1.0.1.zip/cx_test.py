"""这是一个模块"""
def printList(theList):
	"""遍历列表"""
	for item in theList:
		if isinstance(item,list):
			print_lol(item)
		else:
			print(item)

def helloWorld():
	print("helloWorld")