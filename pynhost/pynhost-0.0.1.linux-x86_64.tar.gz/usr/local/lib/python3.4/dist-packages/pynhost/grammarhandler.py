import os
import obj
import re
import inspect
import sys
import subprocess
import os
import utilities
import matching

class GrammarHandler:
    def __init__(self):
        self.modules = {}

    def load_grammars(self):
        for root, dirs, files in os.walk('grammars'):
            path = root.split('/')
            for filename in files:
                if filename.endswith('.py') and filename.replace('.', '').isalnum():
                    path = os.path.join(root, filename).replace('/', '.')[:-3]
                    module = __import__(path, fromlist=['grammars'])
                    self.modules[module] = self.extract_grammars_from_module(module)
   
    def extract_grammars_from_module(self, module):
        clsmembers = inspect.getmembers(sys.modules[module.__name__], inspect.isclass)
        grammars = []
        for member in clsmembers:
            # screen for objects with obj.GrammarBase ancestor
            if obj.GrammarBase == inspect.getmro(member[1])[-2]:
                grammars.append(member[1]())
                obj.set_rules(grammars[-1])
        return grammars

    def get_matching_rule(self, words):
        proc = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname'])
        window_name = proc.decode('utf8').rstrip('\n')
        result = {'rule': None, 'new words': None, 'remaining words': words}
        for module_obj in self.modules:
            split_name = module_obj.__name__.split('.')
            if len(split_name) == 2 or re.search(split_name[1], window_name):
                for grammar in [m for m in self.modules[module_obj] if m._is_loaded()]:
                    for rule in grammar.rules:
                        new, remaining = matching.words_match_rule(rule, result['remaining words'])
                        if new:
                            result['new words'] = new
                            result['remaining words'] = remaining
                            result['rule'] = rule
                            return result
        result['remaining words'] = []
        return result
