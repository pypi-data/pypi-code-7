# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from __future__ import print_function

from fontTools.ttLib import TTLibError


def fix_style_names(fontpath):
    from bakery_cli.ttfont import Font
    try:
        font = Font(fontpath)
    except TTLibError as ex:
        print("ERROR: %s" % ex)
        return
    # font['name'].fsType = 0
    font.save(fontpath + '.fix')


def show_stylenames(fontpath):
    from bakery_cli.ttfont import Font
    try:
        font = Font(fontpath)
    except TTLibError as ex:
        print("ERROR: %s" % ex)
        return
    print(font['name'].names[2].string)
