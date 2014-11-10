# -*- coding: utf-8 -*-
"""Recipe eggpath"""

import logging
from zc.recipe.egg import Egg
import os

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)
        self.egg = Egg(buildout, options['egg'], options)

        self.path = ''
        self.egglocation = ''
        options['path'] = ''
        options['egglocation'] = ''
        requirements, ws = self.egg.working_set()
        
        for k,v in ws.by_key.items():            
            if k == options['egg'] or k.replace('-', '_') == options['egg']:
                loc = [v.location]
                if os.path.isdir(v.location):
                    #not zipped package, append egg name
                    loc.extend(options['egg'].split('.'))
                self.path = os.path.join(*loc)
                self.egglocation = v.location
                options['path'] = self.path
                options['egglocation'] = self.egglocation 
        self.logger.info(self.path)
        
    def install(self):
        """Installer"""
        return tuple()

    def update(self):
        """Updater"""
        pass
