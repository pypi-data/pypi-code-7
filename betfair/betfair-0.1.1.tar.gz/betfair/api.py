from . import auth
import asyncio

__all__ = ['BetfairAPI']

class BetfairAPI:
  def __init__(self, appKey, cert, key):
     self.auth = auth.BetfairAuth(appKey, cert, key)
     
  @asyncio.coroutine
  def bot_login(self, login, password):
      return self.auth.bot_login(login, password)
