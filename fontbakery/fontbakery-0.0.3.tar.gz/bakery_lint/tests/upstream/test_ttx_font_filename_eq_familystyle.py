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
import os.path

from bakery_lint.base import BakeryTestCase as TestCase, autofix
from bakery_cli.ttfont import Font, getSuggestedFontNameValues


class TestTTFSourceFontFileNameEqualsFamilyStyle(TestCase):

    targets = ['upstream', 'upstream-ttx']
    tool = 'lint'
    name = __name__

    @autofix('bakery_cli.pipe.autofix.rename')
    def test_source_ttf_font_filename_equals_familystyle(self):
        """ Source TTF Font filename equals family style """
        ttfont = Font.get_ttfont(self.operator.path)

        suggestedvalues = getSuggestedFontNameValues(ttfont.ttfont)

        family_name = suggestedvalues['family']
        subfamily_name = suggestedvalues['subfamily']

        expectedname = '{0}-{1}'.format(family_name.replace(' ', ''),
                                        subfamily_name.replace(' ', ''))
        actualname, extension = os.path.splitext(self.operator.path)

        expected_filename = '{0}{1}'.format(expectedname, extension)
        setattr(self, 'expectedfilename', expected_filename)
        self.assertEqual(os.path.basename(actualname), expectedname)
