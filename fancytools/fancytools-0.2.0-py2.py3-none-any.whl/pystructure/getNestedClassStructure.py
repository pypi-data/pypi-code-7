'''
Created on 3 Jul 2014

@author: elkb4
'''
import fancytools
from fancytools.fcollections import NestedOrderedDict
import inspect


class GetCallablesInPackage(NestedOrderedDict):
    def __init__(self, mainModule, include_classes=True, include_functions=False ):
        NestedOrderedDict.__init__(self)
        self._include_classes = include_classes
        self._include_functions = include_functions
       # self._nested = nested
        
       # self.l = NestedOrderedDict()
       # self._nameToFunc = {}
       # self._icon_dict = {}
        #print mainModule
        self._mainPath = mainModule.__package__
        self._buildLimitsRecursive('', mainModule, self)
        
    
    
    def _buildLimitsRecursive(self,namePath, module, subSelf):
        for modName in dir(module):
            try:
                #get the module
                mod = eval('%s.%s' %(module.__name__, modName))
                # take only 'public' modules
                if modName[0] != '_':
                    if inspect.ismodule(mod):
                        p = self._mainPath
                        if namePath:
                            p+='.'+namePath.replace(', ','.')[:-1]
                        if mod.__name__.startswith(p):
                            #only create a submenu for folders/modules:
                            if mod.__package__ == mod.__name__:
                                l = subSelf[modName] = NestedOrderedDict()
                            else:
                                #use same menu for all classes of all files on one folder/module
                                l = subSelf
                            self._buildLimitsRecursive(l.path, mod,l)
                    else: 
                        # if object belongs to its module (is not imported)
                        if mod.__module__ == module.__name__:
                            # if object is a class 
                            if ( not self._include_classes or ( self._include_classes and inspect.isclass(mod) ) or 
                            # and/or a function 
                               ( not self._include_functions or ( self._include_functions and inspect.isfunction(mod)) ) ):

                                subSelf[modName] = mod

            except:
                pass
    
    
  #  def _createLambda(self, arg):
        #i dont know why, but if i call lambda in no extra function it wont work
   #     return lambda: self.__call__(value=arg)
    
    
    def buildHirarchy(self, horizontal_operation=None, vertical_operation=None):
        def buildRecursive(obj):
            if isinstance(obj, NestedOrderedDict):
                for key, val in obj.iteritems():
                    if vertical_operation:
                        vertical_operation(key) 
                    buildRecursive(val)
            else:
                if horizontal_operation:
                    horizontal_operation(obj) 
    
        buildRecursive(self)       

    

 

if __name__ == '__main__':
    import sys

    g = GetCallablesInPackage(fancytools, include_functions=True)
    #TODO: debug - soll schoen aussehen und sinn machen
    class printClassStructure(object):
        def __init__(self): 
            self.indent = ''
            self._hor_as_last_called = True

        def hor(self, mod):
            sys.stdout.write("%s%s - " %(self.indent,mod.__name__) )
            self.indent = ''

           # print mod
            self._hor_as_last_called = True
        def vert(self, mod):
            if self._hor_as_last_called:
                print ''
            print "%s-> %s" %(self.indent,mod)
            self.indent += '\t'
            self._hor_as_last_called = False
            
    #TODO: direktzugriff mit g['fcollection']['...] = 
    p = printClassStructure()
    g.buildHirarchy(horizontal_operation=p.hor, 
                    vertical_operation=p.vert)
  #  for i in GetNestedClassStructure(fancytools)._nameToFunc.items():
            #print GetNestedClassStructure(i)