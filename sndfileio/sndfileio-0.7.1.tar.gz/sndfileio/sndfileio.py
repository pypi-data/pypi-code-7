"""
SNDFILE.IO

A simple module providing a unified API to read and write sound-files to and from
numpy arrays. If no extra modules are installed, it uses only standard modules
and numpy to read and write uncompressed formats (WAV, AIFF).

If other modules are installed (scikits.audiolab, for example), it uses that
and more formats are supported.

Advantages over the built-in modules wave and aifc

* support for PCM16, PCM24, PCM32 and FLOAT32
* unified output format, independent of encoding --> always float64
* unified API for all backends

API
===

sndinfo(path) --> return SndInfo, a namedtuple with all the information of the sound-file

Read & Write all samples
------------------------

sndread(path) --> it will read ALL the samples and return a Sample --a tuplet (data, samplerate)
                  | Data will always be as a numpy.float64, between -1 and 1,
                  | independently of bit-rate

sndwrite(samples, samplerate, outfile, encoding='auto')
              --> write the samples. samples need to be a numpy.float64 array with data between -1 and 1

Chunked IO
----------

sndread_chunked(path)  --> returns a generator yielding chunks of frames

sndwrite_chunked(path) --> opens the file for writing.
                           To write to the file, call .write
"""

from __future__ import division as _division
import os as _os
from collections import namedtuple as _namedtuple
import struct as _struct
import warnings as _warnings
import numpy as np
from .util import *
from numbers import Number as _Number

__all__ = [
    "sndread",
    "sndread_chunked",
    "sndinfo",
    "sndwrite",
    "bitdepth",
    "numchannels",
    "asmono",
    "getchannel"
]

Sample = _namedtuple("Sample", "samples sr")


########################
#
# SndInfo
#
########################

class SndInfo(_namedtuple("SndInfo", "samplerate nframes channels encoding fileformat")):
    @property
    def duration(self):
        return self.nframes / self.samplerate

    def __repr__(self):
        return """------------------
samplerate : %d
nframes    : %d
channels   : %d
encoding   : %s
fileformat : %s
duration   : %.3f s""" % (
            self.samplerate,
            self.nframes,
            self.channels,
            self.encoding,
            self.fileformat,
            self.duration
        )


class SndfileError(IOError):
    pass


#######################################
#
#             Utilities
#
########################################

def _chunks(start, end, step):
    pos = start
    last_full = end - step
    while pos < last_full:
        yield pos, step
        pos += step
    yield pos, end - pos


_DEFAULT_CHUNKSIZE = 512

    
########################################
#
#                API
#
########################################

def sndread(path):
    """
    read a soundfile as a numpy array. returns (data, sr)
    """
    backend = _get_backend(path)
    return backend.read(path)


def sndread_chunked(path, frames=_DEFAULT_CHUNKSIZE):
    """
    returns a generator yielding numpy arrays (float64) of at most `frames` frames
    """
    backend = _get_backend(path, key=lambda backend: backend.can_read_in_chunks)
    if backend:
        return backend.read_chunked(path, frames)
    else:
        raise SndfileError("chunked reading is not supported by the available backends")


def sndinfo(path):
    """
    Get info about a soundfile

    path (str): the path to a soundfile

    RETURNS --> a namedtuple containing samplerate, nframes, channels, encoding, fileformat
    """
    backend = _get_backend(path)
    return backend.getinfo(path)


def sndwrite(samples, sr, outfile, encoding='auto', normalize_if_would_clip=True):
    """
    samples  --> array-like. the actual samples, shape=(nframes, channels)
    sr       --> sampling-rate
    outfile  --> the name of the outfile. the extension will determine the file-format
                 The formats supported depend on the available backends
                 Without additional backends, only uncompressed formats
                 are supported (wav, aif)
    encoding --> one of: 
                 - 'auto' or None: the encoding is determined from the format
                                   given by the extension of outfile, and
                                   from the data
                 - 'pcm16'
                 - 'pcm24'
                 - 'pcm32'
                 - 'flt32'

                 NB: not all file formats support all encodings.
                     Throws a SndfileError if the format does not support
                     the given encoding

                 If set to 'auto', an encoding will be selected based on the 
                 file-format and on the data. The bitdepth of the data is measured,
                 and if the file-format supports it, it will be used. For bitdepths
                 of 8, 16 and 24 bits, a PCM encoding will be used. For a bitdepth
                 of 32 bits, a FLOAT encoding will be used if supported, or the next
                 lower supported encoding (for flac file-format, 24 bit encoding will
                 be used. If the data would clip, it is first normalized)
    """
    if encoding == 'auto':
        encoding = _guess_encoding(samples, outfile)
    # normalize in the case where there would be clipping
    if encoding.startswith('pcm') and ((samples > 1).any() or (samples < -1).any()):
        maxvalue = max(samples.max(), abs(samples.min()))
        samples = samples / maxvalue
    backend = _get_write_backend(outfile, encoding)
    if not backend:
        raise SndfileError("No backend found to support the given format and encoding")
    return backend.write(samples, sr, outfile, encoding)


def asmono(samples, mixdown=False):
    """
    convert samples to mono if they are not mono already.

    The returned array will always have the shape (numframes,)

    If mixdown is True, channels are mixed to one channel
    Otherwise, the first channel is returned.
    """
    if numchannels(samples) == 1:
        # it could be [1,2,3,4,...], or [[1], [2], [3], [4], ...]
        if isinstance(samples[0], _Number):
            return samples
        elif isinstance(samples[0], np.dnarray):
            return np.reshape(samples, (len(samples),))
        else:
            raise TypeError("Samples should be numeric, found: %s" % str(type(samples[0])))
    if not mixdown:
        return samples[:, 0]
    else:
        return _mix(samples, scale_by_numchannels=True)


def getchannel(samples, ch):
    """
    Returns a view into a channel of samples.

    samples    : a numpy array representing the audio data
    ch         : the channel to extract (channels begin with 0)
    """
    N = numchannels(samples)
    if ch > (N - 1):
        raise ValueError("channel %d out of range" % ch)
    if N == 1 and ch == 0:
        return samples
    return samples[:, ch]


def bitdepth(data, snap=True):
    """
    returns the number of bits actually used to represent the data.

    data: a numpy.array (mono or multi-channel)
    snap: snap to 8, 16, 24 or 32 bits.
    """
    data = asmono(data)
    maxitems = min(4096, data.shape[0])
    maxbits = max(x.as_integer_ratio()[1] for x in data[:maxitems]).bit_length()
    if snap:
        if maxbits <= 8:
            maxbits = 8
        elif maxbits <= 16:
            maxbits = 16
        elif maxbits <= 24:
            maxbits = 24
        elif maxbits <= 32:
            maxbits = 32
        elif maxbits <= 64:
            maxbits = 64
        else:
            raise ValueError("bitdepth too high!: %d" % maxbits)
    return maxbits
    
        
############################################
#
#                BACKENDS
#
############################################

class _Audiolab(object):
    priority = 1
    supported_filetypes = ".aif .aiff .wav .flac .ogg .wav64 .caf .raw".split()
    supported_filetypes_write = ".aif .aiff .wav .flac .ogg .wav64 .caf .raw".split()
    encodings = 'pcm16 pcm24 flt32'.split()
    can_read_in_chunks = True
    backend = None
    backend_name = 'scikits.audiolab'

    @classmethod
    def get_backend(cls):
        if cls.backend is not None:
            return cls.backend
        try:
            from scikits import audiolab
            cls.backend = audiolab
            return cls.backend
        except ImportError:
            return None

    @classmethod
    def is_available(cls):
        backend = cls.get_backend()
        if backend:
            return True
        return False

    @classmethod
    def read(cls, path):
        audiolab = cls.get_backend()
        snd = audiolab.Sndfile(path)
        data = snd.read_frames(snd.nframes)
        sr = snd.samplerate
        return Sample(data, sr)

    @classmethod
    def read_chunked(cls, path, frames=_DEFAULT_CHUNKSIZE):
        audiolab = cls.get_backend()
        snd = audiolab.Sndfile(path)
        if with_position:
            for pos, nframes in _chunks(0, snd.nframes, frames):
                yield snd.read_frames(nframes), pos
        else:
            for pos, nframes in _chunks(snd.nframes):
                yield snd.read_frames(nframes)

    @classmethod
    def getinfo(cls, path):
        audiolab = cls.get_backend()
        snd = audiolab.Sndfile(path)
        return SndInfo(
            snd.samplerate, snd.nframes, snd.channels, snd.encoding, snd.file_format
        )

    @classmethod
    def write(cls, data, sr, outfile, encoding):
        if encoding not in cls.encodings:
            raise ValueError("correct")
        ext = _os.path.splitext(outfile)[1].lower()
        if not ext in cls.supported_filetypes:
            raise ValueError(
                "The given format (%s) is not supported by the %s backend" % 
                (ext, cls.backend_name)
            )
        format = cls._get_sndfile_format(ext, encoding)
        audiolab = cls.get_backend()
        snd = audiolab.Sndfile(
            outfile, mode='w', format=format, channels=numchannels(data), samplerate=sr)
        snd.write_frames(data)
        snd.close()

    @classmethod
    def _get_sndfile_format(cls, extension, encoding):
        assert extension in cls.supported_filetypes
        def _parse_encoding(encoding):
            # format --> pcm, flt  | bits --> 16, 24, 32, etc.
            format, bits = encoding[:3], int(encoding[3:])
            assert (format in ('pcm, flt')) and (bits in (8, 16, 24, 32))
            return format, bits
        format, bits = _parse_encoding(encoding)
        extension = extension[1:]
        if extension == 'aif':
            extension = 'aiff'
        format = "%s%d" % (
            {'pcm': 'pcm', 'flt': 'float'}[format],
            bits
        )
        audiolab = cls.get_backend()
        return audiolab.Format(extension, format)
    

class _Builtin(object):
    priority = 100
    supported_filetypes = (".wav", ".aif", ".aiff")
    supported_filetypes_write = []
    can_read_in_chunks = True
    backend_name = 'builtin'

    @staticmethod
    def is_available():
        return True

    @staticmethod
    def read(path):
        ext = _os.path.splitext(path)[1].lower()
        if ext in (".aif", ".aiff"):
            return _AiffReader(path).read()
        elif ext == ".wav":
            return _WavReader(path).read()
        else:
            raise ValueError("format not supported")

    @staticmethod
    def getinfo(path):
        ext = _os.path.splitext(path)[1].lower()
        if ext in (".aif", ".aiff"):
            return _AiffReader(path).info
        elif ext == ".wav":
            return _WavReader(path).info

    @staticmethod
    def read_chunked(path, frames=_DEFAULT_CHUNKSIZE):
        ext = _os.path.splitext(path)[1].lower()
        if ext == '.wav':
            return _WavReader(path).read_chunked(path, frames)
        else:
            raise NotImplementedError("read_chunked not implemented for the given format")


_BACKENDS = [_Builtin, _Audiolab]
    

###########################################
#
#             IMPLEMENTATION
#
###########################################

class _WavReader(object):
    def __init__(self, path):
        self.path = path
        fsize, self._big_endian = _wav_read_riff_chunk(open(path))
        self._info = None

    def getinfo(self):
        if self._info is not None:
            return self._info
        self._info = _wav_getinfo(self.path)
        return self._info

    def read(self):
        sample, info = _wav_read(self.path)
        self._info = info
        return sample

    def read_chunked(self, frames=_DEFAULT_CHUNKSIZE):
        return _wav_read_chunked(self.path, frames)


class _AiffReader(object):
    def __init__(self, path):
        self.path = path
        self._info = None

    def getinfo(self):
        if self._info is not None:
            return self._info
        self._info = _aiff_getinfo(self.path)
        return self._info

    def read(self):
        sample, info = _aiff_read(self.path)
        self._info = info
        return sample

                      
def _aiff_getinfo(path):
    import aifc
    f = aifc.open(path)
    bytes = f.getsampwidth()
    if bytes == 4:
        raise IOError("32 bit aiff is not supported yet!")
    encoding = "pcm%d" % (bytes * 8)
    return SndInfo(f.getframerate(), f.getnframes(), f.getnchannels(), encoding, "aiff")


def _aiff_read(path):
    import aifc
    f = aifc.open(path)
    datastr = f.readframes(f.getnframes())
    bytes = f.getsampwidth()
    channels = f.getnchannels()
    encoding = "pcm%d" % (bytes * 8)
    if encoding == 'pcm8':
        data = (np.fromstring(datastr, dtype=np.int8) / (2.0 ** 7)).astype(float)
    elif encoding == 'pcm16':
        data = (np.fromstring(datastr, dtype=">i2") / (2.0 ** 15)).astype(float)
    elif encoding == 'pcm24':
        data = np.fromstring(datastr, dtype=np.ubyte)
        data = _numpy_24bit_to_32bit(data, bigendian=True).astype(float) / (2.0 ** 31)
    elif encoding == 'pcm32':
        data = (np.fromstring(datastr, dtype=">i4") / (2.0 ** 31)).astype(float)
    if channels > 1:
        data = data.reshape(-1, channels)
    info = SndInfo(f.getframerate(), f.getnframes(), f.getnchannels(), encoding, "aiff")
    return Sample(data, info.samplerate), info
        

def _wav_read_riff_chunk(fid):
    big_endian = False
    asbytes = str
    str1 = fid.read(4)
    if str1 == asbytes('RIFX'):
        big_endian = True
    elif str1 != asbytes('RIFF'):
        raise ValueError("Not a WAV file.")
    if big_endian:
        fmt = '>I'
    else:
        fmt = '<I'
    fsize = _struct.unpack(fmt, fid.read(4))[0] + 8
    str2 = fid.read(4)
    if (str2 != asbytes('WAVE')):
        raise ValueError("Not a WAV file.")
    if str1 == asbytes('RIFX'):
        big_endian = True
    return fsize, big_endian


def _wav_read_fmt_chunk(f, big_endian):
    fmt = ">" if big_endian else "<"
    res = _struct.unpack(fmt + 'ihHIIHH', f.read(20))
    chunksize, format, ch, sr, brate, ba, bits = res
    formatstr = {
        1: 'pcm',
        3: 'flt',
        6: 'alw',
        7: 'mlw',
        -2: 'ext'     # extensible
    }.get(format)
    if formatstr is None:
        raise SndfileError("could not understand format while reading wav file")
    if formatstr == 'ext':
        raise SndfileError("extension formats are not supported yet")
    if chunksize > 16:
        f.read(chunksize - 16)
    return chunksize, formatstr, ch, sr, brate, ba, bits


def _wav_read_data(fid, size, channels, encoding, big_endian):
    """
    adapted from scipy.io.wavfile._read_data_chunk

    assume we are at the data (after having read the size)
    """
    bits = int(encoding[3:])
    if bits == 8:
        data = np.fromfile(fid, dtype=np.ubyte, count=size)
        if channels > 1:
            data = data.reshape(-1, channels)
    else:
        bytes = bits // 8
        if encoding in ('pcm16', 'pcm32', 'pcm64'):
            if big_endian:
                dtype = '>i%d' % bytes
            else:
                dtype = '<i%d' % bytes
            data = np.fromfile(fid, dtype=dtype, count=size // bytes)
            if channels > 1:
                data = data.reshape(-1, channels)
        elif encoding[:3] == 'flt':
            print "flt32!"
            if bits == 32:
                if big_endian:
                    dtype = '>f4'
                else:
                    dtype = '<f4'
            else:
                raise NotImplementedError
            data = np.fromfile(fid, dtype=dtype, count=size // bytes)
            if channels > 1:
                data = data.reshape(-1, channels)
        elif encoding == 'pcm24':
            # this conversion approach is really bad for long files
            # TODO: do the same but in chunks
            data = _numpy_24bit_to_32bit(np.fromfile(fid, dtype=np.ubyte, count=size), bigendian=False)
            if channels > 1:
                data = data.reshape(-1, channels)
    return data


def _wav_read(path, convert_to_float=True):
    f = open(path, 'rb')
    info, fsize, big_endian, datasize = _wav_getinfo(f, extended=True)
    asbytes = str
    fmt = ">i" if big_endian else "<i"
    bits = int(info.encoding[3:])
    data = _wav_read_data(f, datasize, info.channels, info.encoding, big_endian)
    f.close()
    if convert_to_float:
        data = _floatize(data, info.encoding).astype(float)
    return Sample(data, info.samplerate), info


def _wav_read_chunked(path, frames=100, convert_to_float=True):
    f = open(path, 'rb')
    info, fsize, big_endian, datasize = _wav_getinfo(f, extended=True)
    if info.encoding == 'flt32':
        raise NotImplementedError("float-32 is not correctly implemented, aborting!")
    asbytes = str
    fmt = ">i" if big_endian else "<i"
    bits = int(info.encoding[3:])
    bytes = bits // 8
    chunksize = bytes * info.channels * frames
    if bits == 8:
        raise NotImplementedError("8 bit .wav is not supported")
    else:
        if big_endian:
            dtype = '>i%d' % bytes
        else:
            dtype = '<i%d' % bytes
        for _, chunk in _chunks(0, chunksize, datasize):
            data = np.fromfile(f, dtype=dtype, count=chunk // bytes)
            if info.channels > 1:
                data = data.reshape(-1, info.channels)
            if convert_to_float:
                data = _floatize(data, info.encoding)
            yield data
    f.close()


def _wav_getinfo(f, extended=False):
    """
    read the info of a wav file. taken mostly from scipy.io.wavfile

    if extended: returns also fsize and big_endian
    """
    if isinstance(f, basestring):
        f = open(f, 'rb')
        needsclosing = True
    else:
        needsclosing = False
    fsize, big_endian = _wav_read_riff_chunk(f)
    if big_endian:
        fmt = ">i"
    else:
        fmt = "<i"
    while (f.tell() < fsize):
        chunk_id = f.read(4)
        if chunk_id == 'fmt ':
            chunksize, sampleformat, channels, samplerate, byterate, block_align, bits = _wav_read_fmt_chunk(f, big_endian)
        elif chunk_id == 'data':
            datasize = _struct.unpack(fmt, f.read(4))[0]
            # size = numsamples * NumChannels * BitsPerSample/8
            nframes = int(datasize / (channels * (bits / 8)))
            break
        else:
            _warnings.warn("chunk not understood: %s" % chunk_id)
            data = f.read(4)
            size = _struct.unpack(fmt, data)[0]
            f.seek(size, 1)
    encoding = _encoding(sampleformat, bits)
    if needsclosing:
        f.close() 
    info = SndInfo(samplerate, nframes, channels, encoding, "wav")    
    if extended:
        return info, fsize, big_endian, datasize
    return info

        
#   HELPERS
    

def _floatize(data, encoding):
    assert (data > 0).any()
    if encoding == 'flt32':
        return data
    elif encoding == 'pcm24':
        return data / (2.0 ** 31)
    elif encoding == 'pcm16':
        return data / (2.0 ** 15)
    else:
        raise ValueError("encoding not understood")


def _encoding(format, bits):
    """
    format, bits as returned by _wav_read_fmt_chunk

    format: "pcm", "float"
    bits  : 16, 24, 32
    """
    return "%s%d" % (format, bits)


def _numpy_24bit_to_32bit(data, bigendian=False):
    """
    data is a ubyte array of shape = (size,) 
    (interleaved channels if multichannel)
    """
    target = np.zeros((data.shape[0] * 4 / 3,), dtype=np.ubyte)
    if not bigendian:
        target[3::4] = data[2::3]
        target[2::4] = data[1::3]
        target[1::4] = data[0::3]
    else:
        target[1::4] = data[2::3]
        target[2::4] = data[1::3]
        target[3::4] = data[0::3]
    del data
    targetraw = target.tostring()
    del target
    data = np.fromstring(targetraw, dtype=np.int32)
    return data


def _available_backends():
    return [b for b in _BACKENDS if b.is_available()]
  

def _get_backend(path=None, key=None):
    """
    ext: a string like .aiff. If given, only backends supporting 
         the given filetype are returned
    key: a function (backend -> bool) signaling if the backend 
         is suitable for a specific task

    example
    =======

    # Get available backends which can read in chunks
    >>> backend = _get_backend('file.flac', key=lambda backend:backend.can_read_in_chunks)
    """
    if path:
        ext = _os.path.splitext(path)[1].lower()
    else:
        ext = None
    backends = _available_backends()
    if key:
        backends = [b for b in backends if key(b)]
    if ext:
        backends = [backend for backend in backends if ext in backend.supported_filetypes]
    if backends:
        best = sorted(backends, key=lambda backend: backend.priority)[0]
        return best
    return None


def _get_write_backend(outfile, encoding, key=None):
    backends = _available_backends()
    if not backends:
        raise SndfileError("No available backends for writing")
    ext = _os.path.splitext(outfile)[1].lower()
    if ext:
        backends = [b for b in backends if ext in b.supported_filetypes_write]
    if key:
        backends = [b for b in backends if key(b)]
    if backends:
        best = sorted(backends, key=lambda backend: backend.priority)[0]
        return best
    return None


def _mix(samples, scale_by_numchannels=True):
    summed = samples.sum(0)
    if scale_by_numchannels:
        summed *= (1 / numchannels(samples))
    return summed


def _guess_encoding(data, outfile):
    ext = _os.path.splitext(outfile)[1].lower()
    maxbits = bitdepth(data, snap=True)
    if ext in ('.wav', '.aif', '.aiff'):
        encoding = {
            16: 'pcm16',
            24: 'pcm24',
            32: 'flt32'
        }.get(maxbits)
    elif ext == ".flac":
        encoding = {
            16: 'pcm16',
            24: 'pcm24',
            32: 'pcm24'
        }.get(maxbits)
    else:
        encoding = 'pcm24'
    return encoding


def _compare_read(path):
    s0 = _Audiolab.read(path)
    s1 = _Builtin.read(path)
    return s0, s1


def _testfile_builtin(path):
    s0, s1 = _compare_read(path)
    return (s0[0] == s1[0]).all()



