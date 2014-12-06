def kill_process(proc):
	import sys
	from os import system as cmd
	if sys.platform != "win32":
		cmd("kill -9 " + proc)
	else:
		cmd("taskkill /t /f /im " + proc)
