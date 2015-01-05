# -*- coding: utf-8 -*-
import requests
import re

class monarchhd():
    """Connect and control Matrox Monarch HD"""

    BASE_URL = 'http://%s/Monarch/syncconnect/sdk.aspx?command=%s'

    def __init__(self, ipAddress, username='admin', password='admin'):
        """Instance a new Matrox Controller"""
        self.ipAddress = ipAddress
        self.username = username
        self.password = password

    def __doQuery(self, command):
        """Send a request to the Matrox"""

        url = self.BASE_URL % (self.ipAddress, command)
        if self.username:
            r = requests.get(url, auth=(self.username, self.password))
            return r.content

        r = requests.get(url)
        return r.content

    ### STATUS ###

    def getStatus(self):
        """Used to acquire the current stream and record status of a Monarch HD device."""
        result = self.__doQuery('GetStatus')

        # RECORD: <state>, STREAM:<mode>,<state>, NAME:<devicename>
        p = re.compile(u'RECORD:(?P<record_state>[A-Z]+),STREAM:(?P<stream_mode>[A-Z]+),(?P<stream_state>[A-Z]+),NAME:(?P<device_name>.+)$', re.IGNORECASE)
        s = re.search(p, result)
        if s:
            return {'RESULT': 'SUCCESS', 'RECORD': {'STATE': s.group('record_state')},
                    'STREAM': {'MODE': s.group('stream_mode'), 'STATE': s.group('stream_state')},
                    'NAME': s.group('device_name')}

        return {'RESULT': 'FAILED'}

    ### STREAMING ###

    def startStreaming(self):
        """Used to start the stream function on a Monarch HD device that is set to RTMP mode."""
        result = self.__doQuery('StartStreaming')

        return {'RESULT': result}

    def stopStreaming(self):
        """Used to stop the stream function on a Monarch HD device that is set to RTMP mode."""
        result = self.__doQuery('StopStreaming')

        return {'RESULT': result}

    ### RECORDING ###

    def startRecording(self):
        """Used to start the record function on a Monarch HD device."""
        result = self.__doQuery('StartRecording')

        return {'RESULT': result}

    def stopRecording(self):
        """Used to stop the record function on a Monarch HD device."""
        result = self.__doQuery('StopRecording')

        return {'RESULT': result}

    ### COMBINED ###

    def startStreamingAndRecording(self):
        """Used to start the stream (RTMP mode) and record functions simultaneously on a Monarch HD device."""
        result = self.__doQuery('StartStreamingAndRecording')

        return {'RESULT': result}

    def stopStreamingAndRecording(self):
        """Used to stop the stream (RTMP mode) and record functions simultaneously on a Monarch HD device."""
        result = self.__doQuery('StopStreamingAndRecording')

        return {'RESULT': result}

    ### STREAMING OPTIONS ###

    def getStreamingVideoDataRate(self):
        """Used to acquire the average video data rate in kb/s (bit rate) that is currently programmed on the device."""
        result = self.__doQuery('GetStreamingVideoDataRate')

        # BITRATE:<average bit rate>
        p = re.compile(u'BITRATE:(?P<bitrate>[A-Z]+)$', re.IGNORECASE)
        s = re.search(p, result)

        if s:
            return {'RESULT': 'SUCCESS', 'BITRATE': s.group('bitrate')}

        return {'RESULT': 'FAILED'}

    def setStreamingVideoDataRate(self, bitrate):
        """Used to set the data rate (in kb/s) dynamically without stopping a current streaming operation."""
        command = '%s,%s' % ('SetStreamingVideoDataRate', bitrate)
        result = self.__doQuery(command)

        return {'RESULT': result}

    def getRTSP(self):
        """Used to get the URL and port that is currently programmed for RTSP streaming."""
        result = self.__doQuery('GetRTSP')

        # URL,name,port
        p = re.compile(u'(?P<url>.+),(?P<name>.+),(?P<port>.+)', re.IGNORECASE)
        s = re.search(p, result)

        if s:
            return {'RESULT': 'SUCCESS', 'RTSP': {'URL': s.group('url'),
                                                  'NAME': s.group('name'),
                                                  'PORT': s.group('port')}}

        return {'RESULT': result}

    def setRTSP(self, url, port):
        """Used to set the RTSP URL and port, as well as switch the streaming mode to RTSP on the device."""
        command = '%s,%s,$s' % ('SetRTSP', url, port)
        result = self.__doQuery(command)

        return {'RESULT': result}

    def getRTMP(self):
        """Used to get the RMTP settings that are currently programmed."""
        result = self.__doQuery('GetRTMP')

        # URL,name,port
        p = re.compile(u'(?P<url>.+),(?P<name>.+)', re.IGNORECASE)
        s = re.search(p, result)

        if s:
            return {'RESULT': 'SUCCESS', 'RTSP': {'URL': s.group('url'),
                                                  'NAME': s.group('name')}}

    def setRTMP(self, url, stream, username, password):
        """Used to configure the RTMP parameters and set the streaming mode to RTMP."""
        command = '%s,%s,$s,%s' % ('SetRTMP', url, stream, username, password)
        result = self.__doQuery(command)

        return {'RESULT': result}