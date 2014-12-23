"""
Command-Query Responsibility Segregation framework (CQRS). Separates
destructive operations from non-destructive (read) operations; CQRS
is "the creation of two objects where there was previously one.
The separation occurs based upon whether the methods are a command
or a query." (Greg Young).

Example commands:
- Update the state of a relation in a relational database.
- Create a directory on a filesystem.

Example queries:
- Get a result set for a query on a relational database.
- Read the contents of a directory on a filesystem.
"""


def get_version():
    return '1.1.0'
