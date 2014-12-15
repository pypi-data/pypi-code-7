class WindowsPassword:
    '''
    Username and password for a Windows target.
    '''
    category = "Host"
    name = "Windows"

    def __init__(self, username, password, domain="", auth_method="Password"):
        self.username = username
        self.password = password
        self.domain = domain
        self.auth_method = auth_method

class Ssh:
    '''
    Does not provide complete credential information on its own. Create one of
    its subclasses instead. The privilege escalation functions can be used on
    any subclass.
    '''
    category = "Host"
    name = "SSH"

    def __init__(self):
        self.elevate_privileges_with = "Nothing"

    def cisco_enable(self, enable_password):
        self.elevate_privileges_with = "Cisco 'enable'"
        self.escalation_password = enable_password
        return self

    def sudo(self, password, username="root"):
        self.elevate_privileges_with = "sudo"
        self.escalation_account = username
        self.escalation_password = password
        return self

class SshPassword(Ssh):
    '''
    Username and password for an SSH login.
    '''
    def __init__(self, username, password):
        super(SshPassword, self).__init__()
        self.auth_method = "password"
        self.username = username
        self.password = password

class SshPublicKey(Ssh):
    '''
    SSH certificate login. The private key must have been uploaded already.
    '''
    def __init__(self, username, private_key_filename, private_key_passphrase):
        super(SshPublicKey, self).__init__()
        self.auth_method = "public key"
        self.username = username
        self.private_key = private_key_filename
        self.private_key_passphrase = private_key_passphrase

class SshUserCert(SshPublicKey):
    '''
    SSH client certificate login. The private key and user cert must have been
    uploaded already.
    '''
    def __init__(self, username, user_cert_filename, private_key_filename,
                 private_key_passphrase):
        self.user_cert = user_cert_filename
        super(SshUserCert, self) \
            .__init__(username=username,
                      private_key_filename=private_key_filename,
                      private_key_passphrase=private_key_passphrase)

class Salesforce:
    '''
    Username and password for Salesforce.com.
    '''
    category = "Cloud Services"
    name = "Salesforce.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

class PaloAltoPANOS:
    '''
    Username and password for a Palo Alto PAN-OS device through the web API.
    '''
    category = "Miscellaneous"
    name = "Palo Alto Networks PAN-OS"

    def __init__(self, username, password, port="443", verify_ssl=True):
        self.username = username
        self.password = password
        self.port = port
        self.verify_ssl = verify_ssl
