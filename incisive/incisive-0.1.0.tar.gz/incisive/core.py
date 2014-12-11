"""Tiny library for handling csv"""

from __future__ import with_statement

import os
import csv
import itertools


__all__ = ("read_csv", "write_csv", "format_to_csv")


# HELPER FUNCTIONS
def is_type(_type, x):
    try:
        return str(_type(x)) == x
    except ValueError:
        return False


def determine_type(x):
    """Determine the type of x"""
    types = (int, float, str)
    _type = filter(lambda a: is_type(a, x), types)[0]
    return _type(x)


def dmap(fn, record):
    """map for a directory"""
    values = (fn(v) for k, v in record.items())
    return dict(itertools.izip(record, values))


def force_type(_type, x):
    if _type is int:
        return int(float(x))
    else:
        return _type(x)


def apply_types(use_types, guess_type, line):
    """Apply the types on the elements of the line"""
    new_line = {}
    for k, v in line.items():
        if use_types.has_key(k):
            new_line[k] = force_type(use_types[k], v)
        elif guess_type:
            new_line[k] = determine_type(v)
        else:
            new_line[k] = v
    return new_line


# FUNCTIONS
def read_csv(filename, delimiter=",", skip=0, guess_type=True, has_header=True, use_types={}):
    """Read a CSV file
    
    Usage
    -----
    >>> data = read_csv(filename, delimiter=delimiter, skip=skip,
            guess_type=guess_type, has_header=True, use_types={}) 

    # Use specific types
    >>> types = {"sepal.length": int, "petal.width": float}
    >>> data = read_csv(filename, guess_type=guess_type, use_types=types) 

    keywords
    :has_header:
        Determine whether the file has a header or not

    """
    with open(filename, 'r') as f:
        # Skip the n first lines
        if has_header:
            header = f.readline().strip().split(delimiter)
        else:
            header = None

        for i in range(skip):
            f.readline()

        for line in csv.DictReader(f, delimiter=delimiter, fieldnames=header):
            if use_types:
                yield apply_types(use_types, guess_type, line)
            elif guess_type:
                yield dmap(determine_type, line)
            else:
                yield line


def write_csv(filename, header, data=None, rows=None, mode="w"):
    """Write the data to the specified filename
    
    Usage
    -----
    >>> write_csv(filename, header, data, mode=mode)

    Parameters
    ----------
    filename : str
        The name of the file

    header : list of strings
        The names of the columns (or fields):
        (fieldname1, fieldname2, ...)

    data : list of dictionaries (optional)
        [
         {fieldname1: a1, fieldname2: a2},
         {fieldname1: b1, fieldname2: b2},
         ...
        ]

    rows : list of lists (optional)
        [
        (a1, a2),
        (b1, b2),
        ...
        ]

    mode : str (optional)
        "w": write the data to the file by overwriting it
        "a": write the data to the file by appending them

    Returns
    -------
    None. A CSV file is written.

    """
    if data == rows == None:
        msg = "You must specify either data or rows"
        raise ValueError(msg)

    elif data != None and rows != None:
        msg = "You must specify either data or rows. Not both"
        raise ValueError(msg)

    data_header = dict((x, x) for x in header)

    with open(filename, mode) as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=header)
            if mode == "w":
                writer.writerow(data_header)
            writer.writerows(data)
        elif rows:
            writer = csv.writer(f)
            if mode == "w":
                writer.writerow(header)
            writer.writerows(rows)

    print "Saved %s." % filename


def format_to_csv(filename, skiprows=0, delimiter=""):
    """Convert a file to a .csv file"""
    if not delimiter:
        delimiter = "\t"

    input_file = open(filename, "r")

    if skiprows:
        [input_file.readline() for _ in range(skiprows)]
 
    new_filename = os.path.splitext(filename)[0] + ".csv"
    output_file = open(new_filename, "w")

    header = input_file.readline().split()
    reader = csv.DictReader(input_file, fieldnames=header, delimiter=delimiter)
    writer = csv.DictWriter(output_file, fieldnames=header, delimiter=",")
    
    # Write header
    writer.writerow(dict((x, x) for x in header))
    
    # Write rows
    for line in reader:
        if None in line: del line[None]
        writer.writerow(line)
    
    input_file.close()
    output_file.close()
    print "Saved %s." % new_filename
