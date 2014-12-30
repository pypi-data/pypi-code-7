import asyncio
import aiohttp
import ssl
import json

class BetfairAuth:
  URL = 'https://identitysso.betfair.com/api/certlogin'

  def __init__(self, appKey, cert, key):
    self.appKey = appKey
    self.sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    self.sslContext.load_cert_chain(cert, key)
    self.sslConnector = aiohttp.TCPConnector(ssl_context=self.sslContext)
    
  @asyncio.coroutine
  def bot_login(self, login, password):
    headers = {
        'X-Application': self.appKey, 
         'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = 'username={0}&password={1}'.format(login, password)
    response = yield from aiohttp.request(
        'POST',  BetfairAuth.URL,
        connector=self.sslConnector, 
        headers=headers, data=payload)
    response = yield from response.read()
    return json.loads(response.decode("utf-8"))
