# -*- coding: utf-8 -*-
import os
import operator
import tempfile
from mediastore.mediatypes.video.convert.base import VideoConverterBase
from mediastore.mediatypes.video.conf import settings


class FFmpegConverter(VideoConverterBase):
    convert_bin = settings.MEDIASTORE_VIDEO_FFMPEG_BIN
    convert_args = settings.MEDIASTORE_VIDEO_FFMPEG_ARGS
    thumbnail_bin = settings.MEDIASTORE_VIDEO_FFMPEG_THUMBNAIL_BIN
    thumbnail_args = settings.MEDIASTORE_VIDEO_FFMPEG_THUMBNAIL_ARGS

    class ConvertionError(VideoConverterBase.ConvertionError):
        pass

    def prepare_config(self, config):
        default_config = {
            'croptop': '0',
            'cropbottom': '0',
            'cropleft': '0',
            'cropright': '0',
            'padtop': '0',
            'padbottom': '0',
            'padleft': '0',
            'padright': '0',
        }
        config = super(FFmpegConverter, self).prepare_config(config)
        default_config.update(config)
        return default_config

    def convert(self, input_path, output_path, extra_config=None):
        extra_config = {}
        expected_width = int(self.config['width'])
        expected_height = int(self.config['height'])

        # create sample thumbnail to get the size of the video
        tfile = tempfile.mkstemp()[1]
        thumbnail_args = [
            '-i', input_path,
            '-f', 'mjpeg',
            '-ss', '0',
            '-an',
            '-y', tfile,
        ]
        try:
            try:
                from PIL import Image
            except ImportError:
                import Image
        except ImportError, e:
            self.stderr += (
                'cannot import PIL. You need PIL installed '
                'to use proportional scaling with ffmpeg backend.\n')
            raise self.ConvertionError
        self.execute_command(self.prepare_command_args(
            self.thumbnail_bin,
            thumbnail_args,
        ))
        try:
            actual_width, actual_height = Image.open(tfile).size
        except IOError, e:
            self.stderr += e.args[0] + '\n'
            raise self.ConvertionError
        # delete sample thumbnail
        os.unlink(tfile)

        extra_args = []

        # now keep the width and crop or pad height to get the correct
        # proportions
        expected_ratio = operator.truediv(expected_width, expected_height)
        actual_ratio = operator.truediv(actual_width, actual_height)

        if settings.MEDIASTORE_VIDEO_FFMPEG_CROP:
            # video is wider than expected video dimensions
            if expected_ratio < actual_ratio:
                wanted_width = int(round(
                    actual_height * expected_ratio, 0))
                crop = actual_width - wanted_width
                crop -= crop % 4
                extra_config['cropleft'] = crop / 2
                extra_config['cropright'] = crop / 2
            # video is higher than expected video dimensions
            else:
                wanted_height = int(round(
                    actual_width * expected_ratio ** -1, 0))
                crop = actual_height - wanted_height
                crop -= crop % 4
                extra_config['croptop'] = crop / 2
                extra_config['cropbottom'] = crop / 2

        # don't crop so we pad
        else:
            # video is wider than expected video dimensions
            if expected_ratio < actual_ratio:
                wanted_height = int(round(
                    expected_width * actual_ratio ** -1, 0))
                padding = expected_height - wanted_height
                padding -= padding % 4
                self.config['padtop'] = padding / 2
                self.config['padbottom'] = padding / 2
                wanted_height -= wanted_height % 2
                self.config['height'] = str(wanted_height)
            # video is higher than expected video dimensions
            elif expected_ratio > actual_ratio:
                wanted_width = int(round(
                    expected_height * actual_ratio, 0))
                padding = expected_width - wanted_width
                padding -= padding % 4
                self.config['padleft'] = padding / 2
                self.config['padright'] = padding / 2
                wanted_width -= wanted_width % 2
                self.config['width'] = str(wanted_width)

        super(FFmpegConverter, self).convert(
            input_path, output_path, extra_config)
