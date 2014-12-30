class PyTwoFaas():

  import requests

  url = "http://127.0.0.1:5000"

  def __init__(self, companyToken):
    self.cToken = companyToken
    print self.cToken

  def init(self, clientId, phoneNum):
    print "It got here"
    payload = { 'userID' : clientId, 'compTK': self.cToken, 'userNum': phoneNum }
    print "Here"
    import pdb; pdb.set_trace
    r = requests.post(self.url + "/init", data=payload)
    print "There"
    print(r.text)

  def validate(self, clientId, code):
    payload = {'userID' :clientId,'compTK':self.cToken,'twoAuth':code}
    r = requests.post(self.url + "/validate", data=payload)
    print(r.text)