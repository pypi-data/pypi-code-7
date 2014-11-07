from .model import Base, engine, StreamGage, SessionMaker


def init_primary(first_time):
    """
    An example persistent store initializer function
    """

    # Create tables
    Base.metadata.create_all(engine)

    # First time add data
    if first_time:
        # Make a session
        session = SessionMaker()

        # Create StreamGage objects
        provo = StreamGage(name='Provo River Near Provo', lat=40.23833, lon=-111.6975)
        woodland = StreamGage(name='Lower River Near Woodland', lat=40.557778, lon=-111.181111)

        # Add to the session and commit
        session.add(provo)
        session.add(woodland)
        session.commit()