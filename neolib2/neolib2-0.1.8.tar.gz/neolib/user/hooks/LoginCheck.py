from neolib.user.hooks.Hook import Hook
from neolib.Exceptions import UserLoggedOut


class LoginCheck(Hook):
    """A hook for grabbing the user's neopoints and active pet"""

    _log_name = 'neolib.user.hooks.LoginCheck'

    def __init__(self):
        super().__init__()

    def execute(self, usr, pg):
        """A hook for checking if a user was logged out"""
        # First make sure we were already logged in
        if usr.logged_in:
            # Check the page for login content
            if 'welcomeLoginButton' in pg.content:
                self._logger.warning('User ' + usr.username + ' was logged out!')
                self._logger.warning('Attempting courtesy relogin attempt..')

                try:
                    if usr.login():
                        self._logger.warning('User ' + usr.username + ' logged in')
                    else:
                        raise UserLoggedOut('User ' + usr.username + ' was unable to log back in')
                except Exception:
                    self._logger.exception('User ' + usr.username + ' was unable to log back in')
