#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Main class, parse args and send request
#
# Author: Kevin Hu


import os
import glob
from optparse import OptionParser

from urlrequest import RequestURL
from config import *


class Ubuntupaste():
    """
    Main class for Ubuntupaste script
    """

    # parse argument
    def parseargs(self):
        """
        parse argument, and return config
        param: list of argv except executable name
        return: config table containing
            typename -t
            open browser -b
        """
        usage = "Usage: <up> [OPTION]... FILENAME..."
        parser = OptionParser(usage = usage)
    
        # Add typename option
        parser.add_option("-t", "--type",
                          dest="type", help="specify type of target file")
    
        # Add open browser option
        parser.add_option("-b", "--browser",
                          action="store_true", dest="browser",
                          help="open response url in browser")
    
        return parser
    
    
    # Find type of the file
    def findtype(self, filename, suffix_match):
        """
        param: filename
        return: type string
        """
        if (filename.lower().startswith("makefile")):
            return "make"
    
        if (filename.lower() == "cmakelist.txt"):
            return "cmake"
    
        fs = filename.split(".")
        if len(fs) == 1:
            return "text"
    
        suffix = (fs[-1]).lower()
    
        if suffix not in suffix_match.keys():
            return "text"
    
        return suffix_match[suffix]
    
    
    # The main function
    def run(self):
        """
        The main function
        """
        # read options and args
        parser = self.parseargs()
        (options, args) = parser.parse_args()
        if (args == []):
            parser.print_help()
            exit()
    
        filetype = None
        if options.type:
            filetype = options.type
    
        # open and read in all files
        totalsize = 0
        allfiles = []
        for f in args:
            for g in glob.iglob(f):
                try:
                    allfiles.append( open(g, "r").read() )
                    totalsize += os.stat(g).st_size
    
                    # protector for file size
                    if totalsize > TOTALSIZE:
                        print("Over size limit, please send one at a time")
                        exit()
    
                    # protector for different file type
                    if not filetype:
                        filetype = self.findtype(g, SUFFIX)
    
                except Exception as e:
                    print(e)
                    print("Error opening file")
                    # protector if overall size too large
    
        # DEBUG
        # print(allfiles)
        # print(filetype)
        # print(totalsize)
    
        # send the request
        content = {"poster": os.environ["USER"],
                   "syntax": filetype,
                   "content": ('\n' * 8).join(allfiles)}
    
        req = RequestURL(content)
        resp = req.send()
    
        print(resp.url)
    
        # Option to open the browser
        if (resp.url != None):
            if (options.browser):
                try:
                    import webbrowser
                    webbrowser.open(resp.url)
                except Exception as e:
                    print(e)
                    print("Could not open browser. Please copy and paste in browser")
                    exit()
    
        

