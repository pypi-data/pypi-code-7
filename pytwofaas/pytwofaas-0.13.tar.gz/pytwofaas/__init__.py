import requests

class PyTwoFaas():

  url = "http://127.0.0.1:5000"

  def __init__(self, companyToken):
    self.cToken = companyToken
    print self.cToken

  def sendAuth(self, clientId, factor, authType):
    if authType == 'email':
      payload = { 'userID' : clientId, 'compTK': self.cToken, 'userNum': factor }
    else:
      payload = { 'userID' : clientId, 'compTK': self.cToken, 'userEmail': factor }
    r = requests.post(self.url + "/init/" + authType, data=payload)
    print(r.text)

  def sendAuthSMS(self, clientId, phoneNum):
    sendAuth(self, clientId, phoneNum, "sms")

  def sendAuthCall(self, cliendId, phoneNum):
    sendAuth(self, clientId, phoneNum, "call")

  def sendAuthEmail(self, cliendId, email):
    sendAuth(self, clientId, phoneNum, "email")

  def sendUserInput(self, clientId, code):
    payload = {'userID' :clientId,'compTK':self.cToken,'twoAuth':code}
    r = requests.post(self.url + "/validate", data=payload)
    print(r.text)
