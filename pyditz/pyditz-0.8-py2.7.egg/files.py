"""
File utilities.
"""

import sys
import yaml
import codecs
import six

from datetime import datetime

from .config import config


def read_yaml(fp):
    "Read YAML data from a stream."
    return yaml.safe_load(fp)


def read_yaml_file(path):
    "Read YAML data from a file."

    with codecs.open(path, "r", encoding='utf-8') as fp:
        return read_yaml(fp)


def read_object(fp):
    """
    Read a YAML object from a stream and validate it.
    """

    obj = read_yaml(fp)
    obj.validate()

    return obj


def read_object_file(path):
    """
    Read a YAML object from a file and validate it.
    """

    obj = read_yaml_file(path)
    obj.validate()

    return obj


def write_yaml(item, fp=None, parent=None, level=0):
    """
    Write YAML data to a stream.
    """

    # This should be using PyYAML's write function, but I can't get it to
    # write things the way I want -- i.e., reproduce the format that
    # rubyditz uses.  And datetimes don't get written in a format that
    # rubyditz can read back again.  Sigh.

    # This function is ghastly and evil, and shouldn't exist.  But it gets
    # the job of roundtripping done.

    if fp is None:
        fp = sys.stdout

    value = six.text_type(item)
    tag = getattr(item, "yaml_tag", None)
    indent = "  "

    if tag:
        fp.write(tag + " \n")
        seenref = False
        for attr in item.attributes:
            if attr == "id" and not seenref:
                fp.write("\n")

            fp.write(indent * (level - 1))
            fp.write("%s: " % attr)
            obj = getattr(item, attr)

            if obj and attr == "references":
                seenref = True

            write_yaml(obj, fp, item, level + 1)
    elif isinstance(item, dict):
        if parent:
            fp.write("\n")

        for key, obj in sorted(item.items()):
            fp.write(indent * (level - 1))
            fp.write("%s: " % key)
            write_yaml(obj, fp, item, level + 1)
    elif isinstance(item, list):
        if len(item) > 0:
            newline = doindent = not isinstance(parent, list)

            # This is a gross hack.  Look away now.
            if hasattr(parent, "ditz_tag") and level > 1:
                level -= 1

            if newline:
                fp.write("\n")

            for obj in item:
                if doindent:
                    fp.write(indent * (level - 1))
                else:
                    doindent = True

                fp.write("- ")
                write_yaml(obj, fp, item, level + 1)
        else:
            fp.write("[]\n")
    elif isinstance(item, datetime):
        fp.write("%s Z\n" % six.text_type(item))
    elif "\n" in value:
        fp.write("|-\n")

        if isinstance(parent, list) and level > 1:
            level -= 1

        for line in value.split("\n"):
            fp.write(indent * level)
            fp.write(line + "\n")
    elif item is None:
        fp.write("\n")
    else:
        quote = False
        if not value:
            quote = True
        elif value[0] in '"{}[]':
            quote = True
        elif value[0] != ':' and ":" in value:
            quote = True
        elif '#' in value:
            quote = True
        else:
            try:
                float(value)
                quote = True
            except ValueError:
                pass

        if quote:
            value = '"' + value.replace('"', r'\"') + '"'

        fp.write(value + "\n")


def write_config(conf, dirname="."):
    """
    Write Ditz config file if required.
    """

    if config.getboolean('config', 'create_ditz_config'):
        conf.write(dirname)
        return True

    return False
