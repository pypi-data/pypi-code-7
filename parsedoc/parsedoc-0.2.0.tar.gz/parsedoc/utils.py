"""Various utilities for the library"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os.path


logger = logging.getLogger(__name__)


def create_index(output_dir, relative_dir_path, dirnames, filenames):
    """Create an index file for a directory"""

    logger.info("Creating index of directory {}".format(relative_dir_path))

    with open(os.path.join(output_dir, relative_dir_path, 'index.md'),
              'w') as f:
        f.write("# {}\n\n".format(relative_dir_path))

        if len(filenames) == 0 and len(dirnames) == 0:
            f.write("This directory is empty")
            return

        if len(dirnames) > 0:
            f.write("## Subdirectories\n")
            for dirname in dirnames:
                f.write("* {}\n".format(dirname))

        if len(filenames) > 0:
            f.write("\n## Files\n")
            for filename in filenames:
                f.write("* {}\n".format(filename))
