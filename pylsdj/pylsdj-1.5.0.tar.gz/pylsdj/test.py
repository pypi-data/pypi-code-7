#!/usr/bin/env python

from pylsdj import SAVFile

sav = SAVFile("/Applications/LSDJ/Battery RAM/lsdj.sav")

synth = sav.projects[12].song.synths[2]

print synth.waves
print synth.waveform
print synth.start
print synth._params.waveform
