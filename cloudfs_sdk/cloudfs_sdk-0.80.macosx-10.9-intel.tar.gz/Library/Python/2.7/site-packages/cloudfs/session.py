from private.rest_api_adapter import CloudFSRESTAdapter
from private.utils import set_debug

from user import User
from account import Account
from filesystem import Filesystem
from errors import operation_not_allowed


class Session(object):
    def __init__(self, endpoint, client_id, client_secret):
        self.rest_interface = CloudFSRESTAdapter(endpoint, client_id, client_secret)
        self.admin_rest_interface = None
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret

    # are we associated with an account?
    def is_linked(self, debug=False):
        """ Can this session make requests?
        :param debug:   If true, will print the the request and response to stdout.
        :return:        True if this session is currently authenticated, false otherwise.
        """
        set_debug(self, debug)
        return self.rest_interface.is_linked()

    # set any account credentials to nil
    def unlink(self):
        """ Discard current authentication.
        :return: None
        """
        self.rest_interface.unlink()

    def set_admin_credentials(self, admin_client_id, admin_secret):
        self.admin_rest_interface = CloudFSRESTAdapter(self.endpoint, admin_client_id, admin_secret)

    # currently broken server side. Not recommended for use.
    def create_account(self, username, password, email=None, first_name=None, last_name=None, log_in_after_creation=False, debug=False):
        """Create a user account associated with your CloudFS account.

        Warning: This method is currently broken, and will almost certainly 500. If you're interested, or the method has
        since been fixed server side, call the method with force=true. The request format is not expected to change.

        Note: Although this method creates a User object - the session associated with the user is _not_ linked. You
        must authenticate it before using it.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Create%20Account.html

        :param username:                Username for the user, must be at least 4 characters and less than 256 characters.
        :param password:                Password for the user, must be at least 6 characters and has no length limit.
        :param email:                   Email address for user. Optional.
        :param first_name:              Users' first name. Optional
        :param last_name:               Users' last name. Optional
        :param log_in_after_creation:   If True, will log into the created user account in this session. Optional, defaults to False.
        :param debug:                   If True, will print the the request and response to stdout.
        :return:                        Newly created User object.
        :raise OperationNotAllowed:
        """
        if not self.admin_rest_interface:
            raise operation_not_allowed("Account creation without admin credentials")

        if debug:
            self.admin_rest_interface.debug_requests(1)

        response = self.admin_rest_interface.create_account(username, password, email, first_name, last_name)
        if log_in_after_creation:
            self.authenticate(username, password, debug)
        return User(self.rest_interface.get_copy(),
                    response)

    # link this session to an account
    def authenticate(self, username, password, debug=False):
        """ Attempt to log into the given users' filesystem.
        :param username:    Username of the user.
        :param password:    Password of the user.
        :param debug:       If true, will print the the request and response to stdout.
        :return:            True if successful, False otherwise.
        """
        set_debug(self, debug)
        return self.rest_interface.authenticate(username, password)

    def get_user(self, debug=False):
        """Get an object describing the current user.
        :param debug:   If true, will print the the request and response to stdout.
        :return:        User object representing the current user.
        """
        set_debug(self, debug)

        return User(self.rest_interface.get_copy(),
                    self.rest_interface.user_profile())


    def get_history(self, start=-10, stop=None, debug=False):
        """List previous actions taken by the current user.

        See CloudFSRESTAdapter documentation for notes on using this.

        :param start:       First version number to list. If negative, will be treated as a limit on number of actions. Optional, defaults to -10.
        :param stop:        Version number to stop listing at. Not the count of actions. Optional, defaults to none.
        :return:            List of dictionaries which describe actions on the filesystem.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        set_debug(self, debug)

        return self.rest_interface.action_history(start, stop)

    def get_account(self, debug=False):
        """Get an object describing the current users account.
        :param debug:   If true, will print the the request and response to stdout.
        :return:        Account object representing the current user account.
        """
        set_debug(self, debug)

        return Account(self.rest_interface.get_copy(),
                       self.rest_interface.user_profile())


    def get_filesystem(self):
        """ Get a filesystem object.

        Does not use a request.

        :return: Filesystem object linked to this session.
        """
        return Filesystem(self.rest_interface.get_copy())