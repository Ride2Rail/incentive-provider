import json
import logging
import threading
import time

import requests
from datetime import datetime, timedelta, timezone

logger = logging.getLogger('incentive_provider_api.request_helper')


# class to obtain the authentication token
class AuthTokenObtainer:
    """
    Handles the JWT token authentication
    """
    def __init__(self, key=None, name="authentication api", lock_timeout=0.5):
        self.token = key
        self.name = name
        self.expires = None
        self.lock = threading.Semaphore()
        self.lock_timeout = lock_timeout
        self.lock_counter = 0

    # Obtains the authentication key. If a key is requested and actual one has expired, obtains a new key.
    def obtain_token_old(self, headers, url):
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

    # Obtains the authentication key. If a key is requested and actual one has expired, obtains a new key.
    def obtain_token(self, headers, url):
        """
        obtains the key from the authentication api
        :param headers: dictionary with headers for the request
        :param url: url for the request
        :param playload: playload for the request
        :return: object of class MyResponse if something fails, else returns the authentication token
        """
        token = self.token
        # if there is no token or it expires in 15 seconds, it obtains a new token
        if self.expires is None or self.expires <= datetime.now() + timedelta(seconds=15):
            # let the others wait for lock_timeout seconds
            self.lock.acquire(timeout=self.lock_timeout)
            # check if it was meanwhile obtained by other request
            if self.expires is None or self.expires <= datetime.now() + timedelta(seconds=15):
                token = self.auth_token_request(headers, url)
            else:
                # the token was obtained by a previous request
                token = self.token
                logger.info("Token obtained by the previous parallel request")
            self.lock.release()
        return token

    def auth_token_request(self, headers, url):
        logger.info("Obtaining new token")
        try:
            token_request = requests.post(url, headers=headers)
        except requests.exceptions.ConnectionError as e:
            return MyResponse(e, 521, error_source='authentication api')
        except Exception as ex:
            return MyResponse(ex, 500, error_source='authentication api')
        if token_request.status_code == 200:
            try:
                token_json = token_request.json()
                self.token = token_json['access_token']
                self.expires = datetime.now() + timedelta(seconds=token_json['expires_in'])
                logger.info(f"Token successfully obtained, expiration set to: {self.expires}")
                return self.token
            except Exception as e:
                return MyResponse(f'Inconsistency in the JSON received from the authentication: {e}',
                                  521, error_source='authentication api')
        elif token_request.status_code == 401:
            return MyResponse('authentication error, headers:' + str(token_request.headers), 401,
                              error_source='authentication api')
        # if it's a different error
        else:
            return MyResponse(token_request.content.decode('UTF-8'), token_request.status_code,
                              error_source='authentication api')


class RequestObtainer:
    """
    class to execute a request to an external end-point
    """

    def __init__(self, token_obtainer, name="", auth_config=None):
        """
        :param name: Name of the request obtainer
        :param auth_config: dictionary with authentication details
        """
        # creates authentication token object
        self.token_obtainer = token_obtainer
        self.auth_token = None

        self.name = name

        # extract authentication url and secret
        try:
            self.url_auth = auth_config["auth_url"]
            auth_secret = auth_config['auth_secret']
        except KeyError as ke:
            logger.error(f"Missing key {ke} in authentication dictionary of request obtainer of {self.name}")
            return
        # create authentication header
        self.headers_auth = {
            'Authorization': f'Basic {auth_secret}',
            'accept': 'application/json'
        }

    def load_request(self, url, id, key_attr="check"):
        """
        authenticates and obtains the request from the API
        returns functions directly to the API
        :param key_attr:
        :param url: url for the request
        :param id: id as a parameter of URL in the get request
        :param key_attr: attribute to check in the received JSON
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
        return self.checkResponse(response, key_attr, name=url)

    def checkResponse(self, response, key, name=""):
        if response.status_code == 200:
            try:
                return self.checkKey(response.json(), key, ret_val=None)
            except ValueError:
                logger.error(f'Wrong type value of received from the {self.name}: {name}')
        else:
            try:
                logger.error(f'Error {response.status_code} at {self.name}, response from server: {response.json()}')
            except ValueError:
                logger.error(f'Error {response.status_code} received without a response in {self.name}')
            return None

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
