# -*- coding: utf-8 -*-
"""
============================================================================
Functions for data manipulation (:mod:`pksci.tools.datautils._datafuncs`)
============================================================================

.. currentmodule:: pksci.tools.datautils._datafuncs

"""
from __future__ import division, print_function, absolute_import

import re
from collections import OrderedDict

import numpy as np

__all__ = ['generate_sequence', 'inv_map', 'load_data',
           'load_fixed_width_data', 'sequence_elements']


sequence_elements = ('si', 'sf', 'ds')


#def get_nearest_neighbor_counts(adata=None, datafile=None,
#                                filter_elements=None, invert=False):
#    if adata is not None:
#        atom_data = adata
#    elif datafile is not None and isinstance(datafile, str):
#        atom_data = get_atom_data_asarray(datafile)
#
#    #atom_ids = get_atom_ids_asarray(adata=atom_data)
#
#    filtered_coords = \
#        get_filtered_coords(adata=atom_data, filter_elements=vacIDs)
#    NNtree = spatial.KDTree(filtered_coords)
#    print(NNtree.data)
#
#    # compute things like the distance for which 50% of vacancies
#    # lie within a distance r of each other, etc.
#
#    #return None
#    pass

#def get_nearest_neighbor_comp_array_dict(vacIDs):
#    nearest_neighbor_comp_dict = OrderedDict()
#    vac_coords = \
#         get_filtered_coords(adata=self.atom_data, filter_elements=vacIDs)
#    #vac_coords = self.get_filtered_coords(vacIDs)
#    for comp in self.position_components:
#        vac_distances = self.get_vac_distances(vac_coords, comp)
#        nearest_neighbor_array = vac_distances[np.where(vac_distances == \
#                                                        vac_distances.min())]
#        nearest_neighbor_comp_dict[comp] = nearest_neighbor_array
#
#    return nearest_neighbor_comp_dict

def generate_sequence(si=None, sf=None, ds=None, dtype=int, stype=list,
                      NoneifNone=False):
    """Generate a sequence based on start, stop, step parameters.

    Parameters
    ----------
    si : int
    sf : int
    ds : int
    dtype : type, optional
    stype : type, optional

    Returns
    -------
    seq

    """

    try:
        seq = np.arange(si, sf + ds, ds, dtype=dtype).tolist()
    except TypeError:
        try:
            si, sf, ds = \
                dtype(float(si)), dtype(float(sf)), dtype(float(ds))
            seq = np.arange(si, sf + ds, ds, dtype=dtype).tolist()
        except (TypeError, ValueError):
            try:
                si, sf = dtype(float(si)), dtype(float(sf))
                seq = np.arange(si, sf + 1, dtype=dtype).tolist()
            except (TypeError, ValueError):
                try:
                    sf = dtype(float(sf))
                    seq = np.arange(sf + 1, dtype=dtype).tolist()
                except (TypeError, ValueError):
                    try:
                        seq = [dtype(float(si))]
                    except (TypeError, ValueError):
                        if NoneifNone:
                            seq = None
                        else:
                            seq = [None]
    finally:
        return seq


def load_data(fname, numbersonly=False, headerlines=None, mincols=None,
              skip_blank_lines=True, skiplinesbeforeheader=None,
              skiplinesafterheader=None, skiplines=None, startlinestr=None,
              delimit_header_space=False, tab_delimited=False,
              skip_lines_starting_with=None):
    """Load data from file.

    Parameters
    ----------
    fname : str
        input file
    skiplines : int
        number of lines to skip
    mincols : int
        number of data columns to look for
    headerlines : int
        number of headerlines to look for and extract
    startlinestr : str
        string used to indicate last line of text before start of data

    Returns
    -------
    data : ndarray
        header is a list of str names denoting the variables in the file.
        data is a list of floats for each line of data in the file.

    """
    header = []
    with open(fname) as f:
        if skiplines is not None:
            linecount = 0
            while linecount < skiplines:
                f.readline().strip()
                linecount += 1

        if skiplinesbeforeheader is not None:
            linecount = 0
            while linecount < skiplinesbeforeheader:
                f.readline().strip()
                linecount += 1

        if headerlines is not None:
            linecount = 0
            while linecount < headerlines:
                #line = f.readline().strip().split()
                line = f.readline().strip()
                if skip_lines_starting_with is not None and \
                        line.startswith(skip_lines_starting_with):
                    continue
                if tab_delimited:
                    s = re.split('\t*', line)
                else:
                    if delimit_header_space:
                        s = re.split(',*\s{2,}\t*', line)
                    else:
                        s = re.split(',*\s*\t*', line)

                if len(s) != 1:
                    header.append(s)
                    linecount += 1
                elif len(s) == 1 and not skip_blank_lines:
                    header.append(None)
                    linecount += 1

        if skiplinesafterheader is not None:
            linecount = 0
            while linecount < skiplinesafterheader:
                f.readline().strip()
                linecount += 1

        if startlinestr is not None:
            line = f.readline().strip()
            while line != startlinestr:
                line = f.readline().strip()

        lines = f.readlines()
        data = []
        for line in lines:
            if skip_lines_starting_with is not None and \
                    line.startswith(skip_lines_starting_with):
                continue

            s = re.split(',*\s*\t*', line.strip())

            if len(s) != 1:
                if mincols is not None and len(s) >= mincols:
                    endcol = mincols
                else:
                    endcol = len(s)
                tmp = []
                for x in s[:endcol:]:
                    try:
                        tmp.append(float(x))
                    except ValueError:
                        if numbersonly:
                            continue
                        else:
                            tmp.append(x)
                data.append(tmp)
            elif len(s) == 1 and not skip_blank_lines:
                data.append(None)

        data = np.asarray(data)
        if headerlines is not None:
            if headerlines == 1:
                return (header[0], data)
            else:
                return (header, data)
        else:
            return (None, data)


def load_fixed_width_data(fname, dtype=None, colwidths=None, comments='#',
                          skiprows=0, skip_header=0, skip_footer=0,
                          converters=None, missing_values=None,
                          filling_values=None, usecols=None, names=None,
                          autostrip=True, colsep=4):
    """Load data from file formatted with fixed width columns.

    Parameters
    ----------
    fname : file or str
    dtype : dtype, optional
    colwidths : sequence, optional
        a list of integers of column widths
    comments : str, optional
    skiprows : int, optional
    skip_header : int, optional
    skip_footer : int, optional
    converters : variable, optional
    missing_values : variable, optional
    filling_values : variable, optional
    usecols : sequence, optional
    names : {None, True, str, sequence}, optional
    autostrip : bool, optional
    colsep : int, optional

    Returns
    -------
    headers, txtdata : {sequence, array_type}


    """
    kwargs = {'dtype': dtype, 'comments': comments,
              'delimiter': colwidths, 'skiprows': skiprows,
              'skip_header': skip_header, 'skip_footer': skip_footer,
              'converters': converters, 'missing_values': missing_values,
              'filling_values': filling_values, 'usecols': usecols,
              'names': names, 'autostrip': autostrip}

    headers = []
    # define regex pattern to split column data by
    colws = '\s{' + '{!s}'.format(colsep) + ',}'
    with open(fname) as f:
        line = f.readline().strip()
        s = re.split(colws, line)
        for ss in s:
            headers.append(ss)

        if colwidths is None:
            colwidths = []
            # in order for the `colwidths` list to be populated with
            # the correct widths, the line following the column headers
            # *must* be non-whitespace characters appearing as 'underlines'
            # of the column headers. The underlines must be n-length
            # strings separated by m-whitespace characters, where
            # n = width of column appended to `colwidths` list and
            # m = `colsep`
            line = f.readline().rstrip()
            s = re.split(colws, line)
            for ss in s:
                colwidth = len(ss) + colsep
                colwidths.append(colwidth)

            # update kwargs['delimiter'] with colwidths list
            kwargs['delimiter'] = colwidths

    txtdata = np.genfromtxt(fname, **kwargs)
    return headers, txtdata


def inv_map(d, unique=True, ordered=False):
    """Generate inverse dictionary for ``d``, mapping values to keys.

    .. note::

       This function is suitable even when values in ``d`` are not unique.

    Parameters
    ----------
    d : dict to generate inverse of
    unique : bool, optional
        if ``True``, it assumes all values in ``d`` are unique and
        generates the inverse map using Python's efficient dict
        comprehension.
        if ``False``, the values in ``inv_map`` will be ``lists``.
    ordered : bool, optional
        if ``True``, use an :py:class:`python:OrderedDict`
        for the inverse mapping. Is of no use unless the input
        dictionary is also an :py:class:`python:OrderedDict`.

    Returns
    -------
    inv_map : dict

    """
    if unique:
        if ordered:
            inv_map = OrderedDict((v, k) for k, v in d.iteritems())
        else:
            inv_map = {v: k for k, v in d.iteritems()}
    else:
        if ordered:
            inv_map = OrderedDict()
        else:
            inv_map = {}
        for k, v in d.iteritems():
            inv_map.setdefault(v, []).append(k)
    return inv_map
