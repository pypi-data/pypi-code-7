"""
Buildout recipe interface

GOAL :

* Build shellscripts in "bin/" to dump/load datas
* Be able to accept and extra map to override/add dependancies;
* Be able to give some dependancy names to use even if not detected from the eggs;

This recipe will create two shellscripts, one to dump datas for defined eggs and another to load these dumped datas. The shellscripts will be created in the 'bin' directory.

Use the defined eggs list in your buildout config to find the apps to manage dumps. Be careful that it can't retrieve apps that are not defined in your eggs to install, it will not follow eggs dependancies.

recipe
    Required, fill it with ``emencia-recipe-drdump``.
eggs
    'eggs' variable from buildout, required. Generally you will fill it with ``${buildout:eggs}``.
dump_dir
    Optional, a path to the directory that will contains dumped datas, this is always a relative path from the buildout project. If not defined the dumps dir will be ``dumps``.
dependancies_map
    Required, a path to a JSON file containing datas dependancies map between apps. This can be either a file name existing in Dr Dump or a path (relative or absolute) to an external JSON file.
extra_dependancies
    Optional, a path to a JSON file that will add or overwrite dependancies other the ``dependancies_map`` file. Useful if you want to rewrite some dependancies from a Dr Dump's map file without to duplicate it.
extra_apps
    Optional, a string of app names separated by spaces, that will be used to defined additional apps that can't be retrieved from the installed eggs.
"""
import json, logging, os, zc.buildout, zc.recipe.egg
from drdump import drdump

class DrDumpRecipe(object):
    """
    The buildout recipe's interface for Dr Dump
    """
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.installed_eggs = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        if 'eggs' not in options:
             raise zc.buildout.UserError('"eggs" variable is required.')
        
        if 'dependancies_map' not in options:
             raise zc.buildout.UserError('"dependancies_map" variable is required.')
         
        options.setdefault('dump_dir', 'drdump_dumps')
        options.setdefault('extra_dependancies', '')

    def install(self):
        """
        Called only for the first time the recipe is used
        """
        logging.getLogger(self.name).info('Dr Dump at your service')
        
        return self.rebuild_script()

    def update(self):
        """
        Called after the first time the recipe is used
        """
        logging.getLogger(self.name).info('Dr Dump here, nice to see you again')
        
        return self.rebuild_script()

    def rebuild_script(self):
        eggs = self.options['eggs']
        dependancies_map = self.options['dependancies_map']
        extra_dependancies = self.options['extra_dependancies']
        dump_dir = os.path.join(self.buildout['buildout']['directory'], self.options['dump_dir'])
        map_dir = os.path.join(os.path.dirname(drdump.__file__), 'maps')
        
        #print "eggs:", eggs
        print "dependancies_map:", dependancies_map
        print "dump_dir:", dump_dir
        print "map_dir:", map_dir
        print "extra_dependancies:", extra_dependancies
        print "bin-directory:", self.buildout['buildout']['bin-directory']

        # Check for dump_dir, create it if not exists
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
        
        # Try to find the map file directly with the given value
        if os.path.exists(dependancies_map):
            map_file = dependancies_map
        # Try to find the map file as a filename within the package 'datas' directory
        elif os.path.exists(os.path.join(map_dir, dependancies_map)):
            map_file = os.path.join(map_dir, dependancies_map)
        # Nothing finded
        else:
             raise zc.buildout.UserError('"dependancies_map" file does not exist.')
         
        print "map_file:", map_file
        print
        
        # Get the installed eggs name
        requirements, ws = self.installed_eggs.working_set(['emencia-recipe-drdump'])
        
        #print requirements
        
        AVAILABLE_DUMPS = json.load(open(map_file, "r"))
        
        dump_manager = drdump.DataDumpScriptCLI(AVAILABLE_DUMPS, silent_key_error=True)
        print dump_manager.build_dumpdata(requirements)
        
        return [dump_dir]
        