class Windows:
    category = "Host"
    name = "Windows"

    def __init__(self, username, password, domain="", auth_method="Password"):
        self.username = username
        self.password = password
        self.domain = domain
        self.auth_method = auth_method

class SSH:
    category = "Host"
    name = "SSH"

    def __init__(self, username, password, auth_method="password", elevate_privileges_with="Nothing"):
        self.username = username
        self.password = password
        self.auth_method = auth_method
        self.elevate_privileges_with = elevate_privileges_with
