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
import functools

from cqrs.command import Command
from cqrs.command import CommandAttribute
from cqrs.command import CommandParameter
from cqrs.command import CommandValidationError
from cqrs.command import CommandInspector
from cqrs.gateway import IGateway
from cqrs.exceptions import MissingCommandHandler
from cqrs.exceptions import UnprocessableCommandException
from cqrs.exceptions import CommandDeserializationError
from cqrs.exceptions import InvalidCommandParameter
from cqrs.exceptions import InvalidCommandParameters
from cqrs.exceptions import GatewayNotResponding
from cqrs.exceptions import GatewayRejectedCommand
from cqrs.exceptions import DuplicateCommand
from cqrs.exceptions import UnknownCommand
from cqrs.exceptions import InvalidRequestData
from cqrs.handler import CommandHandler


def get_version():
    return '1.0.0'
