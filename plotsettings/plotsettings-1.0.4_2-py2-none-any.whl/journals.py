'''
Dictionary of plot settings for submission to academic journals.

The structure of the dictionary 'journals' must adhere to the following structure::

    journals = {'journal1':      {'rcParams':     {'param1': value1,
                                                   'param2': value2 ...}, 
                                  'figsize':      {'param1': value1,
                                                   'param2': value2 ...},
                                  'panel_labels': {'param1': value1,
                                                   'param2': value2 ...},
                'journal2':      {'rcParams':     {'param1': value1,
                                                   'param2': value2 ...}, 
                                  'figsize':      {'param1': value1,
                                                   'param2': value2 ...},
                                  'panel_labels': {'param1': value1,
                                                   'param2': value2 ...},
                'journal3'...
                }

where 'journalx' are the identifying names of academic journals (e.g. 'Nature'), with
the specifications for each journal being divided into 3 dictionaries:

    * *rcParams*: All parameters are optional. Any valid input to pyplot.rcParams (for
      example font name and sizes, default linewidths) is accepted. Definitions of valid 
      keys to rcParams can be found `here <http://matplotlib.org/users/customizing.html>`_.
    * *figsize*: Set figure dimension calculations. Requires the parameters column_width, 
      gutter_width, and units. The parameter max_height is optional. See below for details.
    * *panel_labels*: Set default panel labels (e.g. A, B, C). All parameters are optional.
      See below for details.
  
The possible non-rcParams parameters are:
    
    * *figsize*:
    
        * *column_width* (required) - the maximum width a figure is allowed to be while still 
          fitting withing a single column.
        * *gutter_width* (required) - the width of the gutter (space between columns). This can 
          usually be found by comparing the maximum width that a journal allows for a single-
          column figure with the maximum width of a 2-column figure. For example, PLoS One
          allows a 1-column figure to be 83 mm in width and a 2-column figure to be 173.5 mm,
          meaning that the gutter width (173.5 - 83*2) must be 7.5 mm wide.
        * *max_height* (optional) - the maximum height a figure is allowed to be while fitting 
          on a single page (i.e. the page height).
        * *units* (required) - the units in which the above are reported. Can be one of 'mm', 
          'cm', 'inch', or 'pts'
    
    * panel_labels:
    
        * *label_weight* (optional) - the font weight of panel annotations (e.g. A, B, C etc.).
          Default is 'bold'
        * *label_case* (optional) - whether to capitalize ('upper') or not capitalize
          ('lower') the panel labels.
        * *label_prefix* (optional) - characters to prepend to panel label (e.g. if the desired
          label style is (A), (B), etc., set label_prefix to ')').
        * *label_suffix* (optional) - characters to append to panel label (e.g. if the desired
          label style is a., b., etc., set label_suffix = '.')

Values for many of these settings can be found in the journal's Author Information page. For example,
the settings for the Proceedings of the Royal Society B can be found in
`<http://rspb.royalsocietypublishing.org/site/misc/preparing-article.xhtml>`_

Some notes:
    * Absolute minimum linewidth is typically 0.1pt - don't go below this,
      and for prominent lines (e.g. plot lines) use 1 pt.

Created on Oct 10, 2014

@author: gdelraye
'''

# Journals in alphabetical order:
journals = {
#--- Cell, updated 14OCT2014:
            'Cell':        {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Helvetica'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 85,
                                            'gutter_width': 4,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''}
                            },
#--- Copeia, updated 14OCT2014:
            'Copeia':     {'rcParams':     {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Helvetica'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 96,
                                            'gutter_width': 6,
                                            'max_height': 245,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''}
                           },
#--- Deep Sea Research II, updated 13OCT2014:
            'DSRII':       {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 8,
                                            'xtick.labelsize': 8,
                                            'ytick.labelsize': 8,
                                            'legend.fontsize': 8,
                                            'lines.markersize': 3,
                                            'font.size': 8,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 90,
                                            'gutter_width': 10,
                                            'max_height': 240,
                                            'units': 'mm',
                                            'fontsize': 8}, 
                            'panel_labels':{}
                            },
#--- Ecology Letters, updated 14OCT2014:
            'EcolLett':    {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 82,
                                            'gutter_width': 9,
                                            'units': 'mm'},
                            'panel_labels':{}
                            },
#--- Global Change Biology, updated 14OCT2014:
            'GlobChangeBio':{'rcParams':   {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 80,
                                            'gutter_width': 9,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'lower',
                                            'prefix': '(',
                                            'suffix': ')'}
                             },
#--- Global Environmental Change, updated 14OCT2014:
            'GlobEnvChange':{'rcParams':   {'backend': 'pdf',
                                            'axes.labelsize': 7,
                                            'xtick.labelsize': 7,
                                            'ytick.labelsize': 7,
                                            'legend.fontsize': 7,
                                            'lines.markersize': 3,
                                            'font.size': 7,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                             'figsize':    {'column_width': 90,
                                            'gutter_width': 10,
                                            'max_height': 240,
                                            'units': 'mm'},
                             'panel_labels':{}
                             },
#--- Integrative and Comparative Biology, updated 14OCT2014:
            'IntCompBiol': {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 88,
                                            'gutter_width': 8,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''}
                            }, 
#--- Journal of Experimental Biology, updated 14OCT2014:
            'JEB':         {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 8,
                                            'xtick.labelsize': 8,
                                            'ytick.labelsize': 8,
                                            'legend.fontsize': 8,
                                            'lines.markersize': 3,
                                            'font.size': 8,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 85,
                                            'gutter_width': 10,
                                            'max_height': 210,
                                            'units': 'mm'},
                            'panel_labels':{}
                             },
# Limnology and Oceanography, updated 14OCT2014:
            'LimnolOcean': {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 10,
                                            'xtick.labelsize': 10,
                                            'ytick.labelsize': 10,
                                            'legend.fontsize': 10,
                                            'lines.markersize': 3,
                                            'font.size': 10,
                                            'font.family': u'serif',
                                            'font.serif': ['Times New Roman'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 89,
                                            'gutter_width': 6,
                                            'max_height': 232,
                                            'units': 'mm'},
                            'panel_labels':{'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''} 
                            },
#--- Marine Ecology Progress Series, updated 14OCT2014:
            'MEPS':        {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 81,
                                            'gutter_width': 7,
                                            'max_height': 225,
                                            'units': 'mm'}, 
                            'panel_labels':{}
                             },
#--- Nature Magazine, updated 15OCT2014:
            'Nature':      {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 7,
                                            'xtick.labelsize': 7,
                                            'ytick.labelsize': 7,
                                            'legend.fontsize': 7,
                                            'lines.markersize': 3,
                                            'font.size': 7,
                                            'font.family': u'serif',
                                            'font.serif': ['Times New Roman'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 89,
                                            'gutter_width': 5,
                                            'max_height': 247,
                                            'units': 'mm'},
                            'panel_labels':{'case': 'lower',
                                            'fontweight': 'bold',
                                            'prefix': '',
                                            'suffix': '',
                                            'fontsize': 8} 
                            },
#--- Oecologia, updated 15OCT2014:
            'Oecologia':   {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 8,
                                            'xtick.labelsize': 8,
                                            'ytick.labelsize': 8,
                                            'legend.fontsize': 8,
                                            'lines.markersize': 3,
                                            'font.size': 8,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 84,
                                            'gutter_width': 6,
                                            'max_height': 234,
                                            'units': 'mm'},
                            'panel_labels':{'case': 'lower',
                                            'fontweight': 'normal',
                                            'prefix': '',
                                            'suffix': '',
                                            'fontsize': 9} 
                            },
#--- Public Library of Science Biology, updated 14OCT2014:
            'PLOSBio':     {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 83,
                                            'gutter_width': 7.5,
                                            'max_height': 233.5,
                                            'units': 'mm'}, 
                            'panel_labels':{}
                             },
#--- Public Library of Science One, updated 13OCT2014:
            'PLOSOne':     {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 83,
                                            'gutter_width': 7.5,
                                            'max_height': 233.5,
                                            'units': 'mm'},
                            'panel_labels':{}
                             },
# Proceedings of the National Academy of Sciences, updated 13OCT2014:
            'PNAS':        {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 8,
                                            'xtick.labelsize': 8,
                                            'ytick.labelsize': 8,
                                            'legend.fontsize': 8,
                                            'lines.markersize': 3,
                                            'font.size': 8,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 87,
                                            'gutter_width': 4,
                                            'max_height': 240,
                                            'units': 'mm'},
                            'panel_labels':{}
                             },
#--- Presentations slides (e.g. powerpoint):
            'Presentation':{'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 18,
                                            'xtick.labelsize': 18,
                                            'ytick.labelsize': 18,
                                            'legend.fontsize': 18,
                                            'lines.markersize': 3,
                                            'font.size': 18,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Arial'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 5,
                                            'gutter_width': 0,
                                            'max_height': 7.5,
                                            'units': 'inch'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''}
                            },
#--- Proceedings of the Royal Society B, updated 13OCT2014:
            'ProcRoySocB': {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 9,
                                            'xtick.labelsize': 9,
                                            'ytick.labelsize': 9,
                                            'legend.fontsize': 9,
                                            'lines.markersize': 3,
                                            'font.size': 9,
                                            'font.family': u'serif',
                                            'font.serif': ['Times New Roman'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 84,
                                            'gutter_width': 7,
                                            'max_height': 250,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'lower',
                                            'prefix': '(',
                                            'suffix': ')',
                                            'fontsize': 11}
                            },
#--- Science Magazine, updated 14OCT2014:
            'Science':     {'rcParams':    {'backend': 'pdf',
                                            'axes.labelsize': 7,
                                            'xtick.labelsize': 7,
                                            'ytick.labelsize': 7,
                                            'legend.fontsize': 7,
                                            'lines.markersize': 3,
                                            'font.size': 7,
                                            'font.family': u'sans-serif',
                                            'font.sans-serif': ['Helvetica'],
                                            'text.usetex': False},
                            'figsize':     {'column_width': 55,
                                            'gutter_width': 10,
                                            'units': 'mm'},
                            'panel_labels':{'fontweight': 'bold',
                                            'case': 'upper',
                                            'prefix': '',
                                            'suffix': ''}
                            }
            }

