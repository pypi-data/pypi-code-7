# -*- coding: utf-8 -*-
"""
=========================================================================
Module for text/LaTeX strings (:mod:`pksci.tools.mpltools._strings`)
=========================================================================

.. currentmodule:: pksci.tools.mpltools._strings

"""
from __future__ import absolute_import, print_function, division

import re

__all__ = ['generate_axis_label_dict', 'concat_units', 'concat_y_vs_x',
           'plotstr', 'replace_whitespace',
           'txt2tex', 'mathrm', 'mathsf', 'texstr', 'texstr2mathrm',
           'texstr2mathsf', 'texstr2mathstr', 'txtstr2mathrm',
           'txtstr2mathsf', 'txtstr2mathstr', 'txtstr2texstr',
           'mathrm2mathsf', 'mathsf2mathrm', 'mixedstr2texstr',
           'axis_texlabels', 'axis_txtlabels', 'axis_labels',
           'var_equations',
           'var_strings', 'var_str',
           'var_texstrings', 'var_txtstrings', 'var_texstr', 'var_txtstr',
           'var_units', 'var_texunits', 'var_txtunits']


def generate_axis_label_dict(var_dict=None, units_dict=None,
                             label_dict=None, mathsf=True):
    """Generate an axis label dictionary.

    Generate axis label dictionary from a variable and units dictionary.

    Parameters
    ----------
    var_dict, units_dict : dict

    Returns
    -------
    axis_label_dict : dict

    """
    axis_label_dict = {}
    for strtype in ('tex', 'txt'):
        if strtype in var_dict.keys():
            axis_label_dict[strtype] = {}
            for var in var_dict[strtype].iterkeys():
                if var in units_dict[strtype].keys():
                    axis_label_dict[strtype][var] = \
                        var_dict[strtype][var] + ' ' + \
                        plotstr('(', strtype=strtype, mathsf=mathsf) + \
                        units_dict[strtype][var] + \
                        plotstr(')', strtype=strtype, mathsf=mathsf)
                else:
                    axis_label_dict[strtype][var] = var_dict[strtype][var]

    if label_dict is not None:
        label_dict.update(axis_label_dict)
        return label_dict
    else:
        return axis_label_dict


def concat_units(var, units, mathrmpar=True, mathrmfull=False,
                 usetex=False, mathvar=False, roman=True):
    """Append units to string.

    Parameters
    ----------
    var : str
    units : str
    mathrmpar : bool, optional
    mathrmfull : bool, optional
    usetex: bool, optional
    mathvar: bool, optional
    roman : bool, optional

    Returns
    -------
    str

    """
    return var + ' ' + plotstr('(', usetex, mathvar, roman) + units + \
        plotstr(')', usetex, mathvar, roman)


def concat_y_vs_x(x='', y='', mathrmvs=True, mathrmfull=False,
                  usetex=False, mathvar=False, roman=True):
    """Create string ``y` vs. ``x`` for plot title.

    Parameters
    ----------
    x : str
    y : str
    mathrmvs : bool, optional
    mathrmfull : bool, optional
    usetex: bool, optional
    mathvar: bool, optional
    roman : bool, optional

    Returns
    -------
    str

    """
    return y + ' ' + plotstr('vs.', usetex, mathvar, roman) + ' ' + x


def plotstr(txtstr, strtype=None, usetex=False, mathvar=False,
            mathsf=True, mathrm=False, roman=False):
    """Format a string for matplotlib use.

    Parameters
    ----------
    txtstr : str
    strtype : {None, 'tex', 'txt'}, optional
    usetex : bool, optional
    mathvar : bool, optional
    mathrm : bool, optional
    mathsf : bool, optional
    roman : bool, optional

    Returns
    -------
    str

    """
    if strtype is not None:
        if strtype == 'tex':
            usetex = True
        elif strtype == 'txt':
            usetex = False

    if usetex:
        if mathrm or roman:
            return txt2tex(txtstr, mathrm=True)
        elif mathsf:
            return txt2tex(txtstr, mathsf=True)
        else:
            return txt2tex(txtstr)
    else:
        if (mathvar and roman) or mathsf:
            return txtstr2mathsf(txtstr)
        elif mathrm or roman:
            return txtstr2mathrm(txtstr)
        elif mathvar:
            return txt2tex(txtstr)
        else:
            return txtstr


def replace_whitespace(txtstr):
    """Remove white space from text string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return ''.join(re.split('\W', txtstr.replace(' ', '_')))


def tex2txt(texstr):
    pass


def txt2tex(txtstr, mathrm=False, mathsf=False):
    """Convert text string to LaTeX string.

    Parameters
    ----------
    txtstr : str
    mathrm : bool, optional
    mathsf : bool, optional

    Returns
    -------
    str

    """
    splitstr = txtstr.strip().split()
    if mathrm:
        return ' '.join(('{!s}'.format(r'$\mathrm{' + word + r'}$') for
                        word in splitstr))
    elif mathsf:
        return ' '.join(('{!s}'.format(r'$\mathsf{' + word + r'}$') for
                        word in splitstr))
    else:
        return ' '.join(('{!s}'.format(r'$' + word + r'$')
                        for word in splitstr))


def mathrm(txtstr):
    """Convert text string to math roman LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr, mathrm=True)


def mathsf(txtstr):
    """Convert text string to math san-serif LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr, mathsf=True)


def texstr(txtstr):
    """Convert text string to LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr)


def texstr2mathrm(texstr):
    """Convert LaTeX string to math roman LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(' '.join([s.strip('$') for s in texstr.split()]),
                   mathrm=True)


def texstr2mathsf(texstr):
    """Convert LaTeX string to math sans-serif LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(' '.join([s.strip('$') for s in texstr.split()]),
                   mathsf=True)


def texstr2mathstr(texstr, mathrm=False, mathsf=False):
    """Convert LaTeX string to math LaTeX string.

    Parameters
    ----------
    txtstr : str
    mathrm : bool, optional
    mathsf : bool, optional

    Returns
    -------
    str

    """
    if mathrm:
        return texstr2mathrm(texstr)
    elif mathsf:
        return texstr2mathsf(texstr)
    else:
        return texstr
        #return txt2tex(' '.join([s.strip('$') for s in texstr.split()]))


def txtstr2mathrm(txtstr):
    """Convert text string to math roman LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr, mathrm=True)


def txtstr2mathsf(txtstr):
    """Convert text string to math sans-serif LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr, mathsf=True)


def txtstr2mathstr(txtstr, mathrm=False, mathsf=False):
    """Convert text string to math LaTeX string.

    Parameters
    ----------
    txtstr : str
    mathrm : bool, optional
    mathsf : bool, optional

    Returns
    -------
    str

    """
    if mathrm:
        return txtstr2mathrm(txtstr)
    elif mathsf:
        return txtstr2mathsf(txtstr)
    else:
        return txtstr


def txtstr2texstr(txtstr):
    """Convert text string to LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return txt2tex(txtstr)


def mathrm2mathsf(texstr):
    """Convert math roman LaTeX string to math sans-serif LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return texstr.replace('mathrm', 'mathsf')


def mathsf2mathrm(texstr):
    """Convert math sans-serif LaTeX string to math roman LaTeX string.

    Parameters
    ----------
    txtstr : str

    Returns
    -------
    str

    """
    return texstr.replace('mathsf', 'mathrm')


def mixedstr2texstr(mixedstr, tex2mathrm=False, tex2mathsf=False,
                    txt2mathrm=False, txt2mathsf=False):
    """Convert mixed text/LaTeX string to LaTeX string.

    Parameters
    ----------
    mixedstr : str
    tex2mathrm : bool, optional
    tex2mathsf : bool, optional
    txt2mathrm : bool, optional
    txt2mathsf : bool, optional

    Returns
    -------
    str

    """
    splitstr = mixedstr.strip().split()
    _texstr = ''
    for s in splitstr:
        if s.startswith('$') or s.endswith('$'):
            _texstr += texstr2mathstr(s, mathrm=tex2mathrm, mathsf=tex2mathsf)
        else:
            _texstr += txt2tex(s, mathrm=txt2mathrm, mathsf=txt2mathsf)
        _texstr += ' '
    return _texstr.strip()

var_equations = {}
var_txtstrings = {}
var_texunits = {}
var_txtunits = {}

nanotube_spatial_vars = ['Ch', 'd_tube', 'T_cell']
var_txtunits.update(dict.fromkeys(nanotube_spatial_vars, unicode(u'\u00c5')))
var_texunits.update(dict.fromkeys(nanotube_spatial_vars, mathrm('\AA')))

var_txtstrings.update({'Ch': 'C$\mathsf{_{h}}$'})
var_txtstrings.update({'d_tube': 'd$\mathsf{_{t}}$'})
var_txtstrings.update({'T_cell': 'T'})
var_txtstrings.update({'Td': 'T$\mathsf{_{d}}$'})

var_txtunits.update({'Td': 'eV'})
var_texunits.update({'Td': mathrm('eV')})

nanotube_chiral_indices = ['n', 'm']
var_txtstrings.update({'n': 'n', 'm': 'm'})
var_txtunits.update(dict.fromkeys(nanotube_chiral_indices, ''))
var_texunits.update(dict.fromkeys(nanotube_chiral_indices, ''))

#nanotube_chiral_vector = ['Ch']
#nanotube_diameter = ['dt', 'd_t', 'd_tube']

var_texstrings = {}
for varkey, varstr in var_txtstrings.iteritems():
    texvarstr = texstr(' '.join(mathsf2mathrm(varstr).split('$')).strip())
    var_texstrings.update({varkey: texvarstr})
var_texstr = var_texstrings
var_txtstr = var_txtstrings

dimensionless_vars = nanotube_chiral_indices[:]
axis_texlabels = {}
axis_txtlabels = {}
for varkey in var_txtstrings.iterkeys():
    if varkey in dimensionless_vars:
        label = var_texstrings[varkey]
    else:
        label = var_texstrings[varkey] + ' ' + \
            r'$($' + var_texunits[varkey] + r'$)$'
    axis_texlabels.update({varkey: label})

for varkey, var in var_txtstrings.iteritems():
    if varkey in dimensionless_vars:
        label = var
    else:
        label = var + ' ' + r'(' + var_txtunits[varkey] + r')'
    axis_txtlabels.update({varkey: label})

axis_labels = {}
axis_labels['tex'] = axis_texlabels
axis_labels['txt'] = axis_txtlabels

var_strings = {}
var_strings['tex'] = var_texstrings
var_strings['txt'] = var_txtstrings
var_str = var_strings

var_units = {}
var_units['tex'] = var_texunits
var_units['txt'] = var_txtunits
