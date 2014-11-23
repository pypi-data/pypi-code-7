from .config import config

def mutt(contacts):
    '''
    Convert each contact to a mutt alias, using the first email address
    field and (optionally) the first name field.
    '''
    for person, data in config(contacts):
        for key, value in data:
            if key == 'email':
                email = value
            elif key == 'name':
                name = value
        if email != None and name != None:
            yield 'alias %s %s <%s>' % (person, name, email)
        elif email != None and name == None:
            yield 'alias %s <%s>' % (person, email)
