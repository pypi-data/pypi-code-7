# -*- coding: utf-8 -*-
"""
===============================================================
Preset data structures (:mod:`pksci.tools.mpltools._luts`)
===============================================================

.. currentmodule:: pksci.tools.mpltools._luts

"""
from __future__ import division, absolute_import, print_function
__docformat__ = 'restructuredtext'

from collections import OrderedDict

__all__ = ['color_dict', 'marker_dict', 'markersize_dict', 'mpl_colors',
           'named_colors', 'rainbow_color_list', 'emacs_colors',
           'web_colors']

marker_dict = {}
_markers = {'square': 's',
            'point': '.',
            'circle': 'o',
            'triangle_down': 'v',
            'triangle_up': '^',
            'triangle_left': '<',
            'triangle_right': '>',
            'octagon': '8',
            'pentagon': 'p',
            'star': '*',
            'plus': '+',
            'hexagon1': 'h',
            'hexagon2': 'H',
            'diamond': 'D',
            'thin_diamond': 'd',
            'x': 'x',
            'vline': '|',
            'hline': '_'}
marker_dict.update(_markers)

markersize_dict = {'o': 34, 's': 32, '^': 36, 'v': 36, 'p': 36, 'D': 32,
                   '>': 36, '<': 36, 'd': 36, 'h': 40, 'H': 40, '*': 42,
                   '8': 36, '+': 40, '.': 20, 'x': 32, '|': 40, '_': 40}

color_dict = OrderedDict()

mpl_colors = {'black': 'k',
              'white': 'w',
              'red': 'r',
              'green': 'g',
              'blue': 'b',
              'cyan': 'c',
              'yellow': 'y',
              'magenta': 'm'}
color_dict.update(mpl_colors)

named_colors = OrderedDict()
named_colors.update({'DarkBlue': '#00008B'})
named_colors.update({'DarkRed': '#8B0000'})
named_colors.update({'DarkGreen': '#006400'})
named_colors.update({'DarkGray': '#A9A9A9'})
named_colors.update({'OrangeRed': '#FF4500'})
named_colors.update({'DarkTurquoise': '#00CED1'})
named_colors.update({'BlueViolet': '#8A2BE2'})
named_colors.update({'DarkCyan': '#008B8B'})
named_colors.update({'DarkOrange': '#FF8C00'})
named_colors.update({'DarkMagenta': '#8B008B'})
named_colors.update({'DarkViolet': '#9400D3'})
named_colors.update({'DarkOrchid': '#9932CC'})
named_colors.update({'DebianRed': '#D70751'})
named_colors.update({'DeepSkyBlue2': '#00B2EE'})
named_colors.update({'DeepPink': '#FF1493'})
named_colors.update({'LimeGreen': '#32CD32'})
named_colors.update({'GreenYellow': '#ADFF2F'})
named_colors.update({'MediumBlue': '#0000CD'})
named_colors.update({'VioletRed': '#D02090'})
color_dict.update(named_colors)

forty_colors = OrderedDict()

oxygen_colors = OrderedDict()

rainbow_color_list = []
rainbow_color_list.append('#0000FF')
rainbow_color_list.append('#FF3333')
rainbow_color_list.append('#CC99FF')
rainbow_color_list.append('#006600')
rainbow_color_list.append('#FF9933')
rainbow_color_list.append('#CC00CC')
rainbow_color_list.append('#FFFF33')
rainbow_color_list.append('#6600CC')
rainbow_color_list.append('#00FFFF')
rainbow_color_list.append('#0066CC')
rainbow_color_list.append('#CC0000')
rainbow_color_list.append('#00FF00')
rainbow_color_list.append('#FFFF99')


emacs_colors = OrderedDict()
#emacs_colors.update({'grey1': '#030303'})
emacs_colors.update({'blue1': '#0000FF'})
emacs_colors.update({'orange1': '#FFA500'})
emacs_colors.update({'yellow1': '#FFFF00'})
emacs_colors.update({'green1': '#00FF00'})
emacs_colors.update({'magenta1': '#FF00FF'})
emacs_colors.update({'cyan1': '#00FFFF'})
#emacs_colors.update({'DeepSkyBlue1': '#00BFFF'})
#emacs_colors.update({'chartreuse1': '#7FFF00'})
#emacs_colors.update({'OliveDrab1': '#C0FF3E'})
#emacs_colors.update({'SpringGreen1': '#00FF7F'})
#emacs_colors.update({'MediumPurple1': '#AB82FF'})
#emacs_colors.update({'SteelBlue1': '#104E8B'})
#emacs_colors.update({'purple2': '#912CEE'})
#emacs_colors.update({'grey10': '#1A1A1A'})
emacs_colors.update({'red1': '#FF0000'})
emacs_colors.update({'green2': '#00EE00'})
emacs_colors.update({'purple1': '#9B30FF'})
emacs_colors.update({'DodgerBlue1': '#1E90FF'})
emacs_colors.update({'cyan3': '#00CDCD'})
#emacs_colors.update({'purple3': '#7D26CD'})
emacs_colors.update({'DeepPink2': '#EE1289'})
emacs_colors.update({'green3': '#00CD00'})
emacs_colors.update({'magenta3': '#CD00CD'})
emacs_colors.update({'DeepSkyBlue3': '#009ACD'})
emacs_colors.update({'green4': '#008B00'})
emacs_colors.update({'magenta2': '#EE00EE'})
emacs_colors.update({'red3': '#CD0000'})
emacs_colors.update({'DeepSkyBlue2': '#00B2EE'})
emacs_colors.update({'DeepPink3': '#CD1076'})
emacs_colors.update({'DodgerBlue4': '#104E8B'})
#emacs_colors.update({'grey40': '#666666'})

#emacs_colors.update({'red2': '#EE0000'})
#emacs_colors.update({'DodgerBlue2': '#1C86EE'})
#emacs_colors.update({'orange2': '#EE9A00'})
#emacs_colors.update({'yellow2': '#EEEE00'})
#emacs_colors.update({'blue2': '#0000EE'})
#emacs_colors.update({'chartreuse2': '#76EE00'})
#emacs_colors.update({'OliveDrab2': '#B3EE3A'})
#emacs_colors.update({'SpringGreen2': '#00EE76'})
#emacs_colors.update({'MediumPurple2': '#9F79EE'})
#emacs_colors.update({'SteelBlue2': '#63B8FF'})
#emacs_colors.update({'grey20': '#333333'})

#emacs_colors.update({'orange3': '#CD8500'})
#emacs_colors.update({'yellow3': '#CDCD00'})
#emacs_colors.update({'DodgerBlue3': '#1874CD'})
#emacs_colors.update({'chartreuse3': '#66CD00'})
#emacs_colors.update({'OliveDrab3': '#9ACD32'})
#emacs_colors.update({'SpringGreen3': '#00CD66'})
#emacs_colors.update({'MediumPurple3': '#8968CD'})
#emacs_colors.update({'SteelBlue3': '#4F94CD'})
#emacs_colors.update({'grey30': '#4D4D4D'})
emacs_colors.update({'BlueViolet': '#8A2BE2'})
emacs_colors.update({'DarkBlue': '#00008B'})
emacs_colors.update({'DarkOrchid': '#9932CC'})
emacs_colors.update({'DarkRed': '#8B0000'})
emacs_colors.update({'DebianRed': '#D70751'})
emacs_colors.update({'DarkCyan': '#008B8B'})
emacs_colors.update({'DarkGray': '#A9A9A9'})
emacs_colors.update({'DarkGreen': '#006400'})
emacs_colors.update({'DarkOrange': '#FF8C00'})
emacs_colors.update({'DarkMagenta': '#8B008B'})
emacs_colors.update({'DarkViolet': '#9400D3'})
emacs_colors.update({'DarkTurquoise': '#00CED1'})
emacs_colors.update({'DeepSkyBlue2': '#00B2EE'})
emacs_colors.update({'DeepPink': '#FF1493'})
emacs_colors.update({'LimeGreen': '#32CD32'})
emacs_colors.update({'MediumBlue': '#0000CD'})
emacs_colors.update({'OrangeRed': '#FF4500'})
emacs_colors.update({'VioletRed': '#D02090'})

#emacs_colors.update({'orange4': '#8B5A00'})
#emacs_colors.update({'yellow4': '#8B8B00'})
#emacs_colors.update({'purple4': '#551A8B'})
#emacs_colors.update({'DeepSkyBlue4': '#00688B'})
#emacs_colors.update({'chartreuse4': '#458B00'})
#emacs_colors.update({'OliveDrab4': '#698B22'})
#emacs_colors.update({'SpringGreen4': '#008B45'})
#emacs_colors.update({'MediumPurple4': '#5D478B'})
#emacs_colors.update({'SteelBlue4': '#36648B'})
#emacs_colors.update({'DeepPink4': '#8B0A50'})

color_dict.update(emacs_colors)

web_colors = {'cayenne': '#800000',
              'mocha': '#804000',
              'asparagus': '#808000',
              'fern': '#408000',
              'clover': '#008000',
              'moss': '#008040',
              'teal': '#008080',
              'ocean': '#004080',
              'midnight': '#000080',
              'eggplant': '#400080',
              'plum': '#800080',
              'maroon': '#800040',
              'tin': '#7F7F7F',
              'steel': '#666666',
              'nickel': '#808080',
              'aluminum': '#999999',
              'magnesium': '#B3B3B3',
              'silver': '#CCCCCC',
              'mercury': '#E6E6E6',
              'snow': '#FFFFFF',
              'licorice': '#000000',
              'lead': '#191919',
              'tungsten': '#333333',
              'iron': '#4C4C4C',
              'magenta': '#FF00FF',
              'strawberry': '#FF0080',
              'bubblegum': '#FF66FF',
              'carnation': '#FF6FCF',
              'lavender': '#CC66FF',
              'orchid': '#6666FF',
              'grape': '#8000FF',
              'blueberry': '#0000FF',
              'turquoise': '#00FFFF',
              'aqua': '#0080FF',
              'ice': '#66FFFF',
              'sky': '#66CCFF',
              'spindrift': '#66FFCC',
              'flora': '#66FF66',
              'sea foam': '#00FF80',
              'spring': '#00FF00',
              'lemon': '#FFFF00',
              'lime': '#80FF00',
              'banana': '#FFFF66',
              'honeydew': '#CCFF66',
              'cantaloupe': '#FFCC66',
              'salmon': '#FF6666',
              'tangerine': '#FF8000',
              'maraschino': '#FF0000'}
color_dict.update(web_colors)
