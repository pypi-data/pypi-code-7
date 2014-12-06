def kill_process(proc):
	from os import system as cmd
	cmd("kill -9 " + proc)