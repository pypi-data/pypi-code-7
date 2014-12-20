# -*- coding: utf-8 -*-
import os
import shutil
import sys

class PathStr(str):
    '''
    easy path-string handling and manipulation using o.spath and shutil
    
    >>> p = PathStr.home()
    >>> print p.isdir()
    True
    >>> print p.exists()
    True
    >>> d_list = [p.join(x) for x in p.listdir()]
    '''

    def __new__(cls,value):
        '''transform / to \ depending on the os'''
        obj = str.__new__(cls, os.path.normpath(str(value)))
        return obj


    @staticmethod
    def home():
        '''return the hode/user directory'''
        return PathStr(os.path.expanduser("~"))
    

    @staticmethod
    def getcwd(moduleName=None):
        '''
        get current path either from the temp folder used by pyinstaller:
        
            * apps 'sys._MEIPASS' if packed with --onefile option
        
        or
        
            * os.getcwd()
        '''
        try:
            p = PathStr(sys._MEIPASS)
            if moduleName != None:
                #pyinstaller create one temp folder
                #to separate e.g. media directories from each package it is usefull
                #to build its file-tree like this /temp/[mainPackage]/
                #to get the main package PathStr need a derived instance
                return p.join(moduleName.split('.')[0])
            return p
        except AttributeError:
            return PathStr(os.getcwd())

    def join(self, *args):
        '''add a file/name to this PathStr instance'''
        return PathStr(os.path.join(self,*args))


    def exists(self):
        '''return whether PathStr instance exists as a file/folder'''
        return os.path.exists(self)


    def abspath(self):
        return PathStr.join(PathStr.getcwd(), self)


    def load(self, size):
        '''open and read the file is existent'''
        if self.exists() and self.isfile():
            return eval( open(self).read(size) )


    def dirname(self):
        return PathStr(os.path.dirname(self))


    def basename(self):
        return PathStr(os.path.basename(self))


    def move(self, dst):
        '''move this file/folder the [dst]'''
        shutil.move(self, dst)
        self = PathStr(dst).join(self.basename())
        return self

    def mkdir(self, dname=None):
        if dname == None:
            n = self
        else:
            n = self.join(dname)
        if not n.exists():
            os.mkdir(n)
        return n


    def rename(self, newname):
        newname = self.dirname().join(newname)
        os.rename(self, newname)
        self = PathStr(newname)

    def remove(self, name=None):
        f = self
        if name:
            f = self.join(name)
        try:
            os.remove(f)
        except OSError:
            shutil.rmtree(f)


    def filetype(self):
        if '.' in self:
            return self.split('.')[-1]
        return ''


    def setFiletype(self, ftype):
        if '.' in self:
            s = self[:self.index('.')]
        else:
            s = self
        return s + '.' + ftype


    def isfile(self):
        return os.path.isfile(self)


    def isdir(self):
        return os.path.isdir(self)


    def listdir(self):
        if os.path.isdir(self):
            d = self
        else:
            d = os.path.dirname(self)
        return os.listdir(d)


    def __iter__(self):
        #TODO: iter and listdir as generator object
        if self.exists():
            return iter(self.listdir())
        return iter([])




if __name__ == "__main__":
    import doctest
    doctest.testmod()