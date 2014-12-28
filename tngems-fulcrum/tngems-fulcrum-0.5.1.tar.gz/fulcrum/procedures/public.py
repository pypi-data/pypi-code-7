from fulcrum.procedures.base import StoredProcedure


set_session_authorization = StoredProcedure('public',
    'set_session_authorization', rtype=None)
