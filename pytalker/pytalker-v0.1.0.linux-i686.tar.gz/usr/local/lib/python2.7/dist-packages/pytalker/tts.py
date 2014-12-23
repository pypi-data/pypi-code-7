#!/usr/bin/python
# -*- coding: utf-8 -*-
#
##################################################################################
#
#	This software is part of pytalker. You can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################
import sys

# Required libraries: gst
# Installation on Debian:
#	sudo apt-get install python-gst0.10
import gobject
from urllib2 import Request, urlopen
try:
    import gst
except:
    print "The gst library seems not to be installed. Please, try under Debian the following command and try again:\n\tsudo apt-get install python-gst0.10"

class Pytalker():
    def on_finish(self, bus, message):
        """ 
		    Callback triggered at the end of the stream.
        """
        self.player.set_state(gst.STATE_NULL)
        self.mainloop.quit()
  
    def __init__(self):
        """ 
		    Constructor of the internal player.
        """
        self.player = None
        self.mainloop = gobject.MainLoop() #Instantiate the mainloop even if not used

    def say(self, text, lang="en",volume=5.0):
        """ 
            Downloading and playing a text.

            :param text:    Text to be played.
            :param lang:    Languague in two-letter ISO standard. Default: 'en'.
            :param volume:  Volume of the reproduction. Default: 5.0.
        """
        music_stream_uri = 'http://translate.google.com/translate_tts?'+'q='+text+'&tl='+lang+"&ie=UTF-8"
        self.player = gst.element_factory_make("playbin", "player") #Create the player
        self.player.set_property('uri', music_stream_uri) #Provide the source which is a stream
        self.player.set_property('volume',volume) #Val from 0.0 to 10 (float)
        self.player.set_state(gst.STATE_PLAYING) #Play

        bus = self.player.get_bus() #Get the bus (to send catch connect signals..)
        bus.add_signal_watch_full(1)
        bus.connect("message::eos", self.on_finish) #Connect end of stream to the callback
        self.mainloop.run() #Wait an event

    def sayNB(self, text, lang="en",volume=5.0): 
        """
            Downloading and playing a text in a Non Blocking way.

            :param text:    Text to be played.
            :param lang:    Languague in two-letter ISO standard. Default: 'en'.
            :param volume:  Volume of the reproduction. Default: 5.0.
        """
        music_stream_uri = 'http://translate.google.com/translate_tts?tl='+lang+'&q=' + text +"&ie=UTF-8"
        self.player = gst.element_factory_make("playbin", "player") #Create the player
        self.player.set_property('uri', music_stream_uri) #Provide the source which is a stream
        self.player.set_property('volume',volume) #Val from 0.0 to 10 (float)
        self.player.set_state(gst.STATE_PLAYING) #Play"""

    def download(self, text, lang="en", filename="tts.mp3"):
        """
            Downloading the pronunciation of a text onto a given file.

            :param text:    Text to be played.
            :param lang:    Languague in two-letter ISO standard. Default: 'en'.
            :param filenam:  A valid filename for the downloadable file. Default: 'tts.mp3'.
        """
        req = Request(url='http://translate.google.com/translate_tts')
        req.add_header('User-Agent', 'My agent !') #Needed otherwise return 403 Forbidden
        req.add_data("tl="+lang+"&q="+text+"&ie=UTF-8")
        fin = urlopen(req)
        mp3 = fin.read()

        with open(filename, "wb") as oF:
            oF.write(mp3)

    def play(self, audio_uri):
        """
            Tiny function to play any audio. This method is useful to play a sound locally.

            :param audio_uri:   Path to the file.
        """
        import pyglet

        sound = pyglet.resource.media(audio_uri)
        sound.play()

        pyglet.app.run()
    
    def setVolume(self, val):
        self.player.set_property('volume',val) #Val from 0 to 1 (float)
    
