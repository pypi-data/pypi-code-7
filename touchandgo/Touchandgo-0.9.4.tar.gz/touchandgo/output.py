from os import system
from time import sleep

from touchandgo.helpers import get_interface


class Output(object):
    def __init__(self, stream_url, sub_file=None, parent=None):
        self.stream_url = stream_url
        self.sub_file = sub_file
        self.parent = parent

    def run(self):
        player_command = self._player()
        if self.sub_file is not None:
            subs = self._subs()
        else:
            subs = ""

        command = "%s %s" % (player_command, subs)
        system(command)

    def _player(self):
        return ""

    def _subs(self):
        return ""


class VLCOutput(Output):
    def _player(self):
        return "vlc %s -q" % self.stream_url

    def _subs(self):
        subs = "--sub-file %s" % self.sub_file
        return subs


class OMXOutput(Output):
    def _player(self):
        return "omxplayer --live --timeout 360 -p -o hdmi %s" \
            % self.stream_url

    def _subs(self):
        subs = "--subtitle %s" % self.sub_file
        return subs

class CastOutput(Output):
    def run(self):
        import pychromecast
        from pychromecast.controllers.media import MediaController

        self.chromecast = pychromecast.get_chromecast()
        interface = get_interface()
        guess = {"mimetype": "video/mp4"} #self.parent.guess(self.parent.get_video_path())

        class Controller(MediaController):
            def receive_message(self, message, data):
                print message, data
                return True

        handler = Controller()
        self.chromecast.register_handler(handler)
        handler.play_media("http://%s:%s" % (interface, 8888), #self.parent.port),
                                   guess['mimetype'])
        while True:
            print("Media status", self.chromecast.media_controller._status_listeners)
            sleep(1)


    def __del__(self):
        self.chromecast.media_controller.stop()


if __name__ == "__main__":
    from logger import log_setup
    log_setup(True)
    CastOutput("http://localhost:8080", None, None).run()
