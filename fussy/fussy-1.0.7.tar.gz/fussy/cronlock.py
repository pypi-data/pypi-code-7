"""Provide a cron lock for preventing cron-bombs and the like"""
import os, logging, fcntl, errno, signal, tempfile, time
log = logging.getLogger( __name__ )

class Busy( IOError ):
    """Raised if the lock is held by another cronlock"""
class Timeout( RuntimeError ):
    """Raised if the timeout signal triggers"""
    
class Flock( object ):
    """A context manager that just flocks a file"""
    file = None
    def __init__( self, filename ):
        self.filename = filename 
    def __str__( self ):
        return '%s( %r )'%( self.__class__.__name__, self.filename )
    def __enter__( self ):
        if self.file:
            raise Busy( """Attempted to lock the %s twice"""%( self ))
        fh = open( self.filename, 'a+' )
        try:
            fcntl.flock( fh, fcntl.LOCK_EX|fcntl.LOCK_NB ) # can raise IOError 
        except IOError as err:
            if err.errno == errno.EWOULDBLOCK:
                other_pid = None
                if os.path.exists(self.filename):
                    try:
                        other_pid = open(self.filename).read()
                    except Exception:
                        pass
                err = Busy( *(err.args + (other_pid, )) )
                err.errno = errno.EWOULDBLOCK
            raise err
        fh.seek( 0 ) # rewind to start...
        self.file = fh
        return fh
    def __exit__( self, *args ):
        try:
            fh = self.__dict__.pop( 'file' )
        except KeyError:
            pass
        else:
            os.remove(self.filename)
            fcntl.flock( fh, fcntl.LOCK_UN )
            fh.close()
    def write( self, *args ):
        with self:
            self.file.write( *args )
            self.file.flush()
    def read( self, *args ):
        with self:
            self.file.read( *args )

class Lock( object ):
    """A Context manager that provides cron-style locking"""
    def __init__( self, lockfile ):
        """Create a lock file 
        
        name -- used to construct the lock-file name 
        directory -- directory in which to construct the lock-file 
        """
        self.flock = Flock( lockfile )
    @property 
    def pid( self ):
        return os.getpid()
    def __enter__( self ):
        self.flock.__enter__()
        self.flock.file.write( str( self.pid ))
        self.flock.file.flush()
    def __exit__( self, *args ):
        self.flock.__exit__(*args)
    def on_timeout( self, *args, **named ):
        raise Timeout( "Maximum run-time exceeded, aborting" )
    def set_timeout( self, duration ):
        """Set a signal to fire after duration and raise an error"""
        signal.signal( signal.SIGALRM, self.on_timeout )
        signal.alarm( int(duration) )

class BlockingLock( Lock ):
    """Lock class that blocks for up to lock_wait seconds waiting for other process to exit"""
    def __init__( self, lockfile, lock_wait=5 ):
        super( BlockingLock, self ).__init__( lockfile )
        self.lock_wait = lock_wait
    def __enter__( self ):
        abort = time.time() + self.lock_wait
        while time.time() < abort:
            try:
                return super( BlockingLock, self ).__enter__()
            except Busy:
                time.sleep( self.lock_wait / 20. )
        raise Busy( "Lock on %s timed out"%( self.flock.filename ))

def with_lock( name, directory=None, timeout=None ):
    """Decorator that runs a function with Lock instance acquired
    
    * name -- basename of the file to create 
    * directory -- if specified, the directory in which to store files, 
        defaults to tempfile.gettempdir()
    * timeout -- if specified, the number of seconds to allow before raising 
        a Timeout error
    """
    if directory is None:
        directory = tempfile.gettempdir()
    filename = os.path.join( directory, name )
    lock = Lock( filename )
    def wrap_func( function ):
        """Wraps the function execution with our lock"""
        def wrapped_with_lock( *args, **named ):
            with lock:
                if timeout:
                    lock.set_timeout( timeout )
                return function( *args, **named )
        wrapped_with_lock.__name__ = function.__name__
        wrapped_with_lock.__doc__ = function.__doc__
        wrapped_with_lock.__dict__ = function.__dict__
        wrapped_with_lock.lock = lock 
        return wrapped_with_lock
    return wrap_func
