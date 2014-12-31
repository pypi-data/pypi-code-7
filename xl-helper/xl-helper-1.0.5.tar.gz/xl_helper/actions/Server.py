import os
import shutil
import urllib2
from xl_helper.FileUtils import FileUtils
from subprocess import Popen, PIPE, STDOUT
from xl_helper.Utils import Utils
from string import join


class Server:

    @staticmethod
    def from_config(config, home):
        return Server(
            home=home,
            username=config.get('deployit', 'username'),
            password=config.get('deployit', 'password'),
            url="{protocol}://{host}:{port}/deployit/".format(
                protocol=config.get('deployit', 'protocol'),
                host=config.get('deployit', 'host'),
                port=config.get('deployit', 'port')
            )
        )

    def __init__(self, home, username, password, url):
        self.home = home
        self.username = username
        self.password = password
        self.url = url + '/' if url[-1] != '/' else url

    def is_stopped(self):
        return not self._ping()

    def is_running(self):
        return self._ping()

    def restart(self):
        self.stop()
        self.run()

    # Starts the server in different thread
    def start(self):
        import thread
        thread.start_new_thread(self.run, ())

    # Starts the server in different thread and waits for the response
    def start_and_wait(self):
        self.start()
        Utils.wait_until(self.is_running, tick=True)

    # Starts the server in the same thread
    def run(self):
        if self.is_stopped():

            if not os.path.isdir("{path}/repository".format(path=self.home)):
                print "Initializing XL Deploy with default configuration."
                config_path = FileUtils.to_absolute_path("xl_helper/resources/deployit.conf")
                print "It is taken from %s " % config_path
                shutil.copy(config_path, os.path.join(self.home, "conf"))
                p = Popen([self._get_run_script(), '-setup', '-reinitialize'], bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                p.stdin.write("yes\n")
                p.stdin.flush()
                p.communicate()

            os.system(self._get_run_script())
        else:
            print "Server is already started"

    def stop(self):
        if self.is_running():
            stop_url = self.url + 'server/shutdown'
            opener = Utils.auth_and_open_url(stop_url, 'POST', self.username, self.password)
            print "Stopping the server"
            urllib2.install_opener(opener)

    def stop_and_wait(self):
        self.stop()
        Utils.wait_until(self.is_stopped, tick=True)

    def _ping(self):
        try:
            ping_url = self.url + 'server/info'
            print "Pinging %s " % ping_url
            opener = Utils.auth_and_open_url(ping_url, 'GET', self.username, self.password)
            urllib2.install_opener(opener)
            return True
        except urllib2.URLError:
            return False

    def _get_run_script(self):
        server_sh = "%s/bin/server.sh" % self.home
        run_sh = "%s/bin/run.sh" % self.home
        candidates = [server_sh, run_sh]

        if os.path.isfile(server_sh):
            return server_sh
        elif os.path.isfile(run_sh):
            return run_sh
        else:
            raise Exception("Server cannot be started as start script hasn't been found. Considered candidates: %s" % join(candidates))

