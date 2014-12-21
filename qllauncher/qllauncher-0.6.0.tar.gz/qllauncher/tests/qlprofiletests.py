"""
QuakeLive Launcher
Copyright (C) 2013  Victor Polevoy (vityatheboss@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Victor Polevoy'

from qllauncher import qlprofile

profile = qlprofile.QLProfile('fx', qlprofile.QLProfileRequestType.SUMMARY, True)
i = 5
i += 1


from html import parser as html_parser
parser = html_parser.HTMLParser()
# page = qlprofile.QLProfile.get_profile_page('fx', qlprofile.QLProfileRequestType.SUMMARY).text
page = ''

# result = parser.feed(page)
# print(result)




import xml.etree.ElementTree as ET
# parser = ET.XMLParser()
page = page.replace('&hellip;', '...')
tree = ET.fromstring(page)
div_img = tree.findall('.//div[@class="prf_imagery"]')[0][0]
profile_title = tree.findall('.//h1[@class="profile_title"]')[0]
profile_title_flag = profile_title[0]
profile_title_name = profile_title.data
print('to string: ' + str(ET.tostring(tree[0])))
print('div image style: ' + div_img.attrib['style']) # *******



