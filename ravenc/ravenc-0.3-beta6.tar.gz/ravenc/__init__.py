"""
This is the Baserip package.

The alkali version of acidrip, a desktop utility to make ripping DVDs easy.
"""

__name = 'ravenc'
__version = '0.3-beta6'
__description = 'DVD Ripper and File Transcoder.'
_version = __version
__readme = """Ravenc is a tool for copying a single video title from a DVD whilst 
transcoding it. The purpose of this is to make the video available 
to devices you may have which do not have a DVD player.

Altenatively you can transcode multimedia files on your filesystem.

Ravenc is designed to work with a clean DVD source like the ones you get 
on bought DVD disks.
Ravenc was created because Acidrip is no longer being maintained 
and I found myself needing a DVD ripper. 

The design of Ravenc was heavily influenced by Acidrip but has now 
significantly changed.
Ravenc is, in fact, a simple front-end to avlib/avconv which is 
itself a front-end to some video encoding and decoding libraries. Everything 
that Ravenc does can be achieved from the command line, Ravenc just 
simplifies the process."""
