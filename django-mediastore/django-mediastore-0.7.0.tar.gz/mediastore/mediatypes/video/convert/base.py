# -*- coding: utf-8 -*-
import os
import subprocess
from datetime import datetime
from mediastore.mediatypes.video.conf import settings


class VideoConverterBase(object):
    convert_bin = None
    convert_args = None
    thumbnail_bin = None
    thumbnail_args = None

    class ConvertionError(Exception):
        pass

    def __init__(self, **kwargs):
        self.stdout = ''
        self.stderr = ''
        self.failed = False
        self.config = self.prepare_config(kwargs)

    def prepare_config(self, config):
        default_config = {
            'width': settings.MEDIASTORE_VIDEO_WIDTH,
            'height': settings.MEDIASTORE_VIDEO_HEIGHT,
            'bitrate': settings.MEDIASTORE_VIDEO_BITRATE,
            'audio_bitrate': settings.MEDIASTORE_VIDEO_AUDIO_BITRATE,
            'thumbnail_pos': settings.MEDIASTORE_VIDEO_THUMBNAIL_POS,
        }
        default_config.update(config)
        return default_config

    def prepare_command_args(self, bin, args, extra_config=None):
        config = self.config.copy()
        if extra_config:
            config.update(extra_config)
        return [arg % config for arg in [bin] + list(args)]

    def execute_command(self, args):
        print ' '.join(args)
        try:
            self.stdout += ('Executing: "%s", %s\n' % (
                ' '.join(args), datetime.now()))
            try:
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                process.wait()
            except OSError:
                raise self.ConvertionError
            self.stdout += process.stdout.read() + '\n'
            self.stderr += process.stderr.read() + '\n'
            self.stdout += 'Exit code: %d\n' % process.returncode
        except self.ConvertionError, e:
            self.stderr += 'Convertion failed:\n%s\n' % e.args[0]
            self.failed = True
            raise

    def convert(self, input_path, output_path, extra_config=None):
        if extra_config is None:
            extra_config = {}
        extra_config['input'] = input_path
        extra_config['output'] = output_path
        self.execute_command(self.prepare_command_args(
            self.convert_bin,
            self.convert_args,
            extra_config))
        # no output file created
        if not os.path.exists(output_path):
            self.stderr += 'convertion: no output file created\n'
            raise self.ConvertionError
        # filesize is 0 bytes
        if os.stat(output_path)[6] == 0:
            os.unlink(output_path)
            self.stderr += 'convertion: zero size output file\n'
            raise self.ConvertionError

    def thumbnail(self, input_path, output_path, extra_config=None):
        if extra_config is None:
            extra_config = {}
        extra_config['input'] = input_path
        extra_config['output'] = output_path
        try:
            self.execute_command(self.prepare_command_args(
                self.thumbnail_bin,
                self.thumbnail_args,
                extra_config))
        except self.ConvertionError:
            try:
                extra_config['thumbnail_pos'] = 1
                self.execute_command(self.prepare_command_args(
                    self.thumbnail_bin,
                    self.thumbnail_args,
                    extra_config))
            except self.ConvertionError:
                pass
        # filesize is 0 bytes
        if os.stat(output_path)[6] == 0:
            os.unlink(output_path)
            self.stderr += 'thumbnail creation: zero size output file\n'
            raise self.ConvertionError
        # no output file created
        if not os.path.exists(output_path):
            self.stderr += 'thumbnail creation: no output file created\n'
            raise self.ConvertionError
