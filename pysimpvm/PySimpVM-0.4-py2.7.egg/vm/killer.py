def kill_process(proc):
	import sys
	from os import system as cmd
	if sys.platform != "win32":
		cmd("kill -9 " + proc)
	else:
		from warnings import error
		error("error: kill_process not supported on windows")
		return
