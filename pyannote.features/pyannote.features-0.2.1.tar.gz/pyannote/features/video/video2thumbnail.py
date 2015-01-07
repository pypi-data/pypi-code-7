#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr

from __future__ import unicode_literals

"""
Extract frame thumbnails from video and generate visualization web page

Usage:
  video2thumb [--step=<step>] [--thumbnail=<fmt>] <input_video> <output_dir>
  video2thumb -h | --help
  video2thumb --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --step=<step>
                Step in seconds [default: 1.000].
  --thumbnail=<fmt>
                Thumbnail path format [default: {time:.3f}.jpg]
"""

import cv
import cv2
import numpy as np
from docopt import docopt
from path import path
from jinja2 import Template

thumb_template = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ video }}</title>
        <link rel="stylesheet" href="http://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
        <style type="text/css">div.inline { float:left; }</style>
    </head>
    <body>
        {% for image in images %}
        <div class="inline">
            <img src="{{ image }}" title="{{ image[:-4] }}">
            <div class="caption">
                {{ image[:-4] }}
            </div>
        </div>
        {% endfor %}
    </body>
</html>
"""


def do_it(input_video, step_in_seconds, output_dir, thumbnail_fmt):

    capture = cv2.VideoCapture(input_video)

    # frame size
    height = int(capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
    width = int(capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))

    # video "size"
    framePerSecond = capture.get(cv.CV_CAP_PROP_FPS)
    frameCount = int(capture.get(cv.CV_CAP_PROP_FRAME_COUNT))
    duration = frameCount / framePerSecond

    thumbMaxWidth, thumbMaxHeight = (100, 200)
    ratioHeight = 1. * thumbMaxHeight / height
    ratioWidth = 1. * thumbMaxWidth / width
    ratio = min(ratioHeight, ratioWidth)

    # create output dir if it does not exist already
    output_dir = path(output_dir)
    output_dir.makedirs_p()

    images = []

    for t in np.arange(0., duration, step_in_seconds):

        # jump to next position
        capture.set(cv.CV_CAP_PROP_POS_MSEC, 1000. * t)

        # grab frame
        success, frame = capture.read()

        # create thumbnail
        thumbnail = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)

        # save image
        images.append(path(thumbnail_fmt.format(time=t)))
        cv2.imwrite(path.joinpath(output_dir, images[-1]), thumbnail)

    capture.release()

    template = Template(thumb_template)
    with open(path.joinpath(output_dir, 'index.html'), 'w') as f:
        f.write(template.render(video=input_video, images=images))

if __name__ == '__main__':

    arguments = docopt(__doc__, version='video2thumbnail 1.0')

    input_video = arguments['<input_video>']
    output_dir = arguments['<output_dir>']
    thumbnail_fmt = arguments['--thumbnail']
    step_in_seconds = float(arguments['--step'])
    do_it(input_video, step_in_seconds, output_dir, thumbnail_fmt)
