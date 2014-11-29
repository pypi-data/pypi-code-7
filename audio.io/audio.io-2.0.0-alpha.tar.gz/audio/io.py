#!/usr/bin/env python
# coding : utf-8

# Python 2.7 Standard Library
from __future__ import division
import atexit
import sys

# Digital Audio Coding
import audio.bitstream
import audio.wave

# Third-Party Libraries
import numpy as np
import pyaudio

_pyaudio = None

def init():
    global _pyaudio
    if _pyaudio is None:
        _pyaudio = pyaudio.PyAudio()

@atexit.register
def exit():
    if _pyaudio is not None:
        _pyaudio.terminate()

def play(data, df=44100, scale=None):
    df = int(df)

    # write-read round trip to normalize the data
    stream = audio.wave.write(data, df=df, scale=scale)
    data = audio.wave.read(stream, scale=False)
    assert data.dtype == np.int16 and len(np.shape(data)) == 2

    init()
    output = _pyaudio.open(format   = pyaudio.paInt16  ,
                           channels = np.shape(data)[0],
                           rate     = int(df)          ,
                           output   = True             )

    flat = np.ravel(data.T.newbyteorder())
    stream = audio.bitstream.BitStream(flat)
    raw = stream.read(bytes, len(stream) // 8)

    output.write(raw)
    output.stop_stream()
    output.close()

def record(duration=np.inf, stereo=True, df=44100, scale=None):
    df = int(df)
    num_channels = 1 + stereo

    init()
    input = _pyaudio.open(format   = pyaudio.paInt16,
                          channels = 1              ,
                          rate     = df             ,
                          input    = True           )

    try:
        num_samples = int(df * duration)
    except OverflowError:
        num_samples = np.inf

    raw_frames = []
    while num_samples:
        try:
            raw = input.read(min(num_samples, 882))
            raw_frames.append(raw)
            num_samples = num_samples - (len(raw) // 2)
        except KeyboardInterrupt:
            break
    raw = "".join(raw_frames)
    input.stop_stream()
    input.close()

    stream = audio.bitstream.BitStream(raw)
    data = stream.read(np.int16, len(raw) // 2).newbyteorder()
    data = np.reshape(data, (len(data) // num_channels, num_channels)).T

    # write-read round trip to normalize the data
    stream = audio.wave.write(data, df=df)
    data = audio.wave.read(stream, scale=scale)

    return data

