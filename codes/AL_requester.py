import json
import requests
from datetime import datetime, timedelta, timezone
from r2r_offer_utils.advanced_logger import logger


# class to obtain the authentication token
class AuthTokenObtainer:

    def __init__(self, key=None, name="authentication api"):
        self.token = key
        self.name = name
        self.expires = None

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
                return MyResponse(e, 521, error_source=self.name)
            if token_request.status_code == 200:
                token_json = token_request.json()
                try:
                    self.token = token_json['access_token']
                    self.expires = datetime.now() + timedelta(seconds=token_request.json()['expires_in'])
                except KeyError as e:
                    return MyResponse(f'Key {str(e)} not found in authentication response JSON',
                                      521, error_source=self.name)

            elif token_request.status_code == 401:
                return MyResponse('authentication error, headers:' + str(token_request.headers), 401,
                                  error_source=self.name)
            # if it's a different error
            else:
                return MyResponse(token_request.content.decode('UTF-8'), token_request.status_code,
                                  error_source=self.name)
            logger.info("Token successfully obtained")
        return self.token


class RequestObtainer:
    """
    class for obtaining the requests from preference api
    """

    def __init__(self, config, name = "", auth_cfg = None):
        """
        :param name: Name of the request obtainer
        :param auth_cfg: dictionary with authentication details
        """
        # creates authentication token object
        self.token_obtainer     = AuthTokenObtainer()
        self.auth_token         = None
        self.name               = name

        # extract authentication url and secret
        try:
 #           self.url_auth = auth_cfg["auth_url"]
            auth_secret   = auth_cfg['auth_secret']
            # self.url_auth = config.get('agreement_ledger_api', 'auth_url')
            # auth_secret = config.get('auth', 'basic_secret')
        except KeyError as ke:
            logger.error(f"Missing key {e} in authentication dictionary of request obtainer of {self.name}")
            return
        # obtains values from config for the authentication
        self.headers_auth = {
            'Authorization': f'Basic {auth_secret}',
            'accept': 'application/json'
        }

    def load_request(self, url, id, key_attr = "check"):
        """
        authenticates and obtains the request from the API
        returns functions directly to the API
        :param  url: url for the request
                id: id as a parameter of URL in the get request
        :return: dictionary containing preference and user profile data, where each contains:
                    - whole request object if 200 was returned or
                    - MyResponse class in case of error if other than 200 returned
        """
        # obtains the token from authentication api
        # if there is an error returns MyResponse object
        try:
            self.auth_token = self.token_obtainer.obtain_token(headers=self.headers_auth, url=self.url_auth)
        except requests.exceptions.ConnectionError as e:
            MyResponse(e, 521, error_source='authentication api').get_response()
            return None
        # if there was a request error pass the error
        if type(self.auth_token) is MyResponse:
            self.auth_token.get_response()
            return None

        headers_get = {'accept': 'application/json', 'Authorization': 'Bearer ' + self.auth_token}
        response = requests.get(url + id, headers=headers_get)

        # check if the response has a proper format
        if key_attr:
            return self.checkResponse(response, key_attr, name=url)

        return None

    def checkResponse(self, response, key, name=""):
        if response.status_code == 200:
            try:
                return int(self.checkKey(response.json(), key, ret_val=0))
            except ValueError:
                logger.error(f'Wrong type value of received from the {self.name}: {name}')
        else:
            try:
                logger.error(f'Error {response.status_code} at {self.name}, response from server: {response.json()}')
            except ValueError:
                logger.error(f'Error {response.status_code} received without a response in {self.name}')
            return 0

    def checkKey(self, json_dict, key, ret_val=None):
        if json_dict is None:
            return ret_val
        try:
            data = json_dict[key]
        except KeyError:
            data = ret_val
        return data


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
