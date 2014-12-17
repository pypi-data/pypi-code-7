# Absolute import (standard in Python 3) imports dicom from pydicom
# rather than the parent module.
from __future__ import absolute_import
import os
import re
import operator
from dicom import datadict
from qiutil.logging import logger
from . import (reader, writer)

# Uncomment to debug pydicom.
# import dicom
# dicom.debug(True)

def select(ds, *tags):
    """
    Reads the given DICOM dataset tags.
    
    :param ds: the pydicom dicom object
    :param tags: the names of tags to read (default all unbracketed tags)
    :return: the tag name => value dictionary
    """
    if not tags:
        # Skip tags with a bracketed name.
        tags = (de.name for de in ds if de.name[0] != '[')
    tdict = {}
    for t in tags:
        try:
            # The tag attribute.
            tattr = re.sub('\W', '', t)
            # Collect the tag value.
            tdict[t] = operator.attrgetter(tattr)(ds)
        except AttributeError:
            pass
    
    return tdict


def edit(*in_files, **opts):
    """
    Sets the tags of the given DICOM files.

    :param in_files: the input DICOM files or directories containing
        DICOM files
    :param opts: the DICOM header (I{name}, I{value}) tag values to set
        and the following option:
    :return: the modified file paths
    """
    dest = opts.pop('dest', None)
    # The {tag: value} dictionary.
    tv = {datadict.tag_for_name(t.replace(' ', ''))
                          : v for t, v in opts.iteritems()}
    # The {tag: VR} dictionary.
    tvr = {t: datadict.get_entry(t)[0] for t in tv.iterkeys()}

    # Edit the files
    logger(__name__).info("Editing the DICOM files with the following tag"
                          " values: %s..." % tag_values)
    for ds in writer.edit(*in_files):
        # Set the tag values.
        for t, v in tv.iteritems():
            if t in ds:
                ds[t].value = v
            else:
                ds.add_new(t, tvr[t], v)

    # The output file path formatter.
    format_out_file = lambda f: os.path.join(dest, os.path.split(f)[1])

    # Return the output file paths.
    return [format_out_file(f) for f in in_files]
