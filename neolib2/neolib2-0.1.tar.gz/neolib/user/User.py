import requests

from neolib.Exceptions import NeopetsOffline
from neolib.http.Page import Page
from neolib.inventory.SDBInventory import SDBInventory
from neolib.inventory.UserInventory import UserInventory
from neolib.NeolibBase import NeolibBase
from neolib.shop.UserBackShop import UserBackShop
from neolib.user.Bank import Bank
from neolib.user.hooks.UserDetails import UserDetails
from neolib.user.Profile import Profile


class User(NeolibBase):
    """Represents a Neopets user account

    This is the one class that ties most of the library together. Every object
    that inherits the library's base class has a dedicated attribute for
    holding a User object. This class should be used as the representation of
    the Neopets user account and all actions involving the account should
    reference this class.

    Attributes
       | **username**: The account username
       | **password**: The account password
       | **pin**: The pin number for the account if applicable

       | **session**: The HTTP session for the account

       | **neopoints**: The number of neopoints the user has on hand

       | **active_pet**: :class:`.Neopet` object representing the user's active pet

       | **profile**: :class:`.Profile` object representing the user's account profile
       | **mail**: :class:`Neomail` object for interacting with the user's neomail

       | **inventory**: :class:`UserInventory` object representing the user's inventory
       | **sdb**: :class:`SDB` object representing the user's safety deposit box
       | **shop**: :class:`UserShop` object representing the user's shop
       | **bank**: :class:`Bank` object representing the user's bank

       | **trades**: :class:`TradingPost` object for interacting with the user's trades
       | **auctions**: :class:`AuctionHouse` object for interacting with the user's auctions

       | **hooks**: A list of :class:`Hook` based classes that will be executed
            after requesting a page
    """

    username = ''
    password = ''
    pin = ''

    session = ''

    neopoints = 0

    active_pet = None

    _profile = None
    mail = None

    _inventory = None
    _SDB = None
    _shop = None
    _bank = None

    trades = None
    auctions = None

    hooks = []

    _last_page = ''

    _log_name = 'neolib.user.User'

    _urls = {
        'index': 'http://www.neopets.com/',
    }

    @property
    def profile(self):
        if not self._profile:
            self._profile = Profile(self)
            self._profile.load()

        return self._profile

    @property
    def inventory(self):
        if not self._inventory:
            self._inventory = UserInventory(self)
            self._inventory.load()

        return self._inventory

    @property
    def SDB(self):
        if not self._SDB:
            self._SDB = SDBInventory(self)
            self._SDB.load()

        return self._SDB

    @property
    def shop(self):
        if not self._shop:
            self._shop = UserBackShop(self)
            self._shop.load()

        return self._shop

    @property
    def bank(self):
        if not self._bank:
            self._bank = Bank(self)
            self._bank.load()

        return self._bank

    def __init__(self, username, password='', pin=None):
        """Initializes the user with the given username, password, and pin

        Args:
            | **username**: The username for the account
            | **password**: The password for the account
            | **pin**: Optional pin number for the user's account
        """
        # Initialize parent
        super().__init__()

        # Set username and password
        self.username, self.password = username, password

        # Grab the pin if available
        self.pin = pin if pin else None

        # Initialize session
        self.session = requests.session()

        # Setup default hooks
        self.add_hook(UserDetails)

    def login(self):
        """Performs a login and returns the result

        This function will submit the login form on the Neopets website with
        the user's username and password. It then returns the status of the
        login by checking for the user's username on the resulting page. This
        method must be called before doing any other account activities that
        normally require the user to be logged in.

        Returns:
            A boolean value indicating if the login was successful
        """
        # TNT has very tight anti-cheat controls so in this scenario it
        # is best to simulate a legitimate login by navigating to the
        # index page first
        pg = self.get_page(self._urls['index'])

        # Fill in the login form
        form = pg.form(action='/login.phtml')[0]
        form.update(username=self.username, password=self.password)

        # Submit the form
        pg = form.submit(self)

        # Return if it was successful
        return self.username in pg.content

    def get_page(self, url, post_data='', header_values=''):
        """A wrapper function that returns a page using the user's session

        This method should be used over initializing a new page object by
        supplying the user's session. It performs checks to inject the user's
        pin number at the appropriate time as well as checks for random events
        and acts on them accordingly.

        Args:
            | **url**: The url of the page to request
            | **post_data**: Optional dictionary containing post data to POST
            | **header_values**: Optional dictionary to override header values

        Returns:
            A :class:`.Page` object representng the requested page
        """
        # Inject a referer (Neopets looks for these often)
        if not header_values and self._last_page:
            header_values = {'Referer': self._last_page}
        elif "Referer" not in header_values and self._last_page:
            header_values['Referer'] = self._last_page

        pg = Page(url, self, post_data=post_data, header_values=header_values)

        # Check if this is an HTML page
        if type(pg.content) is bytes:
            return pg

        self._last_page = url

        # This image is shown if Neopets is offline
        if "http://images.neopets.com/homepage/indexbak_oops_en.png" in pg.content:
            raise NeopetsOffline

        # Call hooks
        for hook in self.hooks:
            h = hook()
            h.execute(self, pg)

        return pg

    def add_hook(self, hook):
        """Adds an instance of a :class:`Hook` based class to be executed after
        page calls
        """
        self.hooks.append(hook)

    def __repr__(self):
        return "User <" + self.username + ">"
