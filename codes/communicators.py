import itertools
from abc import ABC, abstractmethod
import redis
import r2r_offer_utils.cache_operations
import logging

from codes.AL_requester import *

logger = logging.getLogger('incentive_provider_api.communicators')


########################################################################################################################
########################################################################################################################
########################################################################################################################
class Communicator(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def accessRuleData(self, dict_data):
        pass


########################################################################################################################
########################################################################################################################
########################################################################################################################
class AgreementLedgerCommunicator(Communicator):
    def __init__(self, config, data=None):
        super().__init__(data)
        # config = data["config"]
        # objects required for requests
        if config is not None:
            self.url_dict = {
                "disc20_url": config.get('agreement_ledger_api', 'disc20_url'),
                "upgrSeat_url": config.get('agreement_ledger_api', 'upgrSeat_url')
            }
            auth_config = {
                'auth_url': config.get('agreement_ledger_api', 'auth_url'),
                'auth_secret': config.get('auth', 'basic_secret')
            }
            self.requestObtainer = RequestObtainer("AgreementLedgerObtainer", auth_config)
        else:
            logger.error('Could not read config file in communicators.py')

    def accessRuleData(self, dict_data):
        # obtain the data from Agreement ledger using request obtainer
        url = self.url_dict[dict_data['url']]
        req_answer = self.requestObtainer.load_request(url, dict_data['id'])
        if req_answer is None:
            logger.error("Value: None received from Agreement Ledger")
        return req_answer
########################################################################################################################
########################################################################################################################
########################################################################################################################
"""
class ensuring communication with the offer Cache
"""


class OfferCacheCommunicator(Communicator):
    """
        Establish connection with the offer cache.
    """

    def __init__(self, config, data=None):
        # get the ports
        super().__init__(data)
        if config is not None:
            # read connection parameters from the config file
            CACHE_HOST = config.get('cache', 'host')
            CACHE_PORT = config.get('cache', 'port')
            logger.info(f"Connecting to offer cache: CACHE_HOST = {CACHE_HOST}, CACHE_PORT = {CACHE_PORT}")
            try:
                # establish connection to the offer cache
                self.cache = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)
            except redis.exceptions.ConnectionError as exc:
                logger.error("Connection to the offer cache has not been established.")
        else:
            logger.error('Could not read config file in communicators.py')

    """
     Request data from the offer cache.
    """
    def read_data_from_offer_cache(self, request_id, list_offer_level_keys, list_tripleg_level_keys):
        try:
            # read data from the offer cache
            logger.info(f"Read data from the offer cache: request_id = {request_id},"
                        f"list_offer_level_keys = {list_offer_level_keys}, "
                        f"list_tripleg_level_keys = {list_tripleg_level_keys}")
            output_offer_level, output_tripleg_level = r2r_offer_utils.cache_operations.read_data_from_cache_wrapper(
                self.cache,
                request_id,
                list_offer_level_keys,
                list_tripleg_level_keys)
        except redis.exceptions.ConnectionError as exc:
            logger.error(f"Reading from the offer cache failed in communicators.py: {str(exc)}")
            return None
        return {'output_offer_level': output_offer_level, 'output_tripleg_level': output_tripleg_level}

    def accessRuleData(self, dict_data):
        request_id = dict_data['request_id']
        # if its a call for more complicated data
        if 'list_offer_level_keys' in dict_data:
            list_offer_level_keys = dict_data['list_offer_level_keys']
            list_tripleg_level_keys = dict_data['list_tripleg_level_keys']
            return self.read_data_from_offer_cache(request_id, list_offer_level_keys, list_tripleg_level_keys)
        # if its a simple call
        else:
            try:
                # pipe = self.cache.pipeline()
                # pipe.lrange(f"{request_id}:offers", 0, -1)
                # pipe.get(f"{request_id}:{dict_data['offer_level_id']}")
                # pipe_list = pipe.execute()
                # pipe_res_dict = {
                #     "offer_ids": pipe_list[0],
                #     "traveller_id": pipe_list[1]
                # }
                # return pipe_res_dict
                return self.redis_request_level_item(request_id, dict_data["offer_level_keys"],
                                                     dict_data["offer_level_types"])
            except KeyError:
                return None
            except redis.exceptions.ConnectionError as exc:
                logger.error(f"Reading from cache by a feature collector failed: {exc}")

    def redis_request_level_item(self, request_id, request_level_keys, request_level_types):
        """
        Obtains the keys provided in request_level_keys from OfferCache, with types specified in request level types.
        In case a wrong type of any key is provided, None is returned.
        :param request_id: id of the request
        :param request_level_keys: keys on the request level
        :param request_level_types: types of the keys on the request level
        :return: dictionary with a dictionary for each key
        """
        # dictionary of possible values
        transl_dict = {"l": "list", "v": "value"}
        pipe = self.cache.pipeline()
        index_list = [] # list of indexed which were not skipped
        res_dict = {} # dictionary for results
        # iterate over the keys
        for key, data_type, i in itertools.zip_longest(request_level_keys, request_level_types, range(0, len(request_level_keys))):
            # if the key type is a valid type add it to the pipe, otherwise set the corresponding key as none
            if data_type in transl_dict.keys():
                self.redis_universal_get(pipe, request_id, key, data_type)
                index_list.append(i)
            else:
                res_dict[key] = None
        # execute the pipe
        try:
            pipe_res_list = pipe.execute()
        # Raised if incorrect key types were provided
        except redis.exceptions.ResponseError as re:
            logger.error(f"Error when reading from cache, probably wrong data type: \n{re}")
            return {}
        # extract the data from the pipe to the dictionary, skips attributes with unexpected data type
        for pipe_req, i in itertools.zip_longest(pipe_res_list, index_list):
            res_dict[request_level_keys[i]] = pipe_req

        return res_dict

    def redis_universal_get(self, pipe, request_id, key, type):
        if type == 'l':
            pipe.lrange(f"{request_id}:{key}", 0, -1)
        if type == 'v':
            pipe.get(f"{request_id}:{key}")
    """
    Code in preparation below
    """
    def iterate_list(self, request_id, keys, types):
        pipe = self.cache.pipeline()
        res_dict = {}
        for key, data_type in itertools.zip_longest(keys, types):
            # if the key type is a valid type add it to the pipe, otherwise set the corresponding key as none
            self.redis_universal_get(pipe, request_id, key, data_type)
        try:
            pipe_res_list = pipe.execute()
        # Raised if incorrect key types were provided
        except redis.exceptions.ResponseError as re:
            logger.error(f"Error when reading from cache, probably wrong data type: \n{re}")
            return None

        for pipe_req, key in  itertools.zip_longest(pipe_res_list, keys):
            res_dict[key] = pipe_req
        return res_dict

    def iterator_cache(self, request_id, request_level_keys, request_level_types,
                             offer_level_keys, offer_level_types,
                             item_level_iterator, item_level_keys, item_level_types):
        request_res = self.iterate_list(self, request_id, request_level_keys, request_level_types)
        for offer in request_res["offers"]:
            offer_res = self.iterate_list(self, request_id + ":" + offer, offer_level_keys, offer_level_types)
            for item in offer_res[item_level_iterator]:
                item_res = self.iterate_list(self, request_id + ":" + offer + ":" + item,
                                             item_level_keys, item_level_types)