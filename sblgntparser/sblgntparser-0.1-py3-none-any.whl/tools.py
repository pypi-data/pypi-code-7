import logging
log = logging.getLogger(__name__)

from pathlib import Path

def filelist(folderpath, ext=None, flat=True):
    '''
    Returns a list of all the files contained in the folder specified by `folderpath`.
    To filter the files by extension simply add a list containing all the extension with `.` as the second argument.
    If `flat` is False, then the Path objects are returned.
    '''
    path = Path(folderpath)
    if not ext:
        ext = []
    if path.exists() and path.is_dir():
        if flat:
            return [ str(f) for f in path.iterdir() if f.is_file() and f.suffix in ext ]
        else:
            return [ f for f in path.iterdir() if f.is_file() and f.suffix in ext ]
    else:
        log.warn('Nothing found in "{}"'.format(str(folderpath)))
