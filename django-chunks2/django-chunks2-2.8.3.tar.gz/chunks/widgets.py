# -*- coding: utf-8 -*-

from easy_thumbnails.widgets import ImageClearableFileInput

TEMPLATE = u"""
<style>
div.thumb {
    border: 1px solid black; background-color: #ddd;
    height: 128px; width: 128px;
}
div.thumb a img {
    width: 100%%; height: 100%%;
}
</style>
%(template)s<br/>
<div class="thumb">
    <a href="%(source_url)s" target="_blank">%(thumb)s</a>
</div>
"""


class CustomizedImageWidget(ImageClearableFileInput):
    template_with_thumbnail = TEMPLATE
