"""Transactionally write a file to disk"""
import os,logging
log = logging.getLogger( __name__ )

def twrite( filename, content ):
    """Write content to filename, creating directory if it does not exist
    
    Notes:
        Is not race-condition safe wrt multiple writers, as it uses 
        the same filename for the temp file in each write.
        
        Transactionality is Linux specific (os.rename guarantee)
    """
    directory = os.path.dirname( filename )
    if not os.path.exists( directory ):
        log.debug( 'Creating directory: %s', directory )
        os.makedirs( directory )
    tmp = os.path.join( filename+'~' )
    fh = open( tmp, 'wb' )
    if isinstance( content, str ):
        fh.write( content )
    elif isinstance( content, unicode ):
        fh.write( content.encode( 'utf-8' ))
    else:
        for item in content:
            fh.write( item )
    fh.close()
    log.debug( 'Writing file: %s', filename )
    os.rename( tmp, filename )
