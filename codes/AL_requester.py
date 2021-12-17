import json
import requests
from datetime import datetime, timedelta, timezone
from r2r_offer_utils.advanced_logger import logger


# class to obtain the authentication token
class AuthTokenObtainer:

    def __init__(self, key=None, expires=None):
        self.token = key
        self.expires = expires

    # Obtains the authentication key. If a key is requested and actual one has expired, obtains a new key.
    def obtain_token(self, headers, url):
        """
        obtains the key from the authentication api
        :param headers: dictionary with headers for the request
        :param url: url for the request
        :param playload: playload for the request
        :return: object of class MyResponse if something fails, else returns the authentication token
        """
        # if there is no token or it expires in 15 seconds, it obtains a new token
        if self.expires is None or self.expires <= datetime.now() + timedelta(seconds=15):
            logger.info("Obtaining new token")
            try:
                token_request = requests.post(url, headers=headers)
            except requests.exceptions.ConnectionError as e:
                return MyResponse(e, 521, error_source='authentication api')
            if token_request.status_code == 200:
                token_json = token_request.json()
                try:
                    self.token = token_json['accessToken']
                    self.expires = datetime.now() + timedelta(seconds=token_request.json()['expiresIn'])
                except KeyError as e:
                    return MyResponse(f'Key {str(e)} not found in authentication response JSON',
                                      521, error_source='authentication api')

            elif token_request.status_code == 401:
                return MyResponse('authentication error, headers:' + str(token_request.headers), 401,
                                  error_source='authentication api')
            # if it's a different error
            else:
                return MyResponse(token_request.content.decode('UTF-8'), token_request.status_code,
                                  error_source='authentication api')
            logger.info("Token successfully obtained")
        return self.token


class RequestObtainer:
    """
    class for obtaining the requests from preference api
    """

    def __init__(self, config):
        """
        :param config: configuration file of class ConfigParser
        """
        # creates authentication token object
        self.token_obtainer = AuthTokenObtainer()
        self.auth_token = None

        auth_secret = config.get('auth', 'basic_secret')
        # obtains values from config for the authentication
        self.headers_auth = {
            'Authorization': f'Basic {auth_secret}',
            'accept': 'application/json'
        }

        # extract urls
        self.url_auth = config.get('agreement_ledger_api', 'auth_url')
        self.url_disc20 = config.get('agreement_ledger_api', 'disc20_url')
        self.url_upgrSeat = config.get('agreement_ledger_api', 'upgrSeat_url')

    def load_request(self, traveller_id, travel_episode_id):
        """
        authenticates and obtains the request from the API
        returns functions directly to the API
        :param traveller_id: traveller id provided in the get request
        :return: dictionary containing preference and user profile data, where each contains:
                    - whole request object if 200 was returned or
                    - MyResponse class in case of error if other than 200 returned
        """
        # obtains the token from authentication api
        try:
            self.auth_token = self.token_obtainer.obtain_token(headers=self.headers_auth, url=self.url_auth)
        except requests.exceptions.ConnectionError as e:
            return MyResponse(e, 521, error_source='authentication api')
        # if there was a request error pass the error
        if type(self.auth_token) is MyResponse:
            return self.auth_token

        headers_get = {'accept': 'application/json', 'authorization': 'Bearer ' + self.auth_token}
        disc20 = self.execute_request(id=traveller_id, url=self.url_disc20, name="AL disc20", headers=headers_get)
        upgrSeat = self.execute_request(id=travel_episode_id, url=self.url_upgrSeat, name="AL upgrade seat",
                                        headers=headers_get)

        return {
            'disc20': disc20,
            'upgrSeat': upgrSeat,
        }

    def execute_request(self, id, url, name="", headers=""):
        url = url + id
        result_pref = requests.get(url, data=None, headers=headers)
        if result_pref.status_code == 200:
            return result_pref
        else:  # if was not a 200 returned
            MyResponse(result_pref.content.decode('UTF-8'), result_pref.status_code, id, error_source=name)


class MyResponse:
    """
    Class to creating, modifying and logging the response.
    When creating the response it automatically logs the error if it is not a 200 response
    if it is a dictionary and is user id provided it enriches the json with the user id
    """

    def __init__(self, rJSON, codeHTTP, user_id=None, error_source="unknown"):
        """
        :param rJSON: response JSON, or a string
        :param codeHTTP: HTTP request integer code
        :param user_id: user id
        :param error_source: string with the source of the error
        """
        self.codeHTTP = codeHTTP
        self.rJSON = rJSON
        self.error_source = error_source
        # logs the error if not 200 returned
        if self.codeHTTP != 200:
            logger.error(f'error: {self.rJSON}, source: {self.error_source}')
        # add user id if is missing in JSON and if is provided as an argument
        if isinstance(self.rJSON, dict):
            if "user_id" not in self.rJSON and user_id is not None:
                self.rJSON['user_id'] = user_id

    def get_response(self, user_id=None):
        """
        transforms error code to 403 if its different from 200
        adds the user_id json as response if provided, otherwise an empty string is returned
        if there is 200 code just returns tuple of rJSON and codeHTTP
        :return: response and code tuple
        """
        # if the error is different from 200
        if self.codeHTTP != 200:
            # set response to JSON with user_id if provided
            if user_id is not None:
                self.rJSON = {'user_id': user_id}
            else:
                self.rJSON = ''
            # set error to 403
            self.codeHTTP = 403

        return self.rJSON, self.codeHTTP
