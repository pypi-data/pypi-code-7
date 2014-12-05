from subprocess import Popen, PIPE
from signal import SIGTERM
import os

def start_server(host, port, output=None, error=None):
    """
    Because of the way this function works, if it called, and you lose the object,
    or you don't call stop_server, the spawned process will become a zombie.
    """

    if output == None:
        output = open(os.devnull, "w")

    if error == None:
        error = open(os.devnull, "w")

    print "Starting nlgserv on %s:%s" % (host, port)
    server_instance = Popen([os.path.join(os.path.dirname(__file__),"jython.jar"),
                             os.path.join(os.path.dirname(__file__),"_server.py"),
                             host,
                             str(port)],
                            stdin=PIPE,
                            stdout=output,
                            stderr=error,
                            preexec_fn=os.setsid)
    
    return server_instance

def stop_server(server_instance):
    """
    This function kills the process group containing server_instance.

    This function is blocking, and will wait until the PG is dead before releasing
    control.
    """
    print "Shutting down nlgserv..."
    os.killpg(server_instance.pid, SIGTERM)
    server_instance.wait()
