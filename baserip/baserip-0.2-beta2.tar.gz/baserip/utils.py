import abc

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Node(object):
    def __init__(self, name=None, parent=None):
        self._name = name
        self._parent = parent
        self._children = []
        if parent is not None:
            parent.addChild(self)

    @property
    def typeinfo(self):
        try:
            return self._nodetype
        except AttributeError:
            return "Node"
            
    @typeinfo.setter
    def typeinfo(self, ntype):
        self._nodetype = ntype

    @property
    def parent(self):
        return self._parent
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True

    def child(self, row):
        try:
            return self._children[row]
        except IndexError:
            return None
    
    def childCount(self):
        return len(self._children)

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

class TrackAdaptor(object):
    def __init__(self, source, device=None):
        self._source = source
        self.device = device
        
    def __getattr__(self, key):
        key = 'ix' if key == 'index' else key
        return self._source[key]

class SourceBase(object, metaclass=abc.ABCMeta):
    def __init__(self, source):
        self._source = source
        
    @property
    @abc.abstractmethod
    def title(self):
        pass
        
    @property
    @abc.abstractmethod
    def path(self):
        pass
        
    @property
    @abc.abstractmethod
    def track_number(self):
        pass

    @property
    @abc.abstractmethod
    def length(self):
        pass

    @property
    @abc.abstractmethod
    def unique_id(self):
        pass

    @property
    @abc.abstractmethod
    def stream_data(self):
        pass

class TrackSource(SourceBase):
    def __init__(self, node):
        super().__init__(node)
        self.video_streams = [TrackAdaptor(node.track, self.path)]
        self.audio_streams = [TrackAdaptor(audio) for audio in node.track['audio']]
        self.subtitle_streams = [TrackAdaptor(subt) for subt in node.track['subp']]
        
    @property
    def title(self):
        return self._source.parent.lsdvd['title']
    
    @property
    def path(self):
        return self._source.parent.lsdvd['device']
        
    @property
    def track_number(self):
        if self.video_streams:
            return self.video_streams[0].index
        return 0

    @property
    def length(self):
        if self.video_streams:
            return max(stream.length for stream in self.video_streams)
        return 0

    @property
    def unique_id(self):
        return self._source.unique_id

    @property
    def stream_data(self):
        return self._source.stream_data()

if __name__ == '__main__':
    class MyClass(metaclass=Singleton):
        pass
        
    print(MyClass() is MyClass())
    
