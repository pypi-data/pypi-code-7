from os.path import join
import subprocess


class Request():
    """Request payment"""
    amount = 0
    request_id = 0
    path_file = ""
    path_bin = ""
    response_return_url = ""
    autoresponse_return_url = ""

    def get_params(self):
        """get list of params"""
        # Affectation des parametres obligatoires
        parm1 = "merchant_id=082584341411111"
        parm2 = "merchant_country=fr"
        parm3 = "amount=" + str(self.amount) + "00"
        parm4 = "currency_code=978"

        # Initialisation du chemin du fichier pathfile
        parm5 = "pathfile=" + self.path_file

        # Initialisation du chemin de l'executable request
        path_bin = join(self.path_bin, "request_2.6.9_3.4.2")

        # Affectation des parametres optionel
        parm6 = "customer_id=" + str(self.request_id)
        parm7 = "normal_return_url=" + self.response_return_url
        parm8 = "cancel_return_url=" + self.response_return_url
        parm9 = "automatic_response_url=" + self.autoresponse_return_url

        return (path_bin, parm1, parm2, parm3, parm4, parm5, parm6, parm7, parm8, parm9)

    def call_request(self):
        """call request bin"""
        # Recuperation des parametres pour le binaire
        parm = self.get_params()

        # Appel du binaire request
        result = subprocess.Popen([p for p in parm], stdout=subprocess.PIPE).communicate()

        # sortie de la fonction : $result=!code!error!buffer!
        #      - code=0    : la fonction genere une page html contenue dans la variable buffer
        #      - code=-1   : La fonction retourne un message d'erreur dans la variable error
        #
        # On separe les differents champs et on les met dans une variable tableau
        tab = result[0].split('!')

        # Recuperation des parametres
        code_dict = {
            "code": tab[1],
            "error": tab[2],
            "message": tab[3],
            "exec_path": parm[0],
        }

        return code_dict
