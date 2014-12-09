import requests


class PipedriveAPIClient:

    pipedrive_base_url = "https://api.pipedrive.com/v1"

    def __init__(self, api_token=None, user_email=None, user_password=None):
        if api_token:
            if isinstance(api_token, str):
                self.api_token = api_token
            else:
                raise ValueError("Pipedrive API key must be provided as a string.")
        elif user_email and user_password:
            if isinstance(user_email, str) and isinstance(user_password, str):
                self.api_token = self.request_api_key(user_email, user_password)
            else:
                raise ValueError("Pipedrive credentials must be provided as strings.")

    def request_api_key(self, user_email, user_password):
        credentials = {'email': user_email, 'password': user_password}
        authorization_url = self.pipedrive_base_url + "/authorizations"

        authorization_response = requests.post(authorization_url, data=credentials)

        if authorization_response.status_code == 200:
            authorization_json_body = authorization_response.json()
            if 'success' in authorization_json_body:
                data = authorization_json_body['data'][0]
                if 'api_token' in data:
                    return data['api_token']
