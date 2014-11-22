from vaitk import core
import collections

class LineMeta:
    def __init__(self, meta_type, document):
        self._meta_type = meta_type
        self._document = document
        self._document.registerLineMeta(self)
        self._data = [None] * self._document.numLines()
        
        self.contentChanged = core.VSignal(self)
        
    def addLines(self, line_number, how_many):
        for i in range(how_many):
            self._data.insert(line_number-1, None)
    
    def deleteLines(self, line_number, how_many):
        for i in range(how_many):
            self._data.pop(line_number-1)
        
    def setData(self, from_line, data):
        if not isinstance(data, collections.Iterable) or isinstance(data, str):
            data = [ data ]
            
        try:
            for idx, d in enumerate(data):
                self._data[from_line-1+idx] = d
        except IndexError:
            pass
            
        self.notifyObservers()
    
    def clear(self):
        self._data = [None] * self._document.numLines()
        self.notifyObservers()
    
    def notifyObservers(self):
        self.contentChanged.emit()
        
    @property
    def meta_type(self):
        return self._meta_type
    
